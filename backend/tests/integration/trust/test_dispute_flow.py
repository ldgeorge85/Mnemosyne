"""
Integration Tests for Dispute and Appeals Flow

Tests that binding agreements can be disputed and appealed.
"""

import pytest
from datetime import timedelta

from app.services.negotiation_service import NegotiationService
from app.db.models.negotiation import NegotiationStatus
from app.db.models.trust import AppealStatus, TrustEventType
from tests.integration.factories import TestDataFactory


class TestDisputeResolution:
    """Test dispute and appeals workflow."""

    @pytest.mark.asyncio
    async def test_binding_agreement_can_be_disputed(self, test_session):
        """
        CRITICAL FIX TEST (Task 1.1)

        Test that disputing a binding agreement creates a TrustEvent
        and an Appeal properly.
        """
        # Setup: Create binding agreement
        alice, bob = await TestDataFactory.create_hostile_users(test_session)

        binding_negotiation = await TestDataFactory.create_binding_negotiation(
            test_session,
            alice,
            [alice, bob],
            binding_terms={"compensation": 750, "deadline": "2024-12-31"}
        )

        assert binding_negotiation.status == NegotiationStatus.BINDING

        service = NegotiationService(test_session)

        # Alice disputes the binding agreement
        negotiation, appeal = await service.dispute_binding(
            binding_negotiation.id,
            alice.id,
            "Bob did not fulfill the agreed terms"
        )

        # Verify negotiation is now DISPUTED
        assert negotiation.status == NegotiationStatus.DISPUTED
        assert negotiation.id == binding_negotiation.id

        # Verify appeal was created
        assert appeal is not None
        assert appeal.appellant_id == alice.id
        assert appeal.status == AppealStatus.PENDING
        assert appeal.appeal_reason == "Bob did not fulfill the agreed terms"
        assert appeal.review_deadline is not None

        # Verify appeal evidence contains negotiation details
        assert appeal.evidence is not None
        assert str(binding_negotiation.id) in str(appeal.evidence['negotiation_id'])
        assert appeal.evidence['binding_hash'] == binding_negotiation.binding_hash

        # Verify TrustEvent was created
        assert appeal.trust_event_id is not None

        # Fetch the trust event
        from sqlalchemy import select
        from app.db.models.trust import TrustEvent

        result = await test_session.execute(
            select(TrustEvent).where(TrustEvent.id == appeal.trust_event_id)
        )
        trust_event = result.scalar_one()

        assert trust_event.actor_id == alice.id
        assert trust_event.subject_id == bob.id
        assert trust_event.event_type == TrustEventType.CONFLICT
        assert trust_event.reporter_id == alice.id
        assert str(binding_negotiation.id) in str(trust_event.context['negotiation_id'])

        print(f"\n✅ SUCCESS: Dispute created TrustEvent and Appeal!")
        print(f"   Negotiation: {negotiation.id} → DISPUTED")
        print(f"   TrustEvent: {trust_event.id}")
        print(f"   Appeal: {appeal.id} → PENDING")

    @pytest.mark.asyncio
    async def test_cannot_dispute_non_binding_negotiation(self, test_session):
        """Test that you can only dispute BINDING negotiations."""
        alice, bob = await TestDataFactory.create_hostile_users(test_session)
        service = NegotiationService(test_session)

        # Create negotiation in NEGOTIATING status
        negotiation = await service.create_negotiation(
            initiator_id=alice.id,
            title="Not Yet Binding",
            description="Still negotiating",
            participant_ids=[alice.id, bob.id],
            initial_terms={"test": "terms"}
        )

        # Try to dispute - should fail
        with pytest.raises(ValueError, match="Can only dispute BINDING agreements"):
            await service.dispute_binding(
                negotiation.id,
                alice.id,
                "Attempting to dispute non-binding"
            )

    @pytest.mark.asyncio
    async def test_non_participant_cannot_dispute(self, test_session):
        """Test that only participants can dispute."""
        alice, bob = await TestDataFactory.create_hostile_users(test_session)
        charlie = await TestDataFactory.create_user(test_session, "charlie")

        binding_negotiation = await TestDataFactory.create_binding_negotiation(
            test_session,
            alice,
            [alice, bob]
        )

        service = NegotiationService(test_session)

        # Charlie tries to dispute - should fail
        with pytest.raises(ValueError, match="not a participant"):
            await service.dispute_binding(
                binding_negotiation.id,
                charlie.id,
                "I wasn't even part of this"
            )

    @pytest.mark.asyncio
    async def test_appeal_has_proper_deadline(self, test_session):
        """Test that appeals have a 7-day review deadline."""
        from datetime import datetime

        alice, bob = await TestDataFactory.create_hostile_users(test_session)

        binding_negotiation = await TestDataFactory.create_binding_negotiation(
            test_session,
            alice,
            [alice, bob]
        )

        service = NegotiationService(test_session)

        before_dispute = datetime.utcnow()
        _, appeal = await service.dispute_binding(
            binding_negotiation.id,
            alice.id,
            "Test dispute"
        )
        after_dispute = datetime.utcnow()

        # Appeal should have ~7 day deadline
        deadline_from_before = appeal.review_deadline - before_dispute
        deadline_from_after = appeal.review_deadline - after_dispute

        # Should be approximately 7 days (within a few seconds tolerance)
        assert timedelta(days=6, hours=23) < deadline_from_before < timedelta(days=7, hours=1)
        assert timedelta(days=6, hours=23) < deadline_from_after < timedelta(days=7, hours=1)
