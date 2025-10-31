"""
Negotiation Service

Handles multi-party negotiation workflow for reaching binding agreements
without central authority. Core of the "Trust Without Central Authority" primitive.
"""

import logging
import hashlib
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from app.db.models.negotiation import (
    Negotiation,
    NegotiationMessage,
    NegotiationStatus,
    NegotiationMessageType
)
from app.db.models.user import User
from app.db.models.trust import Appeal, AppealStatus
from app.services.crypto_service import CryptoService

logger = logging.getLogger(__name__)


class NegotiationService:
    """Service for managing multi-party negotiations."""

    def __init__(self, db: AsyncSession):
        """Initialize the negotiation service.

        Args:
            db: Database session
        """
        self.db = db

    async def create_negotiation(
        self,
        initiator_id: UUID,
        title: str,
        description: str,
        participant_ids: List[UUID],
        initial_terms: Dict[str, Any],
        negotiation_days: int = 7,
        finalization_days: int = 3,
        required_consensus_count: Optional[int] = None
    ) -> Negotiation:
        """Create a new negotiation.

        Args:
            initiator_id: User ID of negotiation initiator
            title: Negotiation title
            description: Negotiation description
            participant_ids: List of all participant user IDs (including initiator)
            initial_terms: Initial proposed terms as JSON dict
            negotiation_days: Days until negotiation deadline (default 7)
            finalization_days: Days to finalize after consensus (default 3)
            required_consensus_count: How many must accept (default: all participants)

        Returns:
            Created negotiation
        """
        # Ensure initiator is in participant list
        if initiator_id not in participant_ids:
            participant_ids.append(initiator_id)

        participant_count = len(participant_ids)

        # Validate and set consensus requirements
        if required_consensus_count is not None:
            # Must be positive integer
            if not isinstance(required_consensus_count, int) or required_consensus_count <= 0:
                raise ValueError(
                    f"Consensus count must be a positive integer (got: {required_consensus_count})"
                )

            # Must be at least majority
            min_consensus = (participant_count // 2) + 1
            if required_consensus_count < min_consensus:
                raise ValueError(
                    f"Consensus count must be at least majority ({min_consensus} of {participant_count} participants)"
                )

            # Cannot exceed total participants
            if required_consensus_count > participant_count:
                raise ValueError(
                    f"Consensus count cannot exceed participant count (got {required_consensus_count}, max {participant_count})"
                )
        else:
            # Default: require ALL participants to accept
            required_consensus_count = participant_count

        # Calculate deadlines
        now = datetime.utcnow()
        negotiation_deadline = now + timedelta(days=negotiation_days)
        finalization_deadline = now + timedelta(days=finalization_days)

        negotiation = Negotiation(
            initiator_id=initiator_id,
            title=title,
            description=description,
            participant_ids=participant_ids,
            joined_participant_ids=[initiator_id],  # Initiator auto-joins
            required_consensus_count=required_consensus_count,
            status=NegotiationStatus.INITIATED,
            current_terms=initial_terms,
            terms_version=1,
            terms_history=[{
                'version': 1,
                'terms': initial_terms,
                'proposed_by': str(initiator_id),
                'timestamp': now.isoformat()
            }],
            negotiation_deadline=negotiation_deadline,
            finalization_deadline=finalization_deadline,
            acceptances={},
            finalizations={},
            negotiation_metadata={}
        )

        # Calculate content hash
        negotiation.content_hash = self._calculate_negotiation_hash(negotiation)

        self.db.add(negotiation)
        await self.db.commit()
        await self.db.refresh(negotiation)

        # Create INITIATE message
        await self._create_message(
            negotiation_id=negotiation.id,
            sender_id=initiator_id,
            message_type=NegotiationMessageType.INITIATE,
            terms=initial_terms,
            terms_version=1,
            message_text=f"Initiated negotiation: {title}"
        )

        logger.info(f"Created negotiation {negotiation.id}: {title}")
        return negotiation

    async def join_negotiation(
        self,
        negotiation_id: UUID,
        participant_id: UUID
    ) -> Negotiation:
        """Join a negotiation as a participant.

        Args:
            negotiation_id: Negotiation to join
            participant_id: User ID joining

        Returns:
            Updated negotiation

        Raises:
            ValueError: If not invited or already joined or wrong status
        """
        negotiation = await self.db.get(Negotiation, negotiation_id)
        if not negotiation:
            raise ValueError(f"Negotiation {negotiation_id} not found")

        # Must be invited
        if participant_id not in negotiation.participant_ids:
            raise ValueError(f"User {participant_id} not invited to this negotiation")

        # Can't join if not INITIATED
        if negotiation.status != NegotiationStatus.INITIATED:
            raise ValueError(f"Negotiation not in INITIATED status (current: {negotiation.status.value})")

        # Check if already joined
        if participant_id in negotiation.joined_participant_ids:
            logger.info(f"User {participant_id} already joined negotiation {negotiation_id}")
            return negotiation

        # Add to joined list
        negotiation.joined_participant_ids = negotiation.joined_participant_ids + [participant_id]

        # Check if all participants have joined
        if set(negotiation.joined_participant_ids) == set(negotiation.participant_ids):
            negotiation.status = NegotiationStatus.NEGOTIATING
            logger.info(f"All participants joined negotiation {negotiation_id}, status → NEGOTIATING")

        # Update hash
        negotiation.content_hash = self._calculate_negotiation_hash(negotiation)

        await self.db.commit()
        await self.db.refresh(negotiation)

        # Create JOIN message
        await self._create_message(
            negotiation_id=negotiation_id,
            sender_id=participant_id,
            message_type=NegotiationMessageType.JOIN,
            message_text="Joined negotiation"
        )

        return negotiation

    async def send_offer(
        self,
        negotiation_id: UUID,
        sender_id: UUID,
        terms: Dict[str, Any],
        message_text: Optional[str] = None
    ) -> Tuple[Negotiation, NegotiationMessage]:
        """Send an offer or counter-offer.

        Args:
            negotiation_id: Negotiation to send offer to
            sender_id: User ID sending offer
            terms: Proposed terms
            message_text: Optional explanation

        Returns:
            Tuple of (updated negotiation, created message)

        Raises:
            ValueError: If not participant or wrong status
        """
        negotiation = await self.db.get(Negotiation, negotiation_id)
        if not negotiation:
            raise ValueError(f"Negotiation {negotiation_id} not found")

        # Must be participant
        if sender_id not in negotiation.participant_ids:
            raise ValueError(f"User {sender_id} not a participant in this negotiation")

        # Must be NEGOTIATING
        if negotiation.status != NegotiationStatus.NEGOTIATING:
            raise ValueError(f"Negotiation not in NEGOTIATING status (current: {negotiation.status.value})")

        # Increment terms version
        new_version = negotiation.terms_version + 1

        # Update negotiation
        negotiation.current_terms = terms
        negotiation.terms_version = new_version

        # Add to terms history
        if not negotiation.terms_history:
            negotiation.terms_history = []
        negotiation.terms_history.append({
            'version': new_version,
            'terms': terms,
            'proposed_by': str(sender_id),
            'timestamp': datetime.utcnow().isoformat()
        })

        # Clear acceptances (new terms need new acceptances)
        negotiation.acceptances = {}

        # Update hash
        negotiation.content_hash = self._calculate_negotiation_hash(negotiation)

        await self.db.commit()
        await self.db.refresh(negotiation)

        # Determine message type
        message_type = (NegotiationMessageType.OFFER if new_version == 2
                       else NegotiationMessageType.COUNTER_OFFER)

        # Create message
        message = await self._create_message(
            negotiation_id=negotiation_id,
            sender_id=sender_id,
            message_type=message_type,
            terms=terms,
            terms_version=new_version,
            message_text=message_text or f"Proposed terms v{new_version}"
        )

        logger.info(f"User {sender_id} sent {message_type.value} for negotiation {negotiation_id} (v{new_version})")
        return negotiation, message

    async def accept_terms(
        self,
        negotiation_id: UUID,
        acceptor_id: UUID,
        signature: Optional[str] = None,
        message_text: Optional[str] = None
    ) -> Negotiation:
        """Accept current terms.

        Args:
            negotiation_id: Negotiation to accept
            acceptor_id: User ID accepting
            signature: Optional cryptographic signature (Ed25519, base64-encoded)
            message_text: Optional explanation

        Returns:
            Updated negotiation (may transition to CONSENSUS_REACHED)

        Raises:
            ValueError: If not participant or wrong status or invalid signature
        """
        negotiation = await self.db.get(Negotiation, negotiation_id)
        if not negotiation:
            raise ValueError(f"Negotiation {negotiation_id} not found")

        # Must be participant
        if acceptor_id not in negotiation.participant_ids:
            raise ValueError(f"User {acceptor_id} not a participant in this negotiation")

        # Must be NEGOTIATING
        if negotiation.status != NegotiationStatus.NEGOTIATING:
            raise ValueError(f"Negotiation not in NEGOTIATING status (current: {negotiation.status.value})")

        # Verify signature if provided
        signature_verified = False
        if signature:
            # Get user's public key
            user = await self.db.get(User, acceptor_id)
            if not user or not user.public_key:
                raise ValueError(f"User {acceptor_id} has no public key registered")

            # Create canonical message to verify
            message_to_sign = self._create_acceptance_message(
                negotiation_id=negotiation_id,
                terms=negotiation.current_terms,
                terms_version=negotiation.terms_version
            )

            # Verify signature
            signature_verified = CryptoService.verify_ed25519_signature(
                public_key_b64=user.public_key,
                message=message_to_sign,
                signature_b64=signature
            )

            if not signature_verified:
                raise ValueError("Invalid signature for acceptance")

            logger.info(f"Signature verified for user {acceptor_id} accepting negotiation {negotiation_id}")

        # Record acceptance
        if not negotiation.acceptances:
            negotiation.acceptances = {}

        # Update dict by reassigning to trigger SQLAlchemy change tracking
        updated_acceptances = negotiation.acceptances.copy()
        updated_acceptances[str(acceptor_id)] = {
            'version': negotiation.terms_version,
            'timestamp': datetime.utcnow().isoformat(),
            'signature': signature,
            'signature_verified': signature_verified
        }
        negotiation.acceptances = updated_acceptances

        # Check for consensus
        consensus_reached = self._check_consensus(negotiation)

        if consensus_reached:
            negotiation.status = NegotiationStatus.CONSENSUS_REACHED
            negotiation.consensus_reached_at = datetime.utcnow()
            logger.info(f"Consensus reached for negotiation {negotiation_id}!")

        # Update hash
        negotiation.content_hash = self._calculate_negotiation_hash(negotiation)

        await self.db.commit()
        await self.db.refresh(negotiation)

        # Create ACCEPT message
        await self._create_message(
            negotiation_id=negotiation_id,
            sender_id=acceptor_id,
            message_type=NegotiationMessageType.ACCEPT,
            terms_version=negotiation.terms_version,
            message_text=message_text or f"Accepted terms v{negotiation.terms_version}",
            signature=signature,
            signature_verified=signature_verified
        )

        return negotiation

    async def finalize_commitment(
        self,
        negotiation_id: UUID,
        finalizer_id: UUID,
        signature: Optional[str] = None
    ) -> Negotiation:
        """Finalize binding commitment.

        Args:
            negotiation_id: Negotiation to finalize
            finalizer_id: User ID finalizing
            signature: Optional cryptographic signature (Ed25519, base64-encoded)

        Returns:
            Updated negotiation (may transition to BINDING)

        Raises:
            ValueError: If not consensus reached or not participant or invalid signature
        """
        negotiation = await self.db.get(Negotiation, negotiation_id)
        if not negotiation:
            raise ValueError(f"Negotiation {negotiation_id} not found")

        # Must be participant
        if finalizer_id not in negotiation.participant_ids:
            raise ValueError(f"User {finalizer_id} not a participant in this negotiation")

        # Must be CONSENSUS_REACHED
        if negotiation.status != NegotiationStatus.CONSENSUS_REACHED:
            raise ValueError(f"Negotiation not in CONSENSUS_REACHED status (current: {negotiation.status.value})")

        # Verify signature if provided
        signature_verified = False
        if signature:
            # Get user's public key
            user = await self.db.get(User, finalizer_id)
            if not user or not user.public_key:
                raise ValueError(f"User {finalizer_id} has no public key registered")

            # Create canonical message to verify
            message_to_sign = self._create_finalization_message(
                negotiation_id=negotiation_id,
                binding_terms=negotiation.current_terms,
                terms_version=negotiation.terms_version
            )

            # Verify signature
            signature_verified = CryptoService.verify_ed25519_signature(
                public_key_b64=user.public_key,
                message=message_to_sign,
                signature_b64=signature
            )

            if not signature_verified:
                raise ValueError("Invalid signature for finalization")

            logger.info(f"Signature verified for user {finalizer_id} finalizing negotiation {negotiation_id}")

        # Record finalization
        if not negotiation.finalizations:
            negotiation.finalizations = {}

        # Update dict by reassigning to trigger SQLAlchemy change tracking
        updated_finalizations = negotiation.finalizations.copy()
        updated_finalizations[str(finalizer_id)] = {
            'timestamp': datetime.utcnow().isoformat(),
            'signature': signature,
            'signature_verified': signature_verified
        }
        negotiation.finalizations = updated_finalizations

        # Check if all participants have finalized
        if len(negotiation.finalizations) == len(negotiation.participant_ids):
            # ALL PARTIES FINALIZED - MAKE IT BINDING
            negotiation.status = NegotiationStatus.BINDING
            negotiation.binding_timestamp = datetime.utcnow()
            negotiation.binding_terms = negotiation.current_terms
            negotiation.binding_hash = self._calculate_binding_hash(negotiation)

            logger.info(f"Negotiation {negotiation_id} is now BINDING!")

        # Update hash
        negotiation.content_hash = self._calculate_negotiation_hash(negotiation)

        await self.db.commit()
        await self.db.refresh(negotiation)

        # Create FINALIZE message
        await self._create_message(
            negotiation_id=negotiation_id,
            sender_id=finalizer_id,
            message_type=NegotiationMessageType.FINALIZE,
            message_text="Finalized binding commitment"
        )

        return negotiation

    async def withdraw(
        self,
        negotiation_id: UUID,
        withdrawer_id: UUID,
        reason: Optional[str] = None
    ) -> Negotiation:
        """Withdraw from negotiation.

        Args:
            negotiation_id: Negotiation to withdraw from
            withdrawer_id: User ID withdrawing
            reason: Optional reason for withdrawal

        Returns:
            Updated negotiation (status → TERMINATED)

        Raises:
            ValueError: If not participant or wrong status
        """
        negotiation = await self.db.get(Negotiation, negotiation_id)
        if not negotiation:
            raise ValueError(f"Negotiation {negotiation_id} not found")

        # Must be participant
        if withdrawer_id not in negotiation.participant_ids:
            raise ValueError(f"User {withdrawer_id} not a participant in this negotiation")

        # Can't withdraw from BINDING
        if negotiation.status == NegotiationStatus.BINDING:
            raise ValueError("Cannot withdraw from binding agreement (use dispute instead)")

        # Terminate negotiation
        negotiation.status = NegotiationStatus.TERMINATED

        # Record withdrawal in metadata
        if not negotiation.negotiation_metadata:
            negotiation.negotiation_metadata = {}

        negotiation.negotiation_metadata['withdrawal'] = {
            'withdrawer_id': str(withdrawer_id),
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat()
        }

        # Update hash
        negotiation.content_hash = self._calculate_negotiation_hash(negotiation)

        await self.db.commit()
        await self.db.refresh(negotiation)

        # Create WITHDRAW message
        await self._create_message(
            negotiation_id=negotiation_id,
            sender_id=withdrawer_id,
            message_type=NegotiationMessageType.WITHDRAW,
            message_text=reason or "Withdrew from negotiation"
        )

        logger.info(f"User {withdrawer_id} withdrew from negotiation {negotiation_id}")
        return negotiation

    async def dispute_binding(
        self,
        negotiation_id: UUID,
        disputer_id: UUID,
        dispute_reason: str
    ) -> Tuple[Negotiation, Appeal]:
        """Dispute a binding agreement (creates appeal).

        Args:
            negotiation_id: Binding negotiation to dispute
            disputer_id: User ID disputing
            dispute_reason: Reason for dispute

        Returns:
            Tuple of (updated negotiation, created appeal)

        Raises:
            ValueError: If not binding or not participant
        """
        negotiation = await self.db.get(Negotiation, negotiation_id)
        if not negotiation:
            raise ValueError(f"Negotiation {negotiation_id} not found")

        # Must be participant
        if disputer_id not in negotiation.participant_ids:
            raise ValueError(f"User {disputer_id} not a participant in this negotiation")

        # Must be BINDING
        if negotiation.status != NegotiationStatus.BINDING:
            raise ValueError(f"Can only dispute BINDING agreements (current: {negotiation.status.value})")

        # Update negotiation status
        negotiation.status = NegotiationStatus.DISPUTED

        # Update hash
        negotiation.content_hash = self._calculate_negotiation_hash(negotiation)

        await self.db.commit()
        await self.db.refresh(negotiation)

        # Create DISPUTE message
        await self._create_message(
            negotiation_id=negotiation_id,
            sender_id=disputer_id,
            message_type=NegotiationMessageType.DISPUTE,
            message_text=dispute_reason
        )

        # Create TrustEvent for the dispute
        from app.db.models.trust import TrustEvent, TrustEventType
        from app.services.appeals_service import AppealResolutionService
        from datetime import timedelta

        # Determine who is the "other party" (subject of the trust event)
        # For simplicity, if there are exactly 2 participants, the other is the subject
        other_participant_ids = [pid for pid in negotiation.participant_ids if pid != disputer_id]
        subject_id = other_participant_ids[0] if other_participant_ids else disputer_id

        # Create TrustEvent representing the dispute/conflict
        trust_event = TrustEvent(
            actor_id=disputer_id,
            subject_id=subject_id,
            event_type=TrustEventType.CONFLICT,
            trust_delta=-0.1,  # Disputes slightly reduce trust
            context={
                'negotiation_id': str(negotiation_id),
                'dispute_reason': dispute_reason,
                'binding_hash': negotiation.binding_hash,
                'binding_terms': negotiation.binding_terms,
                'timestamp': datetime.utcnow().isoformat()
            },
            reporter_id=disputer_id,
            visibility_scope='private',
            user_consent=True  # Explicit action by disputer
        )

        # Calculate trust event hash
        import hashlib
        import json
        trust_event_hashable = {
            'actor_id': str(trust_event.actor_id),
            'subject_id': str(trust_event.subject_id),
            'event_type': trust_event.event_type.value,
            'context': trust_event.context,
            'timestamp': datetime.utcnow().isoformat()
        }
        trust_event_json = json.dumps(trust_event_hashable, sort_keys=True, separators=(',', ':'))
        trust_event.content_hash = hashlib.sha256(trust_event_json.encode('utf-8')).hexdigest()

        self.db.add(trust_event)
        await self.db.flush()  # Get trust_event.id without committing

        # Create Appeal linked to TrustEvent
        appeal_service = AppealResolutionService(self.db)
        appeal = Appeal(
            trust_event_id=trust_event.id,
            appellant_id=disputer_id,
            status=AppealStatus.PENDING,
            appeal_reason=dispute_reason,
            evidence={
                'negotiation_id': str(negotiation_id),
                'binding_hash': negotiation.binding_hash,
                'binding_terms': negotiation.binding_terms,
                'binding_timestamp': negotiation.binding_timestamp.isoformat() if negotiation.binding_timestamp else None
            },
            review_deadline=datetime.utcnow() + timedelta(days=7)  # 7-day SLA
        )

        self.db.add(appeal)
        await self.db.commit()
        await self.db.refresh(trust_event)
        await self.db.refresh(appeal)

        logger.info(f"Negotiation {negotiation_id} disputed by {disputer_id}")
        logger.info(f"Created TrustEvent {trust_event.id} and Appeal {appeal.id}")

        return negotiation, appeal

    async def check_timeouts(self) -> Dict[str, List[Negotiation]]:
        """Check for negotiations past their deadlines.

        Returns:
            Dict with 'negotiation_timeouts' and 'finalization_timeouts' lists
        """
        now = datetime.utcnow()

        # Find negotiations past deadline without consensus
        negotiation_result = await self.db.execute(
            select(Negotiation).where(
                and_(
                    Negotiation.status.in_([
                        NegotiationStatus.INITIATED,
                        NegotiationStatus.NEGOTIATING
                    ]),
                    Negotiation.negotiation_deadline < now
                )
            )
        )
        negotiation_timeouts = list(negotiation_result.scalars())

        # Find consensus past finalization deadline
        finalization_result = await self.db.execute(
            select(Negotiation).where(
                and_(
                    Negotiation.status == NegotiationStatus.CONSENSUS_REACHED,
                    Negotiation.finalization_deadline < now
                )
            )
        )
        finalization_timeouts = list(finalization_result.scalars())

        # Update expired negotiations
        for negotiation in negotiation_timeouts + finalization_timeouts:
            negotiation.status = NegotiationStatus.EXPIRED
            negotiation.content_hash = self._calculate_negotiation_hash(negotiation)

        if negotiation_timeouts or finalization_timeouts:
            await self.db.commit()
            logger.warning(f"Found {len(negotiation_timeouts)} negotiation timeouts and {len(finalization_timeouts)} finalization timeouts")

        return {
            'negotiation_timeouts': negotiation_timeouts,
            'finalization_timeouts': finalization_timeouts
        }

    # Helper methods

    def _check_consensus(self, negotiation: Negotiation) -> bool:
        """Check if consensus has been reached.

        Args:
            negotiation: Negotiation to check

        Returns:
            True if consensus reached, False otherwise
        """
        acceptances = negotiation.acceptances or {}

        # Need required_consensus_count acceptances
        if len(acceptances) < negotiation.required_consensus_count:
            return False

        # All acceptances must be for same terms_version
        current_version = negotiation.terms_version
        for acceptance in acceptances.values():
            if acceptance['version'] != current_version:
                return False

        return True

    def _calculate_negotiation_hash(self, negotiation: Negotiation) -> str:
        """Calculate deterministic hash of negotiation state.

        Args:
            negotiation: Negotiation to hash

        Returns:
            SHA-256 hash as hex string
        """
        hashable = {
            'id': str(negotiation.id),
            'participant_ids': sorted([str(pid) for pid in negotiation.participant_ids]),
            'current_terms': negotiation.current_terms,
            'terms_version': negotiation.terms_version,
            'status': negotiation.status.value,
            'acceptances': negotiation.acceptances,
            'finalizations': negotiation.finalizations,
        }

        json_str = json.dumps(hashable, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()

    def _calculate_binding_hash(self, negotiation: Negotiation) -> str:
        """Calculate irreversible binding commitment hash.

        Args:
            negotiation: Negotiation to create binding hash for

        Returns:
            SHA-256 hash as hex string
        """
        binding_data = {
            'negotiation_id': str(negotiation.id),
            'final_terms': negotiation.current_terms,
            'terms_version': negotiation.terms_version,
            'participant_ids': sorted([str(pid) for pid in negotiation.participant_ids]),
            'acceptances': negotiation.acceptances,
            'finalizations': negotiation.finalizations,
            'timestamp': negotiation.binding_timestamp.isoformat() if negotiation.binding_timestamp else None,
        }

        json_str = json.dumps(binding_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()

    async def _create_message(
        self,
        negotiation_id: UUID,
        sender_id: UUID,
        message_type: NegotiationMessageType,
        terms: Optional[Dict[str, Any]] = None,
        terms_version: Optional[int] = None,
        message_text: Optional[str] = None,
        signature: Optional[str] = None,
        signature_verified: bool = False
    ) -> NegotiationMessage:
        """Create a negotiation message.

        Args:
            negotiation_id: Negotiation this message belongs to
            sender_id: User ID sending message
            message_type: Type of message
            terms: Optional terms (for OFFER/COUNTER_OFFER)
            terms_version: Optional terms version
            message_text: Optional message text
            signature: Optional Ed25519 signature (base64-encoded)
            signature_verified: Whether signature was verified

        Returns:
            Created message
        """
        message = NegotiationMessage(
            negotiation_id=negotiation_id,
            sender_id=sender_id,
            message_type=message_type,
            terms=terms,
            terms_version=terms_version,
            message_text=message_text,
            signature_ed25519=signature,
            signature_verified=signature_verified
        )

        # Calculate content hash
        hashable = {
            'negotiation_id': str(negotiation_id),
            'sender_id': str(sender_id),
            'message_type': message_type.value,
            'terms': terms,
            'terms_version': terms_version,
            'message_text': message_text,
            'timestamp': datetime.utcnow().isoformat()
        }
        json_str = json.dumps(hashable, sort_keys=True, separators=(',', ':'))
        message.content_hash = hashlib.sha256(json_str.encode('utf-8')).hexdigest()

        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)

        return message

    def _create_acceptance_message(
        self,
        negotiation_id: UUID,
        terms: Dict[str, Any],
        terms_version: int
    ) -> str:
        """Create canonical message for acceptance signature.

        Args:
            negotiation_id: Negotiation ID
            terms: Terms being accepted
            terms_version: Version of terms

        Returns:
            Canonical message string to sign
        """
        canonical = {
            'action': 'ACCEPT',
            'negotiation_id': str(negotiation_id),
            'terms': terms,
            'terms_version': terms_version
        }
        return json.dumps(canonical, sort_keys=True, separators=(',', ':'))

    def _create_finalization_message(
        self,
        negotiation_id: UUID,
        binding_terms: Dict[str, Any],
        terms_version: int
    ) -> str:
        """Create canonical message for finalization signature.

        Args:
            negotiation_id: Negotiation ID
            binding_terms: Final binding terms
            terms_version: Version of terms

        Returns:
            Canonical message string to sign
        """
        canonical = {
            'action': 'FINALIZE',
            'negotiation_id': str(negotiation_id),
            'binding_terms': binding_terms,
            'terms_version': terms_version
        }
        return json.dumps(canonical, sort_keys=True, separators=(',', ':'))
