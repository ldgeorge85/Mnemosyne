"""
Test Data Factories

Factory pattern for creating test data with sensible defaults.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
from uuid import uuid4, UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User
from app.db.models.negotiation import Negotiation, NegotiationStatus
from app.db.models.trust import TrustEvent, TrustEventType, Appeal, AppealStatus


class TestDataFactory:
    """Factory for creating test data."""

    @staticmethod
    async def create_user(
        session: AsyncSession,
        username: str,
        email: str | None = None,
        with_keys: bool = False
    ) -> User:
        """Create a test user.

        Args:
            session: Database session
            username: Username
            email: Email (defaults to {username}@test.com)
            with_keys: Whether to add mock keypair

        Returns:
            Created user
        """
        if email is None:
            email = f"{username}@test.com"

        user = User(
            id=uuid4(),
            username=username,
            email=email,
            hashed_password="test_password_hash"
        )

        if with_keys:
            user.public_key = f"mock_public_key_{username}"
            user.encrypted_private_key = {
                "algorithm": "Ed25519",
                "encrypted_key": f"mock_encrypted_{username}",
                "salt": "mock_salt",
                "iv": "mock_iv",
                "iterations": 100000
            }

        session.add(user)
        await session.flush()
        return user

    @staticmethod
    async def create_hostile_users(
        session: AsyncSession
    ) -> tuple[User, User]:
        """Create a pair of hostile users (Alice and Bob).

        Returns:
            Tuple of (alice, bob)
        """
        alice = await TestDataFactory.create_user(session, "alice", with_keys=True)
        bob = await TestDataFactory.create_user(session, "bob", with_keys=True)
        return alice, bob

    @staticmethod
    async def create_negotiation(
        session: AsyncSession,
        initiator: User,
        participants: List[User],
        title: str = "Test Negotiation",
        initial_terms: Dict[str, Any] | None = None,
        status: NegotiationStatus = NegotiationStatus.INITIATED,
        negotiation_days: int = 7,
        finalization_days: int = 3
    ) -> Negotiation:
        """Create a test negotiation.

        Args:
            session: Database session
            initiator: User who creates the negotiation
            participants: List of all participants (including initiator)
            title: Negotiation title
            initial_terms: Initial proposed terms
            status: Initial status
            negotiation_days: Days until negotiation deadline
            finalization_days: Days to finalize after consensus

        Returns:
            Created negotiation
        """
        if initial_terms is None:
            initial_terms = {"compensation": 1000, "payment_method": "bank_transfer"}

        participant_ids = [p.id for p in participants]
        if initiator.id not in participant_ids:
            participant_ids.insert(0, initiator.id)

        now = datetime.utcnow()
        negotiation = Negotiation(
            id=uuid4(),
            initiator_id=initiator.id,
            title=title,
            description=f"Test negotiation: {title}",
            participant_ids=participant_ids,
            joined_participant_ids=[initiator.id],
            required_consensus_count=len(participant_ids),
            status=status,
            current_terms=initial_terms,
            terms_version=1,
            terms_history=[{
                'version': 1,
                'terms': initial_terms,
                'proposed_by': str(initiator.id),
                'timestamp': now.isoformat()
            }],
            negotiation_deadline=now + timedelta(days=negotiation_days),
            finalization_deadline=now + timedelta(days=finalization_days),
            acceptances={},
            finalizations={},
            content_hash="mock_hash",
            negotiation_metadata={}
        )

        session.add(negotiation)
        await session.flush()
        return negotiation

    @staticmethod
    async def create_binding_negotiation(
        session: AsyncSession,
        initiator: User,
        participants: List[User],
        binding_terms: Dict[str, Any] | None = None
    ) -> Negotiation:
        """Create a negotiation that's already BINDING.

        Args:
            session: Database session
            initiator: User who creates the negotiation
            participants: List of all participants
            binding_terms: Final agreed terms

        Returns:
            Created binding negotiation
        """
        if binding_terms is None:
            binding_terms = {"compensation": 750, "payment_method": "bank_transfer"}

        negotiation = await TestDataFactory.create_negotiation(
            session=session,
            initiator=initiator,
            participants=participants,
            initial_terms=binding_terms,
            status=NegotiationStatus.BINDING
        )

        # Set binding fields
        negotiation.binding_timestamp = datetime.utcnow()
        negotiation.binding_terms = binding_terms
        negotiation.binding_hash = "mock_binding_hash"
        negotiation.consensus_reached_at = datetime.utcnow() - timedelta(hours=1)

        # Mark all participants as having accepted and finalized
        for participant in participants:
            negotiation.acceptances[str(participant.id)] = {
                'version': 1,
                'timestamp': datetime.utcnow().isoformat(),
                'signature': f'mock_signature_{participant.id}'
            }
            negotiation.finalizations[str(participant.id)] = {
                'timestamp': datetime.utcnow().isoformat(),
                'signature': f'mock_finalization_{participant.id}'
            }

        await session.flush()
        return negotiation

    @staticmethod
    async def create_trust_event(
        session: AsyncSession,
        actor: User,
        subject: User,
        event_type: TrustEventType = TrustEventType.CONFLICT,
        context: Dict[str, Any] | None = None
    ) -> TrustEvent:
        """Create a test trust event.

        Args:
            session: Database session
            actor: User who triggered the event
            subject: User affected by the event
            event_type: Type of trust event
            context: Event context

        Returns:
            Created trust event
        """
        if context is None:
            context = {"test": "event"}

        trust_event = TrustEvent(
            id=uuid4(),
            actor_id=actor.id,
            subject_id=subject.id,
            event_type=event_type,
            trust_delta=-0.1 if event_type == TrustEventType.CONFLICT else 0.1,
            context=context,
            reporter_id=actor.id,
            content_hash="mock_trust_event_hash"
        )

        session.add(trust_event)
        await session.flush()
        return trust_event

    @staticmethod
    async def create_appeal(
        session: AsyncSession,
        trust_event: TrustEvent,
        appellant: User,
        reason: str = "Test appeal reason"
    ) -> Appeal:
        """Create a test appeal.

        Args:
            session: Database session
            trust_event: Related trust event
            appellant: User filing the appeal
            reason: Appeal reason

        Returns:
            Created appeal
        """
        appeal = Appeal(
            id=uuid4(),
            trust_event_id=trust_event.id,
            appellant_id=appellant.id,
            status=AppealStatus.PENDING,
            appeal_reason=reason,
            evidence={"test": "evidence"},
            review_deadline=datetime.utcnow() + timedelta(days=7)
        )

        session.add(appeal)
        await session.flush()
        return appeal
