"""
Appeals Resolution Service

Handles resolver assignment, review board workflow, and status transitions
for trust event appeals with proper separation of duties.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from app.db.models.trust import Appeal, TrustEvent, AppealStatus
from app.db.models.user import User

logger = logging.getLogger(__name__)


class AppealResolverCriteria:
    """Criteria for selecting appeal resolvers."""

    @staticmethod
    def is_eligible_resolver(
        user: User,
        appeal: Appeal,
        trust_event: TrustEvent
    ) -> bool:
        """Check if a user is eligible to resolve an appeal.

        Separation of duties requirements:
        - Cannot be the appellant
        - Cannot be the reporter of the trust event
        - Cannot be the actor or subject of the trust event
        - Should be an active user

        Args:
            user: User to check
            appeal: Appeal to resolve
            trust_event: Related trust event

        Returns:
            True if eligible, False otherwise
        """
        user_id = user.id

        # Cannot be directly involved
        if user_id == appeal.appellant_id:
            return False
        if user_id == trust_event.reporter_id:
            return False
        if user_id == trust_event.actor_id:
            return False
        if user_id == trust_event.subject_id:
            return False

        # Must be active (could add more criteria here)
        # For now, just check user exists and is not banned
        if hasattr(user, 'is_active') and not user.is_active:
            return False

        return True


class AppealResolutionService:
    """Service for managing appeal resolution workflow."""

    def __init__(self, db: AsyncSession):
        """Initialize the appeals resolution service.

        Args:
            db: Database session
        """
        self.db = db

    async def assign_resolver(
        self,
        appeal_id: UUID,
        preferred_resolver_id: Optional[UUID] = None
    ) -> UUID:
        """Assign a resolver to an appeal.

        Uses separation of duties to ensure impartial resolution.

        Args:
            appeal_id: Appeal to assign resolver to
            preferred_resolver_id: Optional preferred resolver (if eligible)

        Returns:
            ID of assigned resolver

        Raises:
            ValueError: If no eligible resolvers found
        """
        # Get appeal and trust event
        appeal = await self.db.get(Appeal, appeal_id)
        if not appeal:
            raise ValueError(f"Appeal {appeal_id} not found")

        trust_event = await self.db.get(TrustEvent, appeal.trust_event_id)
        if not trust_event:
            raise ValueError(f"Trust event {appeal.trust_event_id} not found")

        # Check if preferred resolver is eligible
        if preferred_resolver_id:
            preferred_user = await self.db.get(User, preferred_resolver_id)
            if preferred_user and AppealResolverCriteria.is_eligible_resolver(
                preferred_user, appeal, trust_event
            ):
                trust_event.resolver_id = preferred_resolver_id
                await self.db.commit()
                logger.info(f"Assigned preferred resolver {preferred_resolver_id} to appeal {appeal_id}")
                return preferred_resolver_id

        # Get all potential resolvers
        result = await self.db.execute(select(User))
        all_users = result.scalars().all()

        # Filter eligible resolvers
        eligible_resolvers = [
            user for user in all_users
            if AppealResolverCriteria.is_eligible_resolver(user, appeal, trust_event)
        ]

        if not eligible_resolvers:
            raise ValueError(f"No eligible resolvers found for appeal {appeal_id}")

        # Simple random selection (could be more sophisticated)
        # Future: weight by trust score, expertise, availability, etc.
        selected_resolver = random.choice(eligible_resolvers)

        trust_event.resolver_id = selected_resolver.id
        await self.db.commit()

        logger.info(f"Assigned resolver {selected_resolver.id} to appeal {appeal_id}")
        return selected_resolver.id

    async def assign_review_board(
        self,
        appeal_id: UUID,
        board_size: int = 3
    ) -> List[UUID]:
        """Assign a review board for complex appeals.

        Review board provides multi-party consensus for important cases.

        Args:
            appeal_id: Appeal to assign board to
            board_size: Number of reviewers (default 3 for majority vote)

        Returns:
            List of review board member IDs

        Raises:
            ValueError: If not enough eligible reviewers
        """
        # Get appeal and trust event
        appeal = await self.db.get(Appeal, appeal_id)
        if not appeal:
            raise ValueError(f"Appeal {appeal_id} not found")

        trust_event = await self.db.get(TrustEvent, appeal.trust_event_id)
        if not trust_event:
            raise ValueError(f"Trust event {appeal.trust_event_id} not found")

        # Get all potential reviewers
        result = await self.db.execute(select(User))
        all_users = result.scalars().all()

        # Filter eligible reviewers
        eligible_reviewers = [
            user for user in all_users
            if AppealResolverCriteria.is_eligible_resolver(user, appeal, trust_event)
        ]

        if len(eligible_reviewers) < board_size:
            raise ValueError(
                f"Not enough eligible reviewers. Need {board_size}, found {len(eligible_reviewers)}"
            )

        # Randomly select board members
        board_members = random.sample(eligible_reviewers, board_size)
        board_member_ids = [member.id for member in board_members]

        # Update appeal with board
        appeal.review_board_ids = board_member_ids
        await self.db.commit()

        logger.info(f"Assigned review board {board_member_ids} to appeal {appeal_id}")
        return board_member_ids

    async def transition_status(
        self,
        appeal_id: UUID,
        new_status: AppealStatus,
        resolution: Optional[str] = None
    ) -> Appeal:
        """Transition appeal to new status.

        Implements state machine for appeal lifecycle:
        PENDING → REVIEWING → RESOLVED/WITHDRAWN/ESCALATED

        Args:
            appeal_id: Appeal to transition
            new_status: New status
            resolution: Optional resolution text

        Returns:
            Updated appeal

        Raises:
            ValueError: If transition is invalid
        """
        appeal = await self.db.get(Appeal, appeal_id)
        if not appeal:
            raise ValueError(f"Appeal {appeal_id} not found")

        old_status = appeal.status

        # Validate state transitions
        valid_transitions = {
            AppealStatus.PENDING: [AppealStatus.REVIEWING, AppealStatus.WITHDRAWN],
            AppealStatus.REVIEWING: [AppealStatus.RESOLVED, AppealStatus.ESCALATED, AppealStatus.WITHDRAWN],
            AppealStatus.RESOLVED: [],  # Terminal state
            AppealStatus.WITHDRAWN: [],  # Terminal state
            AppealStatus.ESCALATED: [AppealStatus.REVIEWING, AppealStatus.RESOLVED]
        }

        if new_status not in valid_transitions.get(old_status, []):
            raise ValueError(
                f"Invalid transition from {old_status.value} to {new_status.value}"
            )

        # Update status
        appeal.status = new_status

        # Handle status-specific logic
        if new_status == AppealStatus.RESOLVED:
            appeal.resolved_at = datetime.utcnow()
            if resolution:
                appeal.resolution = resolution

            # Mark trust event as resolved
            trust_event = await self.db.get(TrustEvent, appeal.trust_event_id)
            if trust_event:
                trust_event.resolved_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(appeal)

        logger.info(f"Transitioned appeal {appeal_id} from {old_status.value} to {new_status.value}")
        return appeal

    async def check_sla_violations(self) -> List[Appeal]:
        """Check for appeals that have exceeded their review deadline.

        Returns:
            List of appeals with SLA violations
        """
        now = datetime.utcnow()

        result = await self.db.execute(
            select(Appeal).where(
                and_(
                    Appeal.status.in_([AppealStatus.PENDING, AppealStatus.REVIEWING]),
                    Appeal.review_deadline < now
                )
            )
        )

        overdue_appeals = result.scalars().all()

        if overdue_appeals:
            logger.warning(f"Found {len(overdue_appeals)} appeals with SLA violations")

        return overdue_appeals

    async def escalate_appeal(
        self,
        appeal_id: UUID,
        reason: str
    ) -> Appeal:
        """Escalate an appeal (e.g., due to SLA violation or complexity).

        Args:
            appeal_id: Appeal to escalate
            reason: Reason for escalation

        Returns:
            Updated appeal with escalated status
        """
        appeal = await self.db.get(Appeal, appeal_id)
        if not appeal:
            raise ValueError(f"Appeal {appeal_id} not found")

        # Transition to escalated status
        appeal = await self.transition_status(appeal_id, AppealStatus.ESCALATED)

        # Log escalation
        if not appeal.appeal_metadata:
            appeal.appeal_metadata = {}

        appeal.appeal_metadata['escalation'] = {
            'escalated_at': datetime.utcnow().isoformat(),
            'reason': reason
        }

        # Assign review board if not already assigned
        if not appeal.review_board_ids:
            await self.assign_review_board(appeal_id, board_size=5)  # Larger board for escalated cases

        await self.db.commit()
        await self.db.refresh(appeal)

        logger.info(f"Escalated appeal {appeal_id}: {reason}")
        return appeal

    async def record_board_vote(
        self,
        appeal_id: UUID,
        reviewer_id: UUID,
        vote: str,  # "uphold" or "overturn"
        reasoning: Optional[str] = None
    ) -> Dict[str, Any]:
        """Record a review board member's vote.

        Args:
            appeal_id: Appeal being voted on
            reviewer_id: ID of reviewer voting
            vote: Vote ("uphold" or "overturn")
            reasoning: Optional reasoning for vote

        Returns:
            Vote record with current tally

        Raises:
            ValueError: If reviewer not on board or invalid vote
        """
        appeal = await self.db.get(Appeal, appeal_id)
        if not appeal:
            raise ValueError(f"Appeal {appeal_id} not found")

        # Verify reviewer is on board
        if not appeal.review_board_ids or reviewer_id not in appeal.review_board_ids:
            raise ValueError(f"Reviewer {reviewer_id} not on review board for appeal {appeal_id}")

        # Validate vote
        if vote not in ['uphold', 'overturn']:
            raise ValueError(f"Invalid vote: {vote}. Must be 'uphold' or 'overturn'")

        # Initialize votes structure if needed
        if not appeal.appeal_metadata:
            appeal.appeal_metadata = {}
        if 'votes' not in appeal.appeal_metadata:
            appeal.appeal_metadata['votes'] = {}

        # Record vote
        appeal.appeal_metadata['votes'][str(reviewer_id)] = {
            'vote': vote,
            'reasoning': reasoning,
            'timestamp': datetime.utcnow().isoformat()
        }

        await self.db.commit()
        await self.db.refresh(appeal)

        # Calculate current tally
        votes = appeal.appeal_metadata.get('votes', {})
        uphold_count = sum(1 for v in votes.values() if v['vote'] == 'uphold')
        overturn_count = sum(1 for v in votes.values() if v['vote'] == 'overturn')

        logger.info(f"Recorded vote for appeal {appeal_id}: {vote} (tally: {uphold_count} uphold, {overturn_count} overturn)")

        return {
            'appeal_id': str(appeal_id),
            'vote_recorded': True,
            'current_tally': {
                'uphold': uphold_count,
                'overturn': overturn_count,
                'total_votes': len(votes),
                'board_size': len(appeal.review_board_ids)
            }
        }

    async def check_board_consensus(
        self,
        appeal_id: UUID
    ) -> Optional[str]:
        """Check if review board has reached consensus.

        Consensus = majority vote (> 50% of board)

        Args:
            appeal_id: Appeal to check

        Returns:
            "uphold" or "overturn" if consensus reached, None otherwise
        """
        appeal = await self.db.get(Appeal, appeal_id)
        if not appeal or not appeal.review_board_ids:
            return None

        votes = appeal.appeal_metadata.get('votes', {}) if appeal.appeal_metadata else {}

        if not votes:
            return None

        board_size = len(appeal.review_board_ids)
        uphold_count = sum(1 for v in votes.values() if v['vote'] == 'uphold')
        overturn_count = sum(1 for v in votes.values() if v['vote'] == 'overturn')

        # Majority threshold
        majority = (board_size // 2) + 1

        if uphold_count >= majority:
            return 'uphold'
        elif overturn_count >= majority:
            return 'overturn'

        return None
