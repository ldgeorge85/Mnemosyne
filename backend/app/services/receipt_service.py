"""
Receipt Service

Handles the creation and management of receipts for transparency and audit trail.
"""

import logging
import hashlib
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from fastapi import Request

from app.db.models.receipt import Receipt, ReceiptType
from app.db.models.user import User
from app.core.config import settings

logger = logging.getLogger(__name__)


class ReceiptService:
    """Service for managing receipts and transparency."""

    def __init__(self, db: AsyncSession, request: Optional[Request] = None):
        """Initialize the receipt service.

        Args:
            db: Database session
            request: Optional FastAPI request object for tracking receipt creation
        """
        self.db = db
        self.request = request

    def _calculate_content_hash(self, receipt_data: Dict[str, Any]) -> str:
        """Calculate SHA-256 hash of receipt contents.

        Creates a deterministic hash of the receipt data for cryptographic integrity.
        The hash includes all receipt fields except the hash fields themselves.

        Args:
            receipt_data: Dictionary of receipt data to hash

        Returns:
            Hex string of SHA-256 hash
        """
        # Exclude hash fields from the hash calculation
        hashable_data = {k: v for k, v in receipt_data.items()
                        if k not in ['content_hash', 'previous_hash']}

        # Convert UUIDs to strings for JSON serialization
        normalized_data = {}
        for key, value in hashable_data.items():
            if value is None:
                # Ensure consistent None handling
                normalized_data[key] = None
            elif isinstance(value, UUID):
                normalized_data[key] = str(value)
            elif isinstance(value, datetime):
                normalized_data[key] = value.isoformat()
            elif hasattr(value, 'value'):  # Enum
                normalized_data[key] = value.value
            elif isinstance(value, (dict, list)):
                # Ensure consistent JSON serialization for dicts/lists
                normalized_data[key] = value
            else:
                normalized_data[key] = value

        # Create deterministic JSON string (sorted keys)
        # Use separators to ensure consistent formatting
        json_str = json.dumps(normalized_data, sort_keys=True, separators=(',', ':'), default=str)

        # Calculate SHA-256 hash
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()

    async def _get_last_receipt_hash(self, user_id: UUID) -> Optional[str]:
        """Get the content hash of the most recent receipt for a user.

        This enables receipt chaining for cryptographic audit trails.

        Args:
            user_id: User ID to get last receipt for

        Returns:
            Content hash of the last receipt, or None if no previous receipts
        """
        try:
            query = select(Receipt).where(
                Receipt.user_id == user_id
            ).order_by(Receipt.timestamp.desc()).limit(1)

            result = await self.db.execute(query)
            last_receipt = result.scalar_one_or_none()

            if last_receipt and last_receipt.content_hash:
                return last_receipt.content_hash

            return None

        except Exception as e:
            logger.warning(f"Error getting last receipt hash: {e}")
            return None
    
    async def create_receipt(
        self,
        user_id: UUID,
        receipt_type: ReceiptType,
        action: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        context: Optional[Dict[str, Any]] = None,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        persona_mode: Optional[str] = None,
        worldview_profile: Optional[Dict[str, Any]] = None,
        decisions_made: Optional[List[Dict[str, Any]]] = None,
        confidence_score: Optional[float] = None,
        alternatives_considered: Optional[List[str]] = None,
        consent_basis: Optional[str] = None,
        data_categories: Optional[List[str]] = None,
        privacy_impact: Optional[str] = None,
        explanation: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        parent_receipt_id: Optional[UUID] = None,
        user_visible: bool = True
    ) -> Receipt:
        """Create a new receipt for transparency.
        
        Args:
            user_id: ID of the user performing the action
            receipt_type: Type of receipt
            action: Human-readable description of the action
            entity_type: Type of entity affected (e.g., "memory", "task")
            entity_id: ID of the affected entity
            context: Additional context about the action
            request_data: Sanitized request data
            response_data: Sanitized response data
            persona_mode: Active persona mode during action
            worldview_profile: Active worldview configuration
            decisions_made: List of decisions and their rationale
            confidence_score: Confidence in the action (0-1)
            alternatives_considered: Other options that were evaluated
            consent_basis: Legal/ethical basis for the action
            data_categories: Categories of data involved
            privacy_impact: Privacy impact level (Low/Medium/High)
            explanation: Human-readable explanation
            ip_address: Client IP address
            user_agent: Client user agent
            session_id: Session identifier
            correlation_id: For linking related receipts
            parent_receipt_id: For nested operations
            user_visible: Whether user can see this receipt
            
        Returns:
            Created receipt
        """
        try:
            # Sanitize sensitive data from request/response
            if request_data:
                request_data = self._sanitize_data(request_data)
            if response_data:
                response_data = self._sanitize_data(response_data)

            # Get previous receipt hash for chaining
            previous_hash = await self._get_last_receipt_hash(user_id)

            # Create receipt ID and timestamp
            receipt_id = uuid4()
            timestamp = datetime.utcnow()

            # Prepare receipt data for hashing
            receipt_data = {
                'id': receipt_id,
                'user_id': user_id,
                'receipt_type': receipt_type,
                'timestamp': timestamp,
                'action': action,
                'entity_type': entity_type,
                'entity_id': entity_id,
                'context': context,
                'request_data': request_data,
                'response_data': response_data,
                'persona_mode': persona_mode,
                'worldview_profile': worldview_profile,
                'decisions_made': decisions_made,
                'confidence_score': confidence_score,
                'alternatives_considered': alternatives_considered,
                'consent_basis': consent_basis,
                'data_categories': data_categories,
                'privacy_impact': privacy_impact,
                'user_visible': user_visible,
                'explanation': explanation,
                'service_name': "mnemosyne-backend",
                'service_version': settings.VERSION if hasattr(settings, 'VERSION') else "1.0.0",
                'correlation_id': correlation_id or str(uuid4()),
                'parent_receipt_id': parent_receipt_id,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'session_id': session_id,
                'previous_hash': previous_hash
            }

            # Calculate content hash
            content_hash = self._calculate_content_hash(receipt_data)

            # Create receipt with cryptographic hashes
            receipt = Receipt(
                id=receipt_id,
                user_id=user_id,
                receipt_type=receipt_type,
                timestamp=timestamp,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                context=context,
                request_data=request_data,
                response_data=response_data,
                persona_mode=persona_mode,
                worldview_profile=worldview_profile,
                decisions_made=decisions_made,
                confidence_score=confidence_score,
                alternatives_considered=alternatives_considered,
                consent_basis=consent_basis,
                data_categories=data_categories,
                privacy_impact=privacy_impact,
                user_visible=user_visible,
                explanation=explanation,
                service_name="mnemosyne-backend",
                service_version=settings.VERSION if hasattr(settings, 'VERSION') else "1.0.0",
                correlation_id=correlation_id or str(uuid4()),
                parent_receipt_id=parent_receipt_id,
                ip_address=ip_address,
                user_agent=user_agent,
                session_id=session_id,
                content_hash=content_hash,
                previous_hash=previous_hash
            )

            self.db.add(receipt)
            await self.db.commit()
            await self.db.refresh(receipt)

            # Mark receipt as created in request state for middleware tracking
            if self.request and hasattr(self.request.state, 'receipt_created'):
                self.request.state.receipt_created = True

            logger.info(f"Receipt created: {receipt.id} for user {user_id}, type: {receipt_type.value}")
            return receipt
            
        except Exception as e:
            logger.error(f"Error creating receipt: {e}")
            await self.db.rollback()
            raise
    
    async def get_user_receipts(
        self,
        user_id: UUID,
        receipt_type: Optional[ReceiptType] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
        only_visible: bool = True
    ) -> List[Receipt]:
        """Get receipts for a user.
        
        Args:
            user_id: User ID
            receipt_type: Filter by receipt type
            entity_type: Filter by entity type
            entity_id: Filter by entity ID
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum number of receipts to return
            offset: Number of receipts to skip
            only_visible: Only return user-visible receipts
            
        Returns:
            List of receipts
        """
        try:
            query = select(Receipt).where(Receipt.user_id == user_id)
            
            if only_visible:
                query = query.where(Receipt.user_visible == True)
            
            if receipt_type:
                query = query.where(Receipt.receipt_type == receipt_type)
            
            if entity_type:
                query = query.where(Receipt.entity_type == entity_type)
            
            if entity_id:
                query = query.where(Receipt.entity_id == entity_id)
            
            if start_date:
                query = query.where(Receipt.timestamp >= start_date)
            
            if end_date:
                query = query.where(Receipt.timestamp <= end_date)
            
            query = query.order_by(Receipt.timestamp.desc())
            query = query.limit(limit).offset(offset)
            
            result = await self.db.execute(query)
            receipts = result.scalars().all()
            
            return receipts
            
        except Exception as e:
            logger.error(f"Error getting user receipts: {e}")
            raise
    
    async def get_receipt_by_id(self, receipt_id: UUID, user_id: UUID) -> Optional[Receipt]:
        """Get a specific receipt by ID.
        
        Args:
            receipt_id: Receipt ID
            user_id: User ID (for authorization)
            
        Returns:
            Receipt if found and authorized, None otherwise
        """
        try:
            query = select(Receipt).where(
                and_(
                    Receipt.id == receipt_id,
                    Receipt.user_id == user_id,
                    Receipt.user_visible == True
                )
            )
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error getting receipt by ID: {e}")
            raise
    
    async def get_entity_receipts(
        self,
        entity_type: str,
        entity_id: UUID,
        user_id: UUID
    ) -> List[Receipt]:
        """Get all receipts for a specific entity.
        
        Args:
            entity_type: Type of entity
            entity_id: Entity ID
            user_id: User ID (for authorization)
            
        Returns:
            List of receipts for the entity
        """
        try:
            query = select(Receipt).where(
                and_(
                    Receipt.entity_type == entity_type,
                    Receipt.entity_id == entity_id,
                    Receipt.user_id == user_id,
                    Receipt.user_visible == True
                )
            ).order_by(Receipt.timestamp.desc())
            
            result = await self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting entity receipts: {e}")
            raise
    
    async def create_memory_receipt(
        self,
        user_id: UUID,
        memory_id: UUID,
        action: str,
        receipt_type: ReceiptType,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Receipt:
        """Create a receipt for a memory operation.
        
        Args:
            user_id: User ID
            memory_id: Memory ID
            action: Action description
            receipt_type: Type of receipt
            request_data: Request data
            response_data: Response data
            **kwargs: Additional receipt fields
            
        Returns:
            Created receipt
        """
        return await self.create_receipt(
            user_id=user_id,
            receipt_type=receipt_type,
            action=action,
            entity_type="memory",
            entity_id=memory_id,
            request_data=request_data,
            response_data=response_data,
            consent_basis="User-initiated action",
            data_categories=["memory", "personal"],
            privacy_impact="Low",
            **kwargs
        )
    
    async def create_task_receipt(
        self,
        user_id: UUID,
        task_id: UUID,
        action: str,
        receipt_type: ReceiptType,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Receipt:
        """Create a receipt for a task operation.
        
        Args:
            user_id: User ID
            task_id: Task ID
            action: Action description
            receipt_type: Type of receipt
            request_data: Request data
            response_data: Response data
            **kwargs: Additional receipt fields
            
        Returns:
            Created receipt
        """
        return await self.create_receipt(
            user_id=user_id,
            receipt_type=receipt_type,
            action=action,
            entity_type="task",
            entity_id=task_id,
            request_data=request_data,
            response_data=response_data,
            consent_basis="User-initiated action",
            data_categories=["task", "productivity"],
            privacy_impact="Low",
            **kwargs
        )
    
    async def create_chat_receipt(
        self,
        user_id: UUID,
        message_id: UUID,
        action: str,
        persona_mode: str,
        worldview_profile: Optional[Dict[str, Any]] = None,
        decisions_made: Optional[List[Dict[str, Any]]] = None,
        confidence_score: Optional[float] = None,
        **kwargs
    ) -> Receipt:
        """Create a receipt for a chat interaction.
        
        Args:
            user_id: User ID
            message_id: Message ID
            action: Action description
            persona_mode: Active persona mode
            worldview_profile: Worldview configuration
            decisions_made: Decisions made during interaction
            confidence_score: Confidence in response
            **kwargs: Additional receipt fields
            
        Returns:
            Created receipt
        """
        return await self.create_receipt(
            user_id=user_id,
            receipt_type=ReceiptType.CHAT_MESSAGE,
            action=action,
            entity_type="message",
            entity_id=message_id,
            persona_mode=persona_mode,
            worldview_profile=worldview_profile,
            decisions_made=decisions_made,
            confidence_score=confidence_score,
            consent_basis="User-initiated conversation",
            data_categories=["conversation", "ai_interaction"],
            privacy_impact="Medium",
            **kwargs
        )
    
    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize sensitive data from request/response.
        
        Args:
            data: Data to sanitize
            
        Returns:
            Sanitized data
        """
        # List of sensitive keys to remove or mask
        sensitive_keys = [
            'password', 'hashed_password', 'token', 'api_key', 
            'secret', 'private_key', 'access_token', 'refresh_token'
        ]
        
        sanitized = {}
        for key, value in data.items():
            # Check if key contains sensitive terms
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                # Recursively sanitize nested dictionaries
                sanitized[key] = self._sanitize_data(value)
            elif isinstance(value, list):
                # Handle lists
                sanitized[key] = [
                    self._sanitize_data(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized
    
    async def get_receipt_stats(
        self,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get receipt statistics for a user.

        Args:
            user_id: User ID
            start_date: Start date for stats
            end_date: End date for stats

        Returns:
            Dictionary with receipt statistics
        """
        try:
            query = select(Receipt).where(
                and_(
                    Receipt.user_id == user_id,
                    Receipt.user_visible == True
                )
            )

            if start_date:
                query = query.where(Receipt.timestamp >= start_date)
            if end_date:
                query = query.where(Receipt.timestamp <= end_date)

            result = await self.db.execute(query)
            receipts = result.scalars().all()

            # Calculate statistics
            stats = {
                "total_receipts": len(receipts),
                "by_type": {},
                "by_entity": {},
                "by_privacy_impact": {},
                "by_persona_mode": {}
            }

            for receipt in receipts:
                # Count by type
                type_key = receipt.receipt_type.value if receipt.receipt_type else "unknown"
                stats["by_type"][type_key] = stats["by_type"].get(type_key, 0) + 1

                # Count by entity type
                if receipt.entity_type:
                    stats["by_entity"][receipt.entity_type] = \
                        stats["by_entity"].get(receipt.entity_type, 0) + 1

                # Count by privacy impact
                if receipt.privacy_impact:
                    stats["by_privacy_impact"][receipt.privacy_impact] = \
                        stats["by_privacy_impact"].get(receipt.privacy_impact, 0) + 1

                # Count by persona mode
                if receipt.persona_mode:
                    stats["by_persona_mode"][receipt.persona_mode] = \
                        stats["by_persona_mode"].get(receipt.persona_mode, 0) + 1

            return stats

        except Exception as e:
            logger.error(f"Error getting receipt stats: {e}")
            raise

    async def verify_receipt(self, receipt: Receipt) -> bool:
        """Verify the cryptographic integrity of a receipt.

        Recalculates the content hash and compares it to the stored hash.

        Args:
            receipt: Receipt to verify

        Returns:
            True if receipt is valid, False otherwise
        """
        try:
            if not receipt.content_hash:
                logger.warning(f"Receipt {receipt.id} has no content hash")
                return False

            # Reconstruct receipt data for hashing
            receipt_data = {
                'id': receipt.id,
                'user_id': receipt.user_id,
                'receipt_type': receipt.receipt_type,
                'timestamp': receipt.timestamp,
                'action': receipt.action,
                'entity_type': receipt.entity_type,
                'entity_id': receipt.entity_id,
                'context': receipt.context,
                'request_data': receipt.request_data,
                'response_data': receipt.response_data,
                'persona_mode': receipt.persona_mode,
                'worldview_profile': receipt.worldview_profile,
                'decisions_made': receipt.decisions_made,
                'confidence_score': receipt.confidence_score,
                'alternatives_considered': receipt.alternatives_considered,
                'consent_basis': receipt.consent_basis,
                'data_categories': receipt.data_categories,
                'privacy_impact': receipt.privacy_impact,
                'user_visible': receipt.user_visible,
                'explanation': receipt.explanation,
                'service_name': receipt.service_name,
                'service_version': receipt.service_version,
                'correlation_id': receipt.correlation_id,
                'parent_receipt_id': receipt.parent_receipt_id,
                'ip_address': receipt.ip_address,
                'user_agent': receipt.user_agent,
                'session_id': receipt.session_id,
                'previous_hash': receipt.previous_hash
            }

            # Calculate hash and compare
            calculated_hash = self._calculate_content_hash(receipt_data)
            is_valid = calculated_hash == receipt.content_hash

            if not is_valid:
                logger.error(f"Receipt {receipt.id} hash mismatch. Expected: {receipt.content_hash}, Got: {calculated_hash}")
                # Debug: print normalized data for troubleshooting
                import json as json_module
                logger.debug(f"Receipt data for hash: {json_module.dumps(receipt_data, sort_keys=True, separators=(',', ':'), default=str)[:500]}")

            return is_valid

        except Exception as e:
            logger.error(f"Error verifying receipt {receipt.id}: {e}")
            return False

    async def verify_receipt_chain(
        self,
        user_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Verify the integrity of a user's receipt chain.

        Checks that:
        1. Each receipt's content hash is valid
        2. Each receipt's previous_hash matches the prior receipt's content_hash

        Args:
            user_id: User ID
            start_date: Optional start date
            end_date: Optional end date

        Returns:
            Dictionary with verification results
        """
        try:
            # Get receipts in chronological order
            query = select(Receipt).where(Receipt.user_id == user_id)

            if start_date:
                query = query.where(Receipt.timestamp >= start_date)
            if end_date:
                query = query.where(Receipt.timestamp <= end_date)

            query = query.order_by(Receipt.timestamp.asc())

            result = await self.db.execute(query)
            receipts = result.scalars().all()

            if not receipts:
                return {
                    "valid": True,
                    "total_receipts": 0,
                    "verified_receipts": 0,
                    "invalid_receipts": [],
                    "chain_breaks": []
                }

            verified = 0
            invalid_receipts = []
            chain_breaks = []
            previous_hash = None

            for i, receipt in enumerate(receipts):
                # Verify content hash
                if not await self.verify_receipt(receipt):
                    invalid_receipts.append({
                        "receipt_id": str(receipt.id),
                        "timestamp": receipt.timestamp.isoformat(),
                        "reason": "Content hash verification failed"
                    })
                else:
                    verified += 1

                # Verify chain linkage (skip first receipt)
                if i > 0:
                    if receipt.previous_hash != previous_hash:
                        chain_breaks.append({
                            "receipt_id": str(receipt.id),
                            "timestamp": receipt.timestamp.isoformat(),
                            "expected_previous_hash": previous_hash,
                            "actual_previous_hash": receipt.previous_hash
                        })

                previous_hash = receipt.content_hash

            is_valid = len(invalid_receipts) == 0 and len(chain_breaks) == 0

            return {
                "valid": is_valid,
                "total_receipts": len(receipts),
                "verified_receipts": verified,
                "invalid_receipts": invalid_receipts,
                "chain_breaks": chain_breaks
            }

        except Exception as e:
            logger.error(f"Error verifying receipt chain: {e}")
            raise