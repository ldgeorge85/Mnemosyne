"""
Integration Tests for Complete Negotiation Flow

Tests the core innovation: hostile parties reaching binding agreements
without central authority.
"""

import pytest
from datetime import datetime, timedelta

from app.services.negotiation_service import NegotiationService
from app.db.models.negotiation import NegotiationStatus
from tests.integration.factories import TestDataFactory


class TestCompleteNegotiationFlow:
    """Test the complete negotiation workflow from initiation to binding."""

    @pytest.mark.asyncio
    async def test_hostile_parties_reach_binding_agreement(self, test_session):
        """
        THE CORE INNOVATION TEST

        Two hostile parties (Alice and Bob) negotiate and reach a binding
        agreement without any central authority involvement.
        """
        # Setup: Create hostile users
        alice, bob = await TestDataFactory.create_hostile_users(test_session)

        service = NegotiationService(test_session)

        # Step 1: Alice initiates negotiation
        initial_terms = {
            "compensation": 1000,
            "payment_method": "bank_transfer",
            "deadline": "2024-12-31"
        }

        negotiation = await service.create_negotiation(
            initiator_id=alice.id,
            title="Privacy Violation Settlement",
            description="Alice claims Bob violated privacy agreement",
            participant_ids=[alice.id, bob.id],
            initial_terms=initial_terms,
            negotiation_days=7,
            finalization_days=3
        )

        assert negotiation.status == NegotiationStatus.INITIATED
        assert negotiation.initiator_id == alice.id
        assert alice.id in negotiation.participant_ids
        assert bob.id in negotiation.participant_ids
        assert negotiation.current_terms == initial_terms

        # Step 2: Bob joins the negotiation
        negotiation = await service.join_negotiation(negotiation.id, bob.id)

        assert negotiation.status == NegotiationStatus.NEGOTIATING
        assert bob.id in negotiation.joined_participant_ids

        # Step 3: Bob sends counter-offer (negotiation happens)
        counter_terms = {
            "compensation": 500,
            "payment_method": "bank_transfer",
            "deadline": "2025-06-30"
        }

        negotiation, _ = await service.send_offer(
            negotiation.id,
            bob.id,
            counter_terms,
            "Offering $500 instead of $1000"
        )

        assert negotiation.current_terms == counter_terms
        assert negotiation.terms_version == 2
        assert negotiation.acceptances == {}  # Counter-offer clears acceptances

        # Step 4: Alice sends another counter-offer
        compromise_terms = {
            "compensation": 750,
            "payment_method": "bank_transfer",
            "deadline": "2025-03-31"
        }

        negotiation, _ = await service.send_offer(
            negotiation.id,
            alice.id,
            compromise_terms,
            "Let's meet in the middle at $750"
        )

        assert negotiation.current_terms == compromise_terms
        assert negotiation.terms_version == 3

        # Step 5: Both parties accept the compromise terms
        negotiation = await service.accept_terms(
            negotiation.id,
            alice.id,
            signature="alice_signature_mock"
        )

        assert negotiation.status == NegotiationStatus.NEGOTIATING  # Not consensus yet
        assert str(alice.id) in negotiation.acceptances

        negotiation = await service.accept_terms(
            negotiation.id,
            bob.id,
            signature="bob_signature_mock"
        )

        # CONSENSUS REACHED!
        assert negotiation.status == NegotiationStatus.CONSENSUS_REACHED
        assert str(bob.id) in negotiation.acceptances
        assert len(negotiation.acceptances) == 2
        assert negotiation.consensus_reached_at is not None

        # Step 6: Both parties finalize (make it binding)
        negotiation = await service.finalize_commitment(
            negotiation.id,
            alice.id,
            signature="alice_finalization_mock"
        )

        assert negotiation.status == NegotiationStatus.CONSENSUS_REACHED  # Not binding yet
        assert str(alice.id) in negotiation.finalizations

        negotiation = await service.finalize_commitment(
            negotiation.id,
            bob.id,
            signature="bob_finalization_mock"
        )

        # BINDING AGREEMENT CREATED!
        assert negotiation.status == NegotiationStatus.BINDING
        assert str(bob.id) in negotiation.finalizations
        assert len(negotiation.finalizations) == 2
        assert negotiation.binding_hash is not None
        assert negotiation.binding_timestamp is not None
        assert negotiation.binding_terms == compromise_terms

        # Step 7: Verify immutability - can't send new offers
        with pytest.raises(ValueError, match="not in NEGOTIATING status"):
            await service.send_offer(
                negotiation.id,
                alice.id,
                {"compensation": 100},
                "Changed my mind!"
            )

        # SUCCESS: Two hostile parties reached binding agreement!
        print(f"\n✅ SUCCESS: Binding agreement reached!")
        print(f"   Negotiation ID: {negotiation.id}")
        print(f"   Final terms: {negotiation.binding_terms}")
        print(f"   Binding hash: {negotiation.binding_hash}")
        print(f"   No central authority involved!")

    @pytest.mark.asyncio
    async def test_consensus_requires_all_acceptances_on_same_version(self, test_session):
        """Test that consensus requires all parties to accept the SAME terms version."""
        alice, bob = await TestDataFactory.create_hostile_users(test_session)
        service = NegotiationService(test_session)

        # Create and join negotiation
        negotiation = await service.create_negotiation(
            initiator_id=alice.id,
            title="Test Consensus",
            description="Testing consensus detection",
            participant_ids=[alice.id, bob.id],
            initial_terms={"test": "v1"}
        )
        negotiation = await service.join_negotiation(negotiation.id, bob.id)

        # Alice accepts version 1
        negotiation = await service.accept_terms(negotiation.id, alice.id)
        assert negotiation.status == NegotiationStatus.NEGOTIATING  # No consensus yet

        # Bob sends counter-offer (version 2)
        negotiation, _ = await service.send_offer(
            negotiation.id,
            bob.id,
            {"test": "v2"}
        )

        # Alice's acceptance was cleared
        assert negotiation.acceptances == {}

        # Bob accepts version 2
        negotiation = await service.accept_terms(negotiation.id, bob.id)
        assert negotiation.status == NegotiationStatus.NEGOTIATING  # Still no consensus

        # Alice accepts version 2
        negotiation = await service.accept_terms(negotiation.id, alice.id)
        assert negotiation.status == NegotiationStatus.CONSENSUS_REACHED  # NOW we have consensus!

    @pytest.mark.asyncio
    async def test_three_party_negotiation(self, test_session):
        """Test negotiation with 3 participants."""
        alice = await TestDataFactory.create_user(test_session, "alice", with_keys=True)
        bob = await TestDataFactory.create_user(test_session, "bob", with_keys=True)
        charlie = await TestDataFactory.create_user(test_session, "charlie", with_keys=True)

        service = NegotiationService(test_session)

        # Create negotiation
        negotiation = await service.create_negotiation(
            initiator_id=alice.id,
            title="Three-Way Agreement",
            description="Testing multi-party negotiation",
            participant_ids=[alice.id, bob.id, charlie.id],
            initial_terms={"amount": 1000}
        )

        assert negotiation.required_consensus_count == 3  # All must agree

        # All join
        await service.join_negotiation(negotiation.id, bob.id)
        negotiation = await service.join_negotiation(negotiation.id, charlie.id)
        assert negotiation.status == NegotiationStatus.NEGOTIATING

        # All must accept for consensus
        await service.accept_terms(negotiation.id, alice.id)
        await service.accept_terms(negotiation.id, bob.id)
        negotiation = await service.accept_terms(negotiation.id, charlie.id)
        assert negotiation.status == NegotiationStatus.CONSENSUS_REACHED

        # All must finalize for binding
        await service.finalize_commitment(negotiation.id, alice.id)
        await service.finalize_commitment(negotiation.id, bob.id)
        negotiation = await service.finalize_commitment(negotiation.id, charlie.id)
        assert negotiation.status == NegotiationStatus.BINDING

    @pytest.mark.asyncio
    async def test_withdrawal_terminates_negotiation(self, test_session):
        """Test that withdrawal terminates the negotiation."""
        alice, bob = await TestDataFactory.create_hostile_users(test_session)
        service = NegotiationService(test_session)

        negotiation = await service.create_negotiation(
            initiator_id=alice.id,
            title="Test Withdrawal",
            description="Testing withdrawal",
            participant_ids=[alice.id, bob.id],
            initial_terms={"test": "terms"}
        )
        await service.join_negotiation(negotiation.id, bob.id)

        # Bob withdraws
        negotiation = await service.withdraw(
            negotiation.id,
            bob.id,
            reason="Changed my mind"
        )

        assert negotiation.status == NegotiationStatus.TERMINATED
        assert negotiation.negotiation_metadata['withdrawal']['withdrawer_id'] == str(bob.id)

    @pytest.mark.asyncio
    async def test_cannot_withdraw_from_binding_agreement(self, test_session):
        """Test that you cannot withdraw from a binding agreement."""
        alice, bob = await TestDataFactory.create_hostile_users(test_session)

        # Create binding negotiation
        negotiation = await TestDataFactory.create_binding_negotiation(
            test_session,
            alice,
            [alice, bob]
        )

        service = NegotiationService(test_session)

        # Try to withdraw - should fail
        with pytest.raises(ValueError, match="Cannot withdraw from binding agreement"):
            await service.withdraw(negotiation.id, alice.id, "I want out")
