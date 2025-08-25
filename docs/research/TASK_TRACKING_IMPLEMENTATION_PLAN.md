# Task Tracking Implementation Plan for Mnemosyne
*Practical integration with current priorities and architecture*
*Created: August 24, 2025*

## Executive Summary

This plan shows how to implement task tracking as the unifying substrate for Mnemosyne's core features WITHOUT disrupting current development. Tasks become the bridge between memories (past), chat (present), and intentions (future), while naturally incorporating game mechanics and enabling collective coordination.

**Key Decision**: Build native task tracking deeply integrated with Mnemosyne's sovereignty architecture, with optional OpenProject adapter for external integration if needed.

## Current State Analysis

### What We Have (Working)
- ✅ Memory CRUD with vector embeddings
- ✅ Chat system with authentication
- ✅ Receipt/consent ledger foundation
- ✅ Basic persona system structure
- ✅ PostgreSQL + Redis + Qdrant infrastructure

### Current Priorities (From Roadmap)
1. **Personas + Contextual Presentation** (mask engine)
2. **Vector similarity search** + masked retrieval
3. **Consent Ledger** (minimal receipts)
4. **Synthetic ICV v0** metrics
5. **Private Media Ingestion v0**

### The Integration Opportunity
Tasks can accelerate ALL of these priorities:
- **Personas** suggest tasks based on mode (Mentor → learning tasks)
- **Search** includes task content and metadata
- **Receipts** generated for every task action
- **ICV** evolves through task completion patterns
- **Media** attached to tasks as evidence/context

## Minimal Viable Task System (Phase 0)

### Core Data Model (Start Here)

```python
# backend/app/models/task.py
from sqlalchemy import Column, String, DateTime, Float, JSON, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4

class Task(Base):
    """Minimal task model with sovereignty built in"""
    __tablename__ = "tasks"
    
    # Core fields (MVP)
    id = Column(UUID, primary_key=True, default=uuid4)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Time awareness (MVP)
    created_at = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Status tracking (MVP)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    progress = Column(Float, default=0.0)  # 0.0 to 1.0
    
    # Privacy/Sovereignty (MVP)
    visibility_mask = Column(String, default='private')
    
    # Game mechanics (Phase 1)
    difficulty = Column(Integer, default=1)  # 1-5
    quest_type = Column(String, nullable=True)
    
    # Identity shaping (Phase 1)
    value_impact = Column(JSON, nullable=True)  # {craft: 0.2, care: 0.1}
    
    # Relationships
    receipts = relationship("Receipt", back_populates="task")
    memories = relationship("Memory", secondary="task_memories")
    
class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"
```

### Basic API Endpoints (Week 1)

```python
# backend/app/api/v1/endpoints/tasks.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime

router = APIRouter()

@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new task with receipt generation"""
    
    # Create task
    db_task = Task(
        user_id=current_user.user_id,
        title=task.title,
        description=task.description,
        due_date=task.due_date,
        visibility_mask=task.visibility_mask or current_user.active_mask
    )
    
    # Generate receipt (consent ledger integration)
    receipt = Receipt(
        user_id=current_user.user_id,
        action="task.create",
        data={"task_id": str(db_task.id), "title": task.title},
        timestamp=datetime.utcnow()
    )
    
    db.add(db_task)
    db.add(receipt)
    await db.commit()
    
    return TaskResponse.model_validate(db_task)

@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    status: Optional[TaskStatus] = None,
    include_completed: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's tasks with filtering"""
    query = select(Task).where(Task.user_id == current_user.user_id)
    
    if status:
        query = query.where(Task.status == status)
    if not include_completed:
        query = query.where(Task.status != TaskStatus.COMPLETED)
    
    # Order by due date, with null dates last
    query = query.order_by(Task.due_date.asc().nullslast())
    
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    return [TaskResponse.model_validate(task) for task in tasks]

@router.patch("/tasks/{task_id}/complete")
async def complete_task(
    task_id: UUID,
    evidence: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Complete a task and trigger game mechanics"""
    
    # Get task
    task = await db.get(Task, task_id)
    if not task or task.user_id != current_user.user_id:
        raise HTTPException(404, "Task not found")
    
    # Mark complete
    task.status = TaskStatus.COMPLETED
    task.completed_at = datetime.utcnow()
    task.progress = 1.0
    
    # Generate completion receipt
    receipt = Receipt(
        user_id=current_user.user_id,
        action="task.complete",
        data={
            "task_id": str(task_id),
            "duration": (task.completed_at - task.created_at).total_seconds(),
            "evidence": evidence
        }
    )
    
    # Check for achievements (game mechanics)
    achievements = await check_task_achievements(current_user, task)
    
    # Update user reputation (hidden initially)
    await update_reputation(current_user, task)
    
    # Create memory from completed task
    memory = await task_to_memory(task, evidence)
    
    db.add(receipt)
    db.add(memory)
    await db.commit()
    
    return {
        "task": TaskResponse.model_validate(task),
        "achievements": achievements,
        "memory_created": memory.id
    }
```

## Phase 1: Time Awareness & Calendar (Week 2)

### Calendar Integration

```python
# backend/app/models/task_schedule.py
class TaskSchedule(Base):
    """Time-aware task scheduling"""
    __tablename__ = "task_schedules"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    task_id = Column(UUID, ForeignKey("tasks.id"))
    
    # Scheduling
    scheduled_start = Column(DateTime)
    scheduled_duration = Column(Integer)  # minutes
    actual_start = Column(DateTime, nullable=True)
    actual_duration = Column(Integer, nullable=True)
    
    # Recurrence (using RRULE standard)
    recurrence_rule = Column(String, nullable=True)  # RRULE string
    recurrence_parent = Column(UUID, nullable=True)  # Original task
    
    # Energy management
    energy_required = Column(Integer, default=1)  # 1-5
    best_time_of_day = Column(String)  # morning, afternoon, evening, night

# backend/app/services/calendar_service.py
from icalendar import Calendar, Event
from dateutil.rrule import rrulestr

class CalendarService:
    """Manage task calendar and scheduling"""
    
    async def get_task_calendar(
        self, 
        user: User, 
        start_date: datetime, 
        end_date: datetime
    ) -> str:
        """Generate iCal format calendar of tasks"""
        
        cal = Calendar()
        cal.add('prodid', '-//Mnemosyne//Task Calendar//EN')
        cal.add('version', '2.0')
        
        # Get tasks in date range
        tasks = await self.get_tasks_in_range(user.id, start_date, end_date)
        
        for task in tasks:
            event = Event()
            event.add('summary', task.title)
            event.add('dtstart', task.due_date or task.created_at)
            event.add('dtend', task.due_date + timedelta(hours=1))
            event.add('description', task.description)
            event.add('uid', str(task.id))
            
            # Add game mechanics as categories
            if task.quest_type:
                event.add('categories', [task.quest_type])
            
            cal.add_component(event)
        
        return cal.to_ical().decode('utf-8')
    
    async def suggest_task_time(self, user: User, task: Task) -> datetime:
        """AI-powered scheduling suggestion"""
        
        # Get user's typical patterns
        patterns = await self.analyze_user_patterns(user)
        
        # Consider task properties
        if task.difficulty > 3:
            # Hard tasks need peak performance time
            suggested_time = patterns['peak_performance_window']
        else:
            # Easy tasks can fill gaps
            suggested_time = await self.find_next_gap(user, minutes=30)
        
        # Check for conflicts
        conflicts = await self.check_conflicts(user, suggested_time)
        if conflicts:
            suggested_time = await self.find_alternative(user, suggested_time)
        
        return suggested_time
```

### Recurring Tasks

```python
# backend/app/services/recurring_tasks.py
class RecurringTaskService:
    """Handle recurring tasks with RRULE"""
    
    async def create_recurring_task(
        self,
        template: TaskCreate,
        recurrence_rule: str,
        user: User
    ) -> List[Task]:
        """Create recurring task instances"""
        
        # Parse RRULE
        rrule = rrulestr(recurrence_rule)
        
        # Create parent task
        parent = Task(
            **template.dict(),
            user_id=user.id,
            is_recurring_template=True
        )
        
        # Generate instances for next 30 days
        instances = []
        for dt in rrule[:30]:  # Limit to 30 occurrences
            instance = Task(
                **template.dict(),
                user_id=user.id,
                due_date=dt,
                recurring_parent_id=parent.id
            )
            instances.append(instance)
        
        return instances
    
    # Example daily habit task
    daily_meditation = {
        "title": "Morning Meditation",
        "description": "10 minutes of mindfulness",
        "recurrence": "RRULE:FREQ=DAILY;BYHOUR=7;BYMINUTE=0",
        "difficulty": 1,
        "quest_type": "daily",
        "value_impact": {"mindfulness": 0.1, "resilience": 0.05}
    }
```

## Phase 2: Game Mechanics Integration (Week 3)

### Quest System on Tasks

```python
# backend/app/services/task_quest_service.py
class TaskQuestService:
    """Transform tasks into quests"""
    
    quest_templates = {
        'first_task': {
            'title': 'Begin Your Journey',
            'description': 'Create your first task',
            'trigger': lambda t: t.user.task_count == 1,
            'reward': {'capability': 'advanced_tasks', 'xp': 10}
        },
        'daily_practice': {
            'title': 'Consistent Practice',
            'description': 'Complete a task every day for 7 days',
            'trigger': lambda t: t.check_streak(days=7),
            'reward': {'reputation': {'reliability': 5}, 'xp': 50}
        },
        'deep_work': {
            'title': 'Deep Focus',
            'description': 'Complete a difficulty 5 task',
            'trigger': lambda t: t.difficulty == 5 and t.status == 'completed',
            'reward': {'reputation': {'craft': 10}, 'xp': 100}
        }
    }
    
    async def check_quest_completion(self, user: User, task: Task):
        """Check if task completion triggers quest completion"""
        
        completed_quests = []
        
        for quest_id, quest in self.quest_templates.items():
            if quest['trigger'](task):
                # Quest completed!
                completed_quests.append(quest)
                
                # Grant rewards
                await self.grant_rewards(user, quest['reward'])
                
                # Create achievement receipt
                receipt = Receipt(
                    user_id=user.id,
                    action='quest.complete',
                    data={'quest': quest_id, 'task_id': task.id}
                )
                
        return completed_quests
```

### Task-Based Reputation

```python
# backend/app/services/reputation_service.py
class TaskReputationService:
    """Build reputation through task completion"""
    
    async def calculate_task_reputation(self, task: Task) -> Dict[str, float]:
        """Calculate reputation gained from task"""
        
        rep_change = {}
        
        # Base reputation from difficulty
        rep_change['craft'] = task.difficulty * 2
        
        # On-time completion
        if task.completed_at <= task.due_date:
            rep_change['reliability'] = 5
        
        # Collaborative tasks
        if task.assignees and len(task.assignees) > 1:
            rep_change['collaboration'] = len(task.assignees) * 2
        
        # Value-aligned tasks
        if task.value_impact:
            for value, impact in task.value_impact.items():
                rep_change[value] = impact * 10
        
        return rep_change
    
    async def update_user_reputation(self, user: User, task: Task):
        """Update user's reputation from task completion"""
        
        rep_change = await self.calculate_task_reputation(task)
        
        # Get or create user reputation
        reputation = await self.get_user_reputation(user)
        
        # Apply changes with decay
        for dimension, change in rep_change.items():
            current = getattr(reputation, dimension, 0)
            # Apply decay to old value
            decayed = current * self.calculate_decay(reputation.last_update)
            # Add new reputation
            new_value = decayed + change
            setattr(reputation, dimension, new_value)
        
        reputation.last_update = datetime.utcnow()
        await self.save_reputation(reputation)
```

## Phase 3: Collective Task Coordination (Week 4)

### Shared Tasks

```python
# backend/app/models/shared_task.py
class SharedTask(Base):
    """Tasks with multiple participants"""
    __tablename__ = "shared_tasks"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    task_id = Column(UUID, ForeignKey("tasks.id"))
    
    # Participants
    creator_id = Column(UUID, ForeignKey("users.id"))
    assignees = Column(JSON)  # List of user IDs
    
    # Coordination
    requires_all_complete = Column(Boolean, default=False)
    requires_synchronous = Column(Boolean, default=False)
    
    # Progress tracking
    individual_progress = Column(JSON)  # {user_id: progress}
    
    # Trust building
    trust_impact = Column(Float, default=0.1)  # How much trust increases

# backend/app/services/collective_task_service.py
class CollectiveTaskService:
    """Manage tasks for collectives"""
    
    async def create_collective_goal(
        self,
        collective: Collective,
        goal: str,
        deadline: datetime
    ) -> List[Task]:
        """Break down collective goal into coordinated tasks"""
        
        # Create parent epic task
        epic = Task(
            title=f"[{collective.name}] {goal}",
            description=f"Collective goal: {goal}",
            due_date=deadline,
            quest_type="epic",
            collective_id=collective.id
        )
        
        # Create role-specific subtasks
        subtasks = []
        for member in collective.members:
            role_task = Task(
                title=f"{goal} - {member.role} tasks",
                description=f"Your part in achieving: {goal}",
                due_date=deadline,
                parent_task_id=epic.id,
                assignee_id=member.user_id,
                quest_type="collective"
            )
            subtasks.append(role_task)
        
        # Create coordination points
        sync_task = Task(
            title=f"Sync Meeting: {goal}",
            description="Coordinate progress on collective goal",
            due_date=deadline - timedelta(days=1),
            parent_task_id=epic.id,
            requires_all_assignees=True,
            quest_type="coordination"
        )
        subtasks.append(sync_task)
        
        return [epic] + subtasks
```

## Phase 4: Persona Integration (Ongoing)

### Persona-Suggested Tasks

```python
# backend/app/services/persona_task_service.py
class PersonaTaskService:
    """Personas suggest growth-oriented tasks"""
    
    async def get_persona_suggestions(
        self,
        user: User,
        persona_mode: PersonaMode
    ) -> List[TaskSuggestion]:
        """Generate task suggestions based on persona mode"""
        
        suggestions = []
        
        if persona_mode == PersonaMode.MENTOR:
            # Learning and skill development
            gaps = await self.identify_skill_gaps(user)
            for gap in gaps[:3]:  # Top 3 gaps
                suggestions.append(TaskSuggestion(
                    title=f"Learn: {gap.skill_name}",
                    description=f"Develop your {gap.skill_name} skills",
                    difficulty=gap.difficulty,
                    value_impact={gap.skill_category: 0.2},
                    rationale="I notice you're interested in growing this area"
                ))
        
        elif persona_mode == PersonaMode.CONFIDANT:
            # Reflection and processing
            recent_memories = await self.get_recent_memories(user)
            if recent_memories:
                suggestions.append(TaskSuggestion(
                    title="Reflect on Recent Experiences",
                    description="Process and integrate recent memories",
                    difficulty=2,
                    value_impact={"self_awareness": 0.3},
                    rationale="You have unprocessed experiences worth reflecting on"
                ))
        
        elif persona_mode == PersonaMode.MEDIATOR:
            # Relationship and trust building
            low_trust_connections = await self.get_low_trust_connections(user)
            for connection in low_trust_connections[:2]:
                suggestions.append(TaskSuggestion(
                    title=f"Trust Building with {connection.name}",
                    description="Complete a paired challenge together",
                    difficulty=3,
                    quest_type="paired",
                    assignees=[user.id, connection.id],
                    rationale="Strengthening this connection could be valuable"
                ))
        
        elif persona_mode == PersonaMode.GUARDIAN:
            # Wellbeing and maintenance
            overdue_tasks = await self.get_overdue_tasks(user)
            if overdue_tasks:
                suggestions.append(TaskSuggestion(
                    title="Clear Task Backlog",
                    description="Address overdue tasks for peace of mind",
                    difficulty=2,
                    value_impact={"wellbeing": 0.2},
                    rationale="Clearing these will reduce cognitive load"
                ))
        
        return suggestions
```

## Implementation Timeline

### Week 1: Foundation
- [ ] Create task model and migrations
- [ ] Basic CRUD endpoints
- [ ] Receipt generation for all task actions
- [ ] Simple frontend task list

### Week 2: Time Awareness
- [ ] Add scheduling fields
- [ ] Calendar view endpoint
- [ ] Recurring task support
- [ ] Time-based suggestions

### Week 3: Game Mechanics
- [ ] Quest classification system
- [ ] Achievement detection
- [ ] Reputation calculation
- [ ] Progress visualization

### Week 4: Collaboration
- [ ] Shared task support
- [ ] Collective goal breakdown
- [ ] Dependency tracking
- [ ] Trust impact calculation

### Ongoing: Integration
- [ ] Persona task suggestions
- [ ] Memory-task bridging
- [ ] Search integration
- [ ] ICV evolution tracking

## Decision: Native vs OpenProject

### Recommended: Native Implementation
**Pros**:
- Deep integration with sovereignty architecture
- Game mechanics built-in
- Trust building native
- ICV evolution tracking
- Perfect alignment with vision

**Cons**:
- More development effort
- No existing ecosystem

### Alternative: OpenProject Adapter
**Pros**:
- Faster initial deployment
- Existing project management features
- Community and plugins

**Cons**:
- Limited sovereignty features
- No game mechanics
- External dependency
- Privacy concerns

### Hybrid Approach (Recommended)
1. Build native task system with sovereignty features
2. Create optional OpenProject adapter for teams that need it
3. Sync selective data bidirectionally
4. Maintain Mnemosyne as source of truth

## Success Metrics

### Phase 1 (Week 1)
- Users can create and complete tasks
- Every task action generates receipt
- Tasks appear in frontend

### Phase 2 (Week 2)
- Calendar view working
- Recurring tasks functional
- Time-based suggestions active

### Phase 3 (Week 3)
- Quest classifications applied
- Achievements unlocking
- Reputation accumulating

### Phase 4 (Week 4)
- Shared tasks working
- Collective goals created
- Trust building through tasks

## Conclusion

Task tracking isn't just another feature—it's the practical bridge that connects all of Mnemosyne's ambitious concepts. By implementing it natively with deep integration into the sovereignty architecture, we create:

1. **Concrete Actions**: Abstract concepts become actionable tasks
2. **Natural Gamification**: Tasks inherently become quests
3. **Trust Building**: Shared tasks build real relationships
4. **Time Sovereignty**: Users control their temporal allocation
5. **Collective Coordination**: Groups achieve goals through tasks

This implementation plan shows how to build incrementally, starting with basic task CRUD and gradually adding time awareness, game mechanics, and collective features—all while maintaining the core focus on cognitive sovereignty.

---

*The task system becomes the action layer of cognitive sovereignty—where intention meets execution.*