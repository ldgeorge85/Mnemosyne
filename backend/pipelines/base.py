"""
Base pipeline classes for Mnemosyne Protocol
Async pipeline architecture with composable stages
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic, Callable, Union
from datetime import datetime
from enum import Enum
import traceback

from pydantic import BaseModel, Field
from ..core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

T = TypeVar('T')
R = TypeVar('R')


class PipelineStatus(str, Enum):
    """Pipeline execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PARTIAL = "partial"  # Some stages failed but pipeline continued


class StageResult(BaseModel):
    """Result from a pipeline stage"""
    stage_name: str
    status: PipelineStatus
    data: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PipelineResult(BaseModel):
    """Result from entire pipeline execution"""
    pipeline_name: str
    status: PipelineStatus
    stages: List[StageResult] = Field(default_factory=list)
    data: Optional[Any] = None
    error: Optional[str] = None
    total_duration_ms: Optional[int] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PipelineStage(ABC, Generic[T, R]):
    """Base class for pipeline stages"""
    
    def __init__(self, name: str, required: bool = True):
        self.name = name
        self.required = required
        self._logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    async def process(self, data: T, context: Dict[str, Any]) -> R:
        """Process data through this stage"""
        pass
    
    async def validate(self, data: T) -> bool:
        """Validate input data for this stage"""
        return True
    
    async def on_error(self, error: Exception, data: T, context: Dict[str, Any]) -> Optional[R]:
        """Handle errors - return None to propagate, or return data to continue"""
        if self.required:
            return None  # Propagate error for required stages
        
        self._logger.warning(f"Non-required stage {self.name} failed: {error}")
        return data  # Continue with original data for optional stages
    
    async def execute(self, data: T, context: Dict[str, Any]) -> StageResult:
        """Execute stage with error handling and timing"""
        start_time = datetime.utcnow()
        
        try:
            # Validate input
            if not await self.validate(data):
                raise ValueError(f"Validation failed for stage {self.name}")
            
            # Process data
            result = await self.process(data, context)
            
            # Calculate duration
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return StageResult(
                stage_name=self.name,
                status=PipelineStatus.COMPLETED,
                data=result,
                duration_ms=duration_ms
            )
            
        except Exception as e:
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            self._logger.error(f"Stage {self.name} failed: {e}\n{traceback.format_exc()}")
            
            # Try error recovery
            recovery_result = await self.on_error(e, data, context)
            
            if recovery_result is not None:
                return StageResult(
                    stage_name=self.name,
                    status=PipelineStatus.PARTIAL,
                    data=recovery_result,
                    error=str(e),
                    duration_ms=duration_ms
                )
            
            return StageResult(
                stage_name=self.name,
                status=PipelineStatus.FAILED,
                error=str(e),
                duration_ms=duration_ms
            )


class Pipeline(ABC, Generic[T, R]):
    """Base pipeline class with composable stages"""
    
    def __init__(
        self,
        name: str,
        stages: Optional[List[PipelineStage]] = None,
        parallel: bool = False,
        continue_on_error: bool = False
    ):
        self.name = name
        self.stages = stages or []
        self.parallel = parallel
        self.continue_on_error = continue_on_error
        self._logger = logging.getLogger(f"{__name__}.{name}")
        self._context: Dict[str, Any] = {}
    
    def add_stage(self, stage: PipelineStage) -> "Pipeline":
        """Add a stage to the pipeline"""
        self.stages.append(stage)
        return self
    
    def remove_stage(self, stage_name: str) -> "Pipeline":
        """Remove a stage by name"""
        self.stages = [s for s in self.stages if s.name != stage_name]
        return self
    
    async def before_pipeline(self, data: T) -> T:
        """Hook called before pipeline execution"""
        return data
    
    async def after_pipeline(self, data: R, result: PipelineResult) -> R:
        """Hook called after pipeline execution"""
        return data
    
    async def execute_parallel(self, data: T) -> PipelineResult:
        """Execute stages in parallel"""
        tasks = []
        for stage in self.stages:
            task = asyncio.create_task(stage.execute(data, self._context))
            tasks.append(task)
        
        stage_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        final_data = data
        all_completed = True
        errors = []
        
        for i, result in enumerate(stage_results):
            if isinstance(result, Exception):
                stage_result = StageResult(
                    stage_name=self.stages[i].name,
                    status=PipelineStatus.FAILED,
                    error=str(result)
                )
                errors.append(str(result))
                if self.stages[i].required:
                    all_completed = False
            else:
                stage_result = result
                if stage_result.status == PipelineStatus.FAILED and self.stages[i].required:
                    all_completed = False
                    errors.append(stage_result.error)
            
            # Store in results
            if isinstance(stage_result, StageResult):
                self._context[f"stage_{stage_result.stage_name}"] = stage_result
        
        return PipelineResult(
            pipeline_name=self.name,
            status=PipelineStatus.COMPLETED if all_completed else PipelineStatus.PARTIAL,
            stages=[r for r in stage_results if isinstance(r, StageResult)],
            data=final_data,
            error="; ".join(errors) if errors else None
        )
    
    async def execute_sequential(self, data: T) -> PipelineResult:
        """Execute stages sequentially"""
        stage_results = []
        current_data = data
        
        for stage in self.stages:
            result = await stage.execute(current_data, self._context)
            stage_results.append(result)
            
            # Store stage result in context
            self._context[f"stage_{stage.name}"] = result
            
            if result.status == PipelineStatus.COMPLETED or result.status == PipelineStatus.PARTIAL:
                current_data = result.data if result.data is not None else current_data
            elif result.status == PipelineStatus.FAILED:
                if stage.required and not self.continue_on_error:
                    return PipelineResult(
                        pipeline_name=self.name,
                        status=PipelineStatus.FAILED,
                        stages=stage_results,
                        error=result.error
                    )
        
        # Determine overall status
        failed_stages = [s for s in stage_results if s.status == PipelineStatus.FAILED]
        if failed_stages:
            required_failed = any(
                s.status == PipelineStatus.FAILED 
                for s, stage in zip(stage_results, self.stages) 
                if stage.required
            )
            status = PipelineStatus.FAILED if required_failed else PipelineStatus.PARTIAL
        else:
            status = PipelineStatus.COMPLETED
        
        return PipelineResult(
            pipeline_name=self.name,
            status=status,
            stages=stage_results,
            data=current_data
        )
    
    async def execute(self, data: T) -> PipelineResult:
        """Execute the pipeline"""
        start_time = datetime.utcnow()
        
        try:
            # Pre-processing hook
            data = await self.before_pipeline(data)
            
            # Execute stages
            if self.parallel:
                result = await self.execute_parallel(data)
            else:
                result = await self.execute_sequential(data)
            
            # Post-processing hook
            if result.data is not None:
                result.data = await self.after_pipeline(result.data, result)
            
            # Set completion time and duration
            result.completed_at = datetime.utcnow()
            result.total_duration_ms = int(
                (result.completed_at - start_time).total_seconds() * 1000
            )
            
            self._logger.info(
                f"Pipeline {self.name} completed with status {result.status} "
                f"in {result.total_duration_ms}ms"
            )
            
            return result
            
        except Exception as e:
            self._logger.error(f"Pipeline {self.name} failed: {e}\n{traceback.format_exc()}")
            
            return PipelineResult(
                pipeline_name=self.name,
                status=PipelineStatus.FAILED,
                error=str(e),
                completed_at=datetime.utcnow(),
                total_duration_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000)
            )
    
    async def execute_batch(self, items: List[T], max_concurrent: int = 10) -> List[PipelineResult]:
        """Execute pipeline on multiple items with concurrency control"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_item(item: T) -> PipelineResult:
            async with semaphore:
                return await self.execute(item)
        
        tasks = [process_item(item) for item in items]
        return await asyncio.gather(*tasks)


class CompositePipeline(Pipeline[T, R]):
    """Pipeline composed of other pipelines"""
    
    def __init__(
        self,
        name: str,
        pipelines: List[Pipeline],
        parallel: bool = False
    ):
        super().__init__(name, parallel=parallel)
        self.pipelines = pipelines
    
    async def execute(self, data: T) -> PipelineResult:
        """Execute composed pipelines"""
        if self.parallel:
            tasks = [p.execute(data) for p in self.pipelines]
            results = await asyncio.gather(*tasks)
        else:
            results = []
            current_data = data
            for pipeline in self.pipelines:
                result = await pipeline.execute(current_data)
                results.append(result)
                if result.data is not None:
                    current_data = result.data
        
        # Aggregate results
        all_stages = []
        for result in results:
            all_stages.extend(result.stages)
        
        # Determine overall status
        if any(r.status == PipelineStatus.FAILED for r in results):
            status = PipelineStatus.FAILED
        elif any(r.status == PipelineStatus.PARTIAL for r in results):
            status = PipelineStatus.PARTIAL
        else:
            status = PipelineStatus.COMPLETED
        
        return PipelineResult(
            pipeline_name=self.name,
            status=status,
            stages=all_stages,
            data=current_data if not self.parallel else data,
            metadata={"sub_pipelines": [r.pipeline_name for r in results]}
        )


class ConditionalStage(PipelineStage[T, T]):
    """Stage that conditionally executes based on a predicate"""
    
    def __init__(
        self,
        name: str,
        condition: Callable[[T, Dict[str, Any]], bool],
        true_stage: Optional[PipelineStage] = None,
        false_stage: Optional[PipelineStage] = None,
        required: bool = True
    ):
        super().__init__(name, required)
        self.condition = condition
        self.true_stage = true_stage
        self.false_stage = false_stage
    
    async def process(self, data: T, context: Dict[str, Any]) -> T:
        """Process based on condition"""
        if await asyncio.coroutine(self.condition)(data, context) if asyncio.iscoroutinefunction(self.condition) else self.condition(data, context):
            if self.true_stage:
                result = await self.true_stage.execute(data, context)
                return result.data if result.data is not None else data
        else:
            if self.false_stage:
                result = await self.false_stage.execute(data, context)
                return result.data if result.data is not None else data
        
        return data


class TransformStage(PipelineStage[T, R]):
    """Generic transformation stage"""
    
    def __init__(
        self,
        name: str,
        transform_func: Callable[[T], Union[R, asyncio.Future[R]]],
        required: bool = True
    ):
        super().__init__(name, required)
        self.transform_func = transform_func
    
    async def process(self, data: T, context: Dict[str, Any]) -> R:
        """Apply transformation"""
        if asyncio.iscoroutinefunction(self.transform_func):
            return await self.transform_func(data)
        else:
            return self.transform_func(data)


class FilterStage(PipelineStage[List[T], List[T]]):
    """Stage that filters a list of items"""
    
    def __init__(
        self,
        name: str,
        filter_func: Callable[[T], bool],
        required: bool = False
    ):
        super().__init__(name, required)
        self.filter_func = filter_func
    
    async def process(self, data: List[T], context: Dict[str, Any]) -> List[T]:
        """Filter items"""
        if asyncio.iscoroutinefunction(self.filter_func):
            results = await asyncio.gather(*[self.filter_func(item) for item in data])
            return [item for item, keep in zip(data, results) if keep]
        else:
            return [item for item in data if self.filter_func(item)]


class BatchStage(PipelineStage[List[T], List[R]]):
    """Stage that processes items in batches"""
    
    def __init__(
        self,
        name: str,
        batch_size: int,
        process_batch: Callable[[List[T]], List[R]],
        required: bool = True
    ):
        super().__init__(name, required)
        self.batch_size = batch_size
        self.process_batch = process_batch
    
    async def process(self, data: List[T], context: Dict[str, Any]) -> List[R]:
        """Process in batches"""
        results = []
        
        for i in range(0, len(data), self.batch_size):
            batch = data[i:i + self.batch_size]
            
            if asyncio.iscoroutinefunction(self.process_batch):
                batch_results = await self.process_batch(batch)
            else:
                batch_results = self.process_batch(batch)
            
            results.extend(batch_results)
        
        return results


# Export classes
__all__ = [
    'PipelineStatus',
    'StageResult',
    'PipelineResult',
    'PipelineStage',
    'Pipeline',
    'CompositePipeline',
    'ConditionalStage',
    'TransformStage',
    'FilterStage',
    'BatchStage',
]