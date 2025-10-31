"""
Integration Tests for Consensus Validation

Tests the consensus bounds checking (Task 1.4).
"""

import pytest

from app.services.negotiation_service import NegotiationService
from tests.integration.factories import TestDataFactory


class TestConsensusValidation:
    """Test consensus count validation."""

    @pytest.mark.asyncio
    async def test_consensus_count_must_be_at_least_majority(self, test_session):
        """
        CRITICAL VALIDATION TEST (Task 1.4)

        Test that consensus count must be at least majority of participants.
        """
        alice, bob = await TestDataFactory.create_hostile_users(test_session)
        charlie = await TestDataFactory.create_user(test_session, "charlie")

        service = NegotiationService(test_session)

        # 3 participants: minimum consensus = 2 (majority)
        # Try to set consensus to 1 - should fail
        with pytest.raises(ValueError, match="must be at least majority"):
            await service.create_negotiation(
                initiator_id=alice.id,
                title="Invalid Consensus",
                description="Trying minority consensus",
                participant_ids=[alice.id, bob.id, charlie.id],
                initial_terms={"test": "terms"},
                required_consensus_count=1  # TOO LOW
            )

    @pytest.mark.asyncio
    async def test_consensus_count_cannot_exceed_participants(self, test_session):
        """Test that consensus count cannot be greater than participant count."""
        alice, bob = await TestDataFactory.create_hostile_users(test_session)

        service = NegotiationService(test_session)

        # 2 participants, try to require 3 - should fail
        with pytest.raises(ValueError, match="cannot exceed participant count"):
            await service.create_negotiation(
                initiator_id=alice.id,
                title="Invalid Consensus",
                description="Requiring more than exist",
                participant_ids=[alice.id, bob.id],
                initial_terms={"test": "terms"},
                required_consensus_count=3  # TOO HIGH
            )

    @pytest.mark.asyncio
    async def test_consensus_count_must_be_positive(self, test_session):
        """Test that consensus count must be positive."""
        alice, bob = await TestDataFactory.create_hostile_users(test_session)

        service = NegotiationService(test_session)

        # Try consensus = 0
        with pytest.raises(ValueError, match="must be a positive integer"):
            await service.create_negotiation(
                initiator_id=alice.id,
                title="Invalid Consensus",
                description="Zero consensus",
                participant_ids=[alice.id, bob.id],
                initial_terms={"test": "terms"},
                required_consensus_count=0
            )

        # Try negative consensus
        with pytest.raises(ValueError, match="must be a positive integer"):
            await service.create_negotiation(
                initiator_id=alice.id,
                title="Invalid Consensus",
                description="Negative consensus",
                participant_ids=[alice.id, bob.id],
                initial_terms={"test": "terms"},
                required_consensus_count=-1
            )

    @pytest.mark.asyncio
    async def test_default_consensus_is_all_participants(self, test_session):
        """Test that default consensus requirement is ALL participants."""
        alice, bob = await TestDataFactory.create_hostile_users(test_session)
        charlie = await TestDataFactory.create_user(test_session, "charlie")

        service = NegotiationService(test_session)

        # Don't specify consensus count
        negotiation = await service.create_negotiation(
            initiator_id=alice.id,
            title="Default Consensus",
            description="Testing default",
            participant_ids=[alice.id, bob.id, charlie.id],
            initial_terms={"test": "terms"}
            # No required_consensus_count specified
        )

        # Should default to all 3 participants
        assert negotiation.required_consensus_count == 3

    @pytest.mark.asyncio
    async def test_majority_consensus_works(self, test_session):
        """Test that majority consensus (2 of 3) works correctly."""
        alice = await TestDataFactory.create_user(test_session, "alice")
        bob = await TestDataFactory.create_user(test_session, "bob")
        charlie = await TestDataFactory.create_user(test_session, "charlie")

        service = NegotiationService(test_session)

        # Create with majority consensus (2 of 3)
        negotiation = await service.create_negotiation(
            initiator_id=alice.id,
            title="Majority Consensus",
            description="Testing 2 of 3",
            participant_ids=[alice.id, bob.id, charlie.id],
            initial_terms={"test": "terms"},
            required_consensus_count=2  # Majority
        )

        assert negotiation.required_consensus_count == 2

        # All join
        await service.join_negotiation(bob.id, negotiation.id)
        await service.join_negotiation(charlie.id, negotiation.id)

        # Alice and Bob accept (2 of 3)
        await service.accept_terms(negotiation.id, alice.id)
        negotiation = await service.accept_terms(negotiation.id, bob.id)

        # Should reach consensus with just 2
        from app.db.models.negotiation import NegotiationStatus
        assert negotiation.status == NegotiationStatus.CONSENSUS_REACHED
        assert len(negotiation.acceptances) == 2  # Only 2 accepted

    @pytest.mark.asyncio
    async def test_two_party_minimum_is_both(self, test_session):
        """Test that 2-party negotiation requires both (100%)."""
        alice, bob = await TestDataFactory.create_hostile_users(test_session)

        service = NegotiationService(test_session)

        # Can't have 1 of 2 (not majority)
        with pytest.raises(ValueError, match="must be at least majority"):
            await service.create_negotiation(
                initiator_id=alice.id,
                title="One of Two",
                description="Trying 1 of 2",
                participant_ids=[alice.id, bob.id],
                initial_terms={"test": "terms"},
                required_consensus_count=1
            )

        # Must be 2 of 2 (minimum for majority)
        negotiation = await service.create_negotiation(
            initiator_id=alice.id,
            title="Both Required",
            description="2 of 2",
            participant_ids=[alice.id, bob.id],
            initial_terms={"test": "terms"},
            required_consensus_count=2
        )

        assert negotiation.required_consensus_count == 2

    @pytest.mark.asyncio
    async def test_five_party_majority_is_three(self, test_session):
        """Test that 5-party negotiation has minimum 3 (majority)."""
        users = [
            await TestDataFactory.create_user(test_session, f"user_{i}")
            for i in range(5)
        ]

        service = NegotiationService(test_session)

        # 5 participants: majority = 3
        # Can set to 3
        negotiation = await service.create_negotiation(
            initiator_id=users[0].id,
            title="3 of 5",
            description="Majority of 5",
            participant_ids=[u.id for u in users],
            initial_terms={"test": "terms"},
            required_consensus_count=3
        )
        assert negotiation.required_consensus_count == 3

        # Can set to 4
        negotiation = await service.create_negotiation(
            initiator_id=users[0].id,
            title="4 of 5",
            description="Supermajority",
            participant_ids=[u.id for u in users],
            initial_terms={"test": "terms"},
            required_consensus_count=4
        )
        assert negotiation.required_consensus_count == 4

        # Cannot set to 2 (not majority)
        with pytest.raises(ValueError, match="must be at least majority \\(3"):
            await service.create_negotiation(
                initiator_id=users[0].id,
                title="2 of 5",
                description="Minority",
                participant_ids=[u.id for u in users],
                initial_terms={"test": "terms"},
                required_consensus_count=2
            )
