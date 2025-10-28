#!/usr/bin/env python3
"""
Direct test of cryptographic receipt functionality

This script tests the ReceiptService directly to verify hash generation.
"""

import asyncio
import sys
from uuid import uuid4
from app.db.session import SessionLocal, get_async_db
from app.services.receipt_service import ReceiptService
from app.db.models.receipt import ReceiptType


async def test_receipt_crypto():
    """Test receipt cryptographic functionality directly."""

    print("=" * 60)
    print("DIRECT RECEIPT CRYPTOGRAPHY TEST")
    print("=" * 60)

    # Create async session
    async for db in get_async_db():
        service = ReceiptService(db)
        # Use existing user ID from database
        from uuid import UUID
        test_user_id = UUID("baf1eeca-1e9f-453c-8e74-31dbbfe26631")

        print(f"\nTest User ID: {test_user_id}")

        # Create first receipt
        print("\n1. Creating first receipt...")
        receipt1 = await service.create_receipt(
            user_id=test_user_id,
            receipt_type=ReceiptType.MEMORY_CREATE,
            action="Test memory creation",
            entity_type="memory",
            entity_id=uuid4(),
            context={"test": "data"},
            explanation="Testing cryptographic hashing"
        )

        print(f"   Receipt ID: {receipt1.id}")
        print(f"   Content Hash: {receipt1.content_hash}")
        print(f"   Previous Hash: {receipt1.previous_hash}")

        if receipt1.content_hash:
            print("   ✅ Content hash generated!")
            print(f"   Hash length: {len(receipt1.content_hash)} (should be 64 for SHA-256)")
        else:
            print("   ❌ FAILED: No content hash!")
            return False

        if receipt1.previous_hash is None:
            print("   ✅ Previous hash is None (first receipt)")

        # Verify first receipt
        print("\n2. Verifying first receipt...")
        is_valid = await service.verify_receipt(receipt1)
        if is_valid:
            print("   ✅ Receipt verification PASSED")
        else:
            print("   ❌ Receipt verification FAILED")
            return False

        # Create second receipt
        print("\n3. Creating second receipt (to test chaining)...")
        receipt2 = await service.create_receipt(
            user_id=test_user_id,
            receipt_type=ReceiptType.MEMORY_UPDATE,
            action="Test memory update",
            entity_type="memory",
            entity_id=uuid4(),
            context={"test": "data2"},
            explanation="Testing receipt chaining"
        )

        print(f"   Receipt ID: {receipt2.id}")
        print(f"   Content Hash: {receipt2.content_hash}")
        print(f"   Previous Hash: {receipt2.previous_hash}")

        if receipt2.content_hash:
            print("   ✅ Content hash generated!")
        else:
            print("   ❌ FAILED: No content hash!")
            return False

        if receipt2.previous_hash == receipt1.content_hash:
            print("   ✅ Receipt chain linked correctly!")
            print(f"   Chain: {receipt1.content_hash[:16]}... → {receipt2.content_hash[:16]}...")
        else:
            print("   ❌ FAILED: Chain link broken!")
            print(f"   Expected previous: {receipt1.content_hash}")
            print(f"   Got previous: {receipt2.previous_hash}")
            return False

        # Verify second receipt
        print("\n4. Verifying second receipt...")
        is_valid = await service.verify_receipt(receipt2)
        if is_valid:
            print("   ✅ Receipt verification PASSED")
        else:
            print("   ❌ Receipt verification FAILED")
            return False

        # Verify chain
        print("\n5. Verifying entire receipt chain...")
        chain_result = await service.verify_receipt_chain(user_id=test_user_id)

        print(f"   Total receipts: {chain_result['total_receipts']}")
        print(f"   Verified: {chain_result['verified_receipts']}")
        print(f"   Invalid: {len(chain_result['invalid_receipts'])}")
        print(f"   Chain breaks: {len(chain_result['chain_breaks'])}")

        if chain_result['valid']:
            print("   ✅ Chain verification PASSED")
        else:
            print("   ❌ Chain verification FAILED")
            if chain_result['invalid_receipts']:
                print(f"   Invalid receipts: {chain_result['invalid_receipts']}")
            if chain_result['chain_breaks']:
                print(f"   Chain breaks: {chain_result['chain_breaks']}")
            return False

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        print("\n✅ Cryptographic integrity is working:")
        print("   - SHA-256 content hashing: WORKING")
        print("   - Receipt chaining: WORKING")
        print("   - Single receipt verification: WORKING")
        print("   - Chain verification: WORKING")

        return True


if __name__ == "__main__":
    import sys
    sys.path.insert(0, '/app')

    result = asyncio.run(test_receipt_crypto())
    sys.exit(0 if result else 1)
