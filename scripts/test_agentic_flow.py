#!/usr/bin/env python3
"""
Test script for Agentic Flow Controller.

Tests basic ReAct pattern implementation and action execution.
"""

import asyncio
import json
import logging
from typing import Dict, Any

# Add parent directory to path
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.services.agentic import AgenticFlowController, MnemosyneAction
from backend.app.services.agentic.actions import ActionPayload, ActionPlan
from backend.app.services.llm.service import LLMService
from backend.app.services.receipt_service import ReceiptService
from backend.app.core.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


class TestAgenticFlow:
    """Test harness for agentic flow."""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.receipt_service = None  # Mock for testing
        self.flow_controller = AgenticFlowController(
            llm_service=self.llm_service,
            receipt_service=self.receipt_service
        )
    
    async def test_basic_flow(self):
        """Test basic agentic flow with a simple query."""
        print("\n" + "="*50)
        print("TEST: Basic Agentic Flow")
        print("="*50)
        
        query = "I'm feeling overwhelmed with all my tasks today"
        context = {
            "user_id": "test_user",
            "persona_mode": "confidant",
            "memories": [],
            "tasks": [
                {"title": "Project deadline", "status": "pending"},
                {"title": "Team meeting", "status": "pending"},
                {"title": "Code review", "status": "in_progress"}
            ]
        }
        
        print(f"\nQuery: {query}")
        print(f"Context: {json.dumps(context, indent=2)}")
        
        try:
            result = await self.flow_controller.execute_flow(
                query=query,
                context=context,
                stream=True
            )
            
            print("\nFlow Result:")
            print(f"- Iterations: {result.get('iterations')}")
            print(f"- Duration: {result.get('duration_ms')}ms")
            print(f"- Reasoning: {result.get('reasoning')}")
            print(f"- Response: {json.dumps(result.get('response'), indent=2)}")
            print(f"- Suggestions: {json.dumps(result.get('suggestions'), indent=2)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            return False
    
    async def test_action_planning(self):
        """Test action planning capabilities."""
        print("\n" + "="*50)
        print("TEST: Action Planning")
        print("="*50)
        
        reasoning = """
        The user is feeling overwhelmed with tasks. I should:
        1. Switch to Guardian mode to provide support
        2. Analyze their task list for prioritization
        3. Suggest breaking down complex tasks
        4. Create a memory of this emotional state for future reference
        """
        
        context = {
            "query": "Help me prioritize",
            "tasks_count": 5
        }
        
        print(f"\nReasoning: {reasoning}")
        
        try:
            actions = await self.flow_controller.plan_actions(reasoning, context)
            
            print("\nPlanned Actions:")
            for i, action in enumerate(actions, 1):
                print(f"{i}. {action.action}: {action.reasoning}")
                print(f"   Confidence: {action.confidence}")
                print(f"   Parameters: {action.parameters}")
            
            return len(actions) > 0
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            return False
    
    async def test_parallel_execution(self):
        """Test parallel action execution."""
        print("\n" + "="*50)
        print("TEST: Parallel Execution")
        print("="*50)
        
        # Create multiple actions to execute in parallel
        actions = [
            ActionPayload(
                action=MnemosyneAction.SEARCH_MEMORIES,
                parameters={"query": "overwhelmed", "limit": 3},
                reasoning="Find similar past experiences",
                confidence=0.9
            ),
            ActionPayload(
                action=MnemosyneAction.ANALYZE_PATTERNS,
                parameters={"data_type": "tasks", "timeframe": "week"},
                reasoning="Identify task patterns",
                confidence=0.7
            ),
            ActionPayload(
                action=MnemosyneAction.SELECT_PERSONA,
                parameters={},
                reasoning="Choose appropriate support mode",
                confidence=0.95
            )
        ]
        
        context = {"user_id": "test_user"}
        
        print(f"\nExecuting {len(actions)} actions in parallel...")
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Execute all actions in parallel
            tasks = [
                self.flow_controller.execute_action(action, context)
                for action in actions
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            duration = (asyncio.get_event_loop().time() - start_time) * 1000
            
            print(f"\nExecution completed in {duration:.2f}ms")
            print("\nResults:")
            for i, result in enumerate(results, 1):
                if hasattr(result, 'action'):
                    print(f"{i}. {result.action}: {'✓' if result.success else '✗'}")
                    if result.data:
                        print(f"   Data: {json.dumps(result.data, indent=6)[:200]}...")
                    if result.error:
                        print(f"   Error: {result.error}")
                else:
                    print(f"{i}. Exception: {result}")
            
            # Check that execution was actually parallel (should be much faster than sequential)
            expected_sequential_time = len(actions) * 100  # Assume 100ms per action minimum
            is_parallel = duration < expected_sequential_time
            
            print(f"\nParallel execution: {'✓' if is_parallel else '✗'}")
            
            return is_parallel
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            return False
    
    async def test_needs_more_info(self):
        """Test decision on whether more information is needed."""
        print("\n" + "="*50)
        print("TEST: Needs More Info Decision")
        print("="*50)
        
        # Test with incomplete results
        from backend.app.services.agentic.actions import ActionResult
        
        incomplete_results = [
            ActionResult(
                action=MnemosyneAction.SEARCH_MEMORIES,
                success=True,
                data={"memories_found": 0}
            ),
            ActionResult(
                action=MnemosyneAction.NEED_MORE,
                success=True,
                data={"needed": "User preferences unknown"}
            )
        ]
        
        context = {"original_query": "What should I focus on?"}
        
        print("\nIncomplete results scenario:")
        needs_more = await self.flow_controller.needs_more_info(
            incomplete_results, 
            context
        )
        print(f"Needs more info: {needs_more}")
        
        # Test with complete results
        complete_results = [
            ActionResult(
                action=MnemosyneAction.SEARCH_MEMORIES,
                success=True,
                data={"memories_found": 5, "memories": ["mem1", "mem2"]}
            ),
            ActionResult(
                action=MnemosyneAction.DONE,
                success=True,
                data={"message": "Analysis complete"}
            )
        ]
        
        print("\nComplete results scenario:")
        needs_more = await self.flow_controller.needs_more_info(
            complete_results,
            context
        )
        print(f"Needs more info: {needs_more}")
        
        return True
    
    async def run_all_tests(self):
        """Run all tests."""
        print("\n" + "="*50)
        print("AGENTIC FLOW TEST SUITE")
        print("="*50)
        
        tests = [
            ("Basic Flow", self.test_basic_flow),
            ("Action Planning", self.test_action_planning),
            ("Parallel Execution", self.test_parallel_execution),
            ("Needs More Info", self.test_needs_more_info)
        ]
        
        results = {}
        for test_name, test_func in tests:
            try:
                result = await test_func()
                results[test_name] = result
            except Exception as e:
                logger.error(f"Test {test_name} failed with exception: {e}")
                results[test_name] = False
        
        print("\n" + "="*50)
        print("TEST RESULTS SUMMARY")
        print("="*50)
        
        for test_name, passed in results.items():
            status = "✓ PASSED" if passed else "✗ FAILED"
            print(f"{test_name}: {status}")
        
        total = len(results)
        passed = sum(1 for p in results.values() if p)
        print(f"\nTotal: {passed}/{total} tests passed")
        
        return all(results.values())


async def main():
    """Main test runner."""
    tester = TestAgenticFlow()
    success = await tester.run_all_tests()
    
    if success:
        print("\n✅ All agentic flow tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed. Check logs for details.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())