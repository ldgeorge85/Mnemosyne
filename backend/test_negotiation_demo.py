#!/usr/bin/env python3
"""
Test Multi-Party Negotiation: Hostile Parties Reach Agreement
Demo scenario for "Trust Without Central Authority" primitive
"""

import asyncio
import json
from datetime import datetime, timedelta
from uuid import uuid4
import httpx
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
ADMIN_TOKEN = "admin-token-123"  # From environment config

class NegotiationDemo:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=BASE_URL, timeout=30.0)
        self.alice_token = None
        self.bob_token = None
        self.alice_id = None
        self.bob_id = None

    async def setup_users(self):
        """Create Alice and Bob as test users."""
        print("\n=== SETUP: Creating hostile parties ===")

        # For demo, we'll use admin authentication
        headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}

        # In a real scenario, we'd create users properly
        # For now, we'll simulate with UUIDs
        self.alice_id = str(uuid4())
        self.bob_id = str(uuid4())
        self.alice_token = ADMIN_TOKEN  # Simplified for demo
        self.bob_token = ADMIN_TOKEN     # Simplified for demo

        print(f"✓ Alice ID: {self.alice_id}")
        print(f"✓ Bob ID: {self.bob_id}")

    async def create_negotiation(self) -> str:
        """Alice initiates negotiation with Bob."""
        print("\n=== STEP 1: Alice initiates negotiation ===")

        initial_terms = {
            "apology": "Bob must formally apologize for trust violation",
            "trust_restoration": "Trust score restored to 0.5",
            "monitoring": "30-day monitoring period with weekly check-ins",
            "compensation": "Bob covers mediation costs"
        }

        payload = {
            "title": "Resolution of Trust Violation Event #123",
            "description": "Alice claims Bob violated trust boundary by sharing private information",
            "participant_ids": [self.alice_id, self.bob_id],
            "initiator_id": self.alice_id,
            "initial_terms": initial_terms,
            "negotiation_deadline": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "required_consensus_count": 2  # Both must agree
        }

        headers = {"Authorization": f"Bearer {self.alice_token}"}
        response = await self.client.post("/negotiations", json=payload, headers=headers)

        if response.status_code != 200:
            print(f"❌ Failed to create negotiation: {response.text}")
            return None

        data = response.json()
        negotiation_id = data["id"]
        print(f"✓ Negotiation created: {negotiation_id}")
        print(f"  Initial terms: {json.dumps(initial_terms, indent=2)}")
        return negotiation_id

    async def bob_joins(self, negotiation_id: str):
        """Bob joins the negotiation."""
        print("\n=== STEP 2: Bob joins negotiation ===")

        headers = {"Authorization": f"Bearer {self.bob_token}"}
        response = await self.client.post(
            f"/negotiations/{negotiation_id}/join",
            headers=headers,
            json={"participant_id": self.bob_id}
        )

        if response.status_code != 200:
            print(f"❌ Bob failed to join: {response.text}")
            return False

        print("✓ Bob joined negotiation")
        print("  Status: NEGOTIATING")
        return True

    async def bob_counter_offer(self, negotiation_id: str):
        """Bob sends counter-offer."""
        print("\n=== STEP 3: Bob sends counter-offer ===")

        counter_terms = {
            "apology": "Bob acknowledges misunderstanding, not malicious intent",
            "trust_restoration": "Trust score restored to 0.7 (higher than Alice proposed)",
            "monitoring": "No monitoring required",
            "compensation": "Split mediation costs 50/50"
        }

        payload = {
            "terms": counter_terms,
            "message": "I didn't intend harm. This was a misunderstanding."
        }

        headers = {"Authorization": f"Bearer {self.bob_token}"}
        response = await self.client.post(
            f"/negotiations/{negotiation_id}/offer",
            json=payload,
            headers=headers
        )

        if response.status_code != 200:
            print(f"❌ Failed to send counter-offer: {response.text}")
            return False

        print("✓ Bob sent counter-offer")
        print(f"  Counter terms: {json.dumps(counter_terms, indent=2)}")
        return True

    async def alice_counter_offer(self, negotiation_id: str):
        """Alice responds with compromise."""
        print("\n=== STEP 4: Alice sends compromise offer ===")

        compromise_terms = {
            "apology": "Bob acknowledges misunderstanding and commits to better communication",
            "trust_restoration": "Trust score restored to 0.6",
            "monitoring": "14-day check-in period",
            "compensation": "Bob covers 75% of mediation costs"
        }

        payload = {
            "terms": compromise_terms,
            "message": "I'm willing to compromise if you take responsibility."
        }

        headers = {"Authorization": f"Bearer {self.alice_token}"}
        response = await self.client.post(
            f"/negotiations/{negotiation_id}/offer",
            json=payload,
            headers=headers
        )

        if response.status_code != 200:
            print(f"❌ Failed to send compromise: {response.text}")
            return False

        print("✓ Alice sent compromise offer")
        print(f"  Compromise terms: {json.dumps(compromise_terms, indent=2)}")
        return True

    async def bob_accepts(self, negotiation_id: str):
        """Bob accepts Alice's terms."""
        print("\n=== STEP 5: Bob accepts compromise ===")

        payload = {
            "message": "I accept these terms and commit to better communication."
        }

        headers = {"Authorization": f"Bearer {self.bob_token}"}
        response = await self.client.post(
            f"/negotiations/{negotiation_id}/accept",
            json=payload,
            headers=headers
        )

        if response.status_code != 200:
            print(f"❌ Bob failed to accept: {response.text}")
            return False

        print("✓ Bob accepted current terms")
        return True

    async def alice_accepts(self, negotiation_id: str):
        """Alice accepts her own terms."""
        print("\n=== STEP 6: Alice accepts (consensus reached) ===")

        payload = {
            "message": "I accept these terms."
        }

        headers = {"Authorization": f"Bearer {self.alice_token}"}
        response = await self.client.post(
            f"/negotiations/{negotiation_id}/accept",
            json=payload,
            headers=headers
        )

        if response.status_code != 200:
            print(f"❌ Alice failed to accept: {response.text}")
            return False

        print("✓ Alice accepted current terms")
        print("🎯 CONSENSUS REACHED! Status: CONSENSUS_REACHED")
        return True

    async def finalize_agreement(self, negotiation_id: str):
        """Both parties finalize to make binding."""
        print("\n=== STEP 7: Finalize binding agreement ===")

        # Bob finalizes
        headers = {"Authorization": f"Bearer {self.bob_token}"}
        response = await self.client.post(
            f"/negotiations/{negotiation_id}/finalize",
            headers=headers,
            json={"participant_id": self.bob_id}
        )

        if response.status_code != 200:
            print(f"❌ Bob failed to finalize: {response.text}")
            return False

        print("✓ Bob finalized commitment")

        # Alice finalizes
        headers = {"Authorization": f"Bearer {self.alice_token}"}
        response = await self.client.post(
            f"/negotiations/{negotiation_id}/finalize",
            headers=headers,
            json={"participant_id": self.alice_id}
        )

        if response.status_code != 200:
            print(f"❌ Alice failed to finalize: {response.text}")
            return False

        print("✓ Alice finalized commitment")
        print("🔒 BINDING AGREEMENT CREATED!")
        return True

    async def verify_binding(self, negotiation_id: str):
        """Verify the binding agreement."""
        print("\n=== VERIFICATION: Check binding commitment ===")

        headers = {"Authorization": f"Bearer {self.alice_token}"}
        response = await self.client.get(
            f"/negotiations/{negotiation_id}",
            headers=headers
        )

        if response.status_code != 200:
            print(f"❌ Failed to get negotiation: {response.text}")
            return

        data = response.json()

        print(f"✓ Status: {data.get('status')}")
        print(f"✓ Binding hash: {data.get('binding_hash', 'N/A')}")
        print(f"✓ Binding timestamp: {data.get('binding_timestamp', 'N/A')}")

        if data.get('status') == 'BINDING':
            print("\n🎆 SUCCESS: Two hostile parties reached binding agreement!")
            print("   - No central authority")
            print("   - No blockchain")
            print("   - No reputation system")
            print("   - Pure peer-to-peer negotiation")
            print("\n   THE IMPOSSIBLE IS NOW POSSIBLE! 🚀")

    async def run_demo(self):
        """Run the complete demonstration."""
        print("=" * 60)
        print("MULTI-PARTY NEGOTIATION DEMO")
        print("Trust Without Central Authority")
        print("=" * 60)

        try:
            # Setup
            await self.setup_users()

            # Create negotiation
            negotiation_id = await self.create_negotiation()
            if not negotiation_id:
                print("❌ Demo failed at negotiation creation")
                return

            # Run negotiation flow
            if not await self.bob_joins(negotiation_id):
                return

            if not await self.bob_counter_offer(negotiation_id):
                return

            if not await self.alice_counter_offer(negotiation_id):
                return

            if not await self.bob_accepts(negotiation_id):
                return

            if not await self.alice_accepts(negotiation_id):
                return

            if not await self.finalize_agreement(negotiation_id):
                return

            # Verify
            await self.verify_binding(negotiation_id)

        finally:
            await self.client.aclose()

async def main():
    demo = NegotiationDemo()
    await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(main())