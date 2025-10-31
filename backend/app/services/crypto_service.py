"""
Cryptographic Service

Handles Ed25519 signature verification and system-level cryptographic operations.
Client-side key generation happens in the frontend - server never sees private keys.
"""

import logging
import base64
from typing import Optional
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature

logger = logging.getLogger(__name__)


class CryptoService:
    """Service for cryptographic operations."""

    @staticmethod
    def verify_ed25519_signature(
        public_key_b64: str,
        message: str,
        signature_b64: str
    ) -> bool:
        """
        Verify an Ed25519 signature.

        Args:
            public_key_b64: Base64-encoded public key (32 bytes)
            message: The message that was signed (UTF-8 string)
            signature_b64: Base64-encoded signature (64 bytes)

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Decode from base64
            public_key_bytes = base64.b64decode(public_key_b64)
            signature_bytes = base64.b64decode(signature_b64)
            message_bytes = message.encode('utf-8')

            # Validate lengths
            if len(public_key_bytes) != 32:
                logger.warning(f"Invalid public key length: {len(public_key_bytes)} (expected 32)")
                return False

            if len(signature_bytes) != 64:
                logger.warning(f"Invalid signature length: {len(signature_bytes)} (expected 64)")
                return False

            # Create public key object
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)

            # Verify signature (raises InvalidSignature if verification fails)
            public_key.verify(signature_bytes, message_bytes)

            logger.debug("Signature verification successful")
            return True

        except InvalidSignature:
            logger.warning("Signature verification failed: invalid signature")
            return False

        except ValueError as e:
            logger.warning(f"Signature verification failed: {e}")
            return False

        except Exception as e:
            logger.error(f"Signature verification error: {e}", exc_info=True)
            return False

    @staticmethod
    def generate_system_signature(
        data: str,
        system_private_key_b64: Optional[str] = None
    ) -> str:
        """
        Generate a signature using the system's private key.

        This is used for system-generated receipts and internal operations.
        User signatures are generated client-side.

        Args:
            data: The data to sign
            system_private_key_b64: Base64-encoded system private key (32 bytes)
                                   If None, loads from environment/config

        Returns:
            Base64-encoded signature (64 bytes)

        Raises:
            ValueError: If system key not configured
        """
        if system_private_key_b64 is None:
            # In production, load from secure storage (HashiCorp Vault, AWS Secrets Manager, etc.)
            # For now, this is a placeholder
            raise ValueError(
                "System private key not configured. "
                "Set SYSTEM_SIGNING_KEY environment variable."
            )

        try:
            # Decode private key
            private_key_bytes = base64.b64decode(system_private_key_b64)

            if len(private_key_bytes) != 32:
                raise ValueError(f"Invalid private key length: {len(private_key_bytes)} (expected 32)")

            # Create private key object
            private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)

            # Sign data
            message_bytes = data.encode('utf-8')
            signature_bytes = private_key.sign(message_bytes)

            # Return base64-encoded signature
            return base64.b64encode(signature_bytes).decode('utf-8')

        except Exception as e:
            logger.error(f"System signature generation failed: {e}", exc_info=True)
            raise

    @staticmethod
    def verify_signature_chain(
        signatures: list[dict],
        public_keys: dict[str, str]
    ) -> bool:
        """
        Verify a chain of signatures (for receipt chains or multi-party agreements).

        Args:
            signatures: List of signature dicts with {user_id, message, signature}
            public_keys: Dict mapping user_id to public_key_b64

        Returns:
            True if all signatures in chain are valid, False otherwise
        """
        try:
            for sig_data in signatures:
                user_id = sig_data['user_id']
                message = sig_data['message']
                signature = sig_data['signature']

                if user_id not in public_keys:
                    logger.warning(f"Public key not found for user {user_id}")
                    return False

                public_key = public_keys[user_id]

                if not CryptoService.verify_ed25519_signature(public_key, message, signature):
                    logger.warning(f"Signature verification failed for user {user_id}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Signature chain verification error: {e}", exc_info=True)
            return False
