# Mnemosyne Instance Routing & Discovery Protocol
*Decentralized Discovery for Sovereign Trust Networks*

## Overview

This protocol enables Mnemosyne instances to discover and route messages to each other without central directories or mandatory participation in a global network. Instances can choose to be completely isolated, selectively connected, or fully networked.

## Design Principles

1. **Sovereignty First** - Instances control their own visibility
2. **No Mandatory Participation** - Can run completely isolated
3. **Trust-Based Routing** - Routes through trusted connections
4. **Privacy Preserving** - Minimal information leakage
5. **Resilient** - Multiple discovery mechanisms

## Architecture

### Network Topology Options

```
Isolated Instance:
    [Instance A]  (No connections)

Direct Peering:
    [Instance A] <---> [Instance B]

Trust Cells (Small Groups):
    [A] <---> [B]
     ^         ^
     |         |
     v         v
    [C] <---> [D]

Federated Networks:
    Cell 1          Cell 2
    [A]--[B]        [E]--[F]
     |    |          |    |
    [C]--[D]   <->  [G]--[H]

Full Mesh (Rare):
    Every instance connected to many others
```

## Discovery Mechanisms

### 1. Direct Exchange (Bootstrap)

The simplest and most secure method - direct exchange of instance information:

```python
class DirectExchange:
    """Direct exchange of instance information."""

    def generate_instance_card(self,
                               instance_id: str,
                               icv_hash: str,
                               endpoints: List[str]) -> dict:
        """
        Generate a shareable instance card.

        Like a business card for your Mnemosyne instance.
        """
        card = {
            "version": "1.0",
            "instance": {
                "id": instance_id,
                "icv_hash": icv_hash,
                "name": "Optional Human Name",
                "description": "Optional Description"
            },
            "endpoints": [
                {
                    "type": "https",
                    "url": "https://alice.mnemosyne.local",
                    "priority": 1
                },
                {
                    "type": "tor",
                    "url": "mnemosyne7x3....onion",
                    "priority": 2
                }
            ],
            "capabilities": [
                "negotiation/1.0",
                "trust/1.0",
                "appeals/1.0"
            ],
            "public_key": "base64_encoded_ed25519",
            "valid_until": "2025-12-31T23:59:59Z"
        }

        # Sign the card
        signature = sign_message(card, private_key)
        card["signature"] = signature

        return card

    def encode_as_qr(self, card: dict) -> str:
        """Encode instance card as QR code for in-person exchange."""
        compressed = zlib.compress(json.dumps(card).encode())
        return base64.b64encode(compressed).decode()

    def import_instance_card(self, card: dict) -> bool:
        """Import and verify an instance card."""
        # Verify signature
        if not verify_signature(card, card["signature"], card["public_key"]):
            return False

        # Check expiry
        if datetime.fromisoformat(card["valid_until"]) < datetime.utcnow():
            return False

        # Store in local routing table
        self.routing_table.add_instance(card)

        return True
```

### 2. Friend-of-Friend Introduction

Discover instances through mutual connections:

```python
class FriendOfFriendDiscovery:
    """Discovery through trusted intermediaries."""

    async def request_introductions(self,
                                   trusted_instance: str,
                                   criteria: dict = None) -> List[dict]:
        """
        Ask a trusted instance for introductions to their connections.
        """
        request = {
            "type": "introduction_request",
            "from": self.instance_id,
            "criteria": criteria or {},  # e.g., {"capabilities": ["negotiation/1.0"]}
            "max_introductions": 5,
            "include_trust_scores": True,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Sign request
        signature = sign_message(request, self.private_key)
        request["signature"] = signature

        # Send to trusted instance
        response = await self.send_message(trusted_instance, request)

        # Process introductions
        introductions = []
        for intro in response.get("introductions", []):
            if self.verify_introduction(intro, trusted_instance):
                introductions.append(intro)

        return introductions

    def verify_introduction(self,
                           introduction: dict,
                           introducer: str) -> bool:
        """
        Verify an introduction from a trusted party.
        """
        # Check introducer's signature
        if not verify_signature(
            introduction,
            introduction["introducer_signature"],
            self.get_instance_key(introducer)
        ):
            return False

        # Check introduced party's signature
        if not verify_signature(
            introduction["instance_card"],
            introduction["instance_card"]["signature"],
            introduction["instance_card"]["public_key"]
        ):
            return False

        # Calculate transitive trust
        introducer_trust = self.trust_scores.get(introducer, 0.0)
        endorsed_trust = introduction.get("trust_score", 0.0)

        # Transitive trust degrades
        transitive_trust = introducer_trust * endorsed_trust * 0.7

        # Require minimum trust
        return transitive_trust >= 0.2

    async def introduce_instances(self,
                                 instance_a: str,
                                 instance_b: str) -> bool:
        """
        Introduce two instances you trust to each other.
        """
        # Get their instance cards
        card_a = self.routing_table.get_card(instance_a)
        card_b = self.routing_table.get_card(instance_b)

        # Create introduction for A -> B
        intro_a_to_b = {
            "type": "introduction",
            "introducer": self.instance_id,
            "introduced": instance_b,
            "instance_card": card_b,
            "trust_score": self.trust_scores.get(instance_b, 0.0),
            "context": "Mutual trusted connection",
            "timestamp": datetime.utcnow().isoformat()
        }

        # Sign introduction
        intro_a_to_b["introducer_signature"] = sign_message(
            intro_a_to_b,
            self.private_key
        )

        # Send to instance A
        await self.send_message(instance_a, intro_a_to_b)

        # Create symmetric introduction for B -> A
        intro_b_to_a = {
            "type": "introduction",
            "introducer": self.instance_id,
            "introduced": instance_a,
            "instance_card": card_a,
            "trust_score": self.trust_scores.get(instance_a, 0.0),
            "context": "Mutual trusted connection",
            "timestamp": datetime.utcnow().isoformat()
        }

        intro_b_to_a["introducer_signature"] = sign_message(
            intro_b_to_a,
            self.private_key
        )

        # Send to instance B
        await self.send_message(instance_b, intro_b_to_a)

        return True
```

### 3. DHT-Based Discovery (Optional)

For instances that want broader discoverability:

```python
class DHTDiscovery:
    """
    Distributed Hash Table for instance discovery.
    Based on Kademlia protocol.
    """

    def __init__(self, bootstrap_nodes: List[str] = None):
        self.node_id = generate_node_id(self.instance_id)
        self.routing_table = KBucketRoutingTable(self.node_id)
        self.storage = {}

        if bootstrap_nodes:
            self.bootstrap(bootstrap_nodes)

    def publish_instance(self,
                        visibility: str = "public",
                        attributes: dict = None) -> bool:
        """
        Publish instance to DHT with chosen visibility.
        """
        if visibility == "private":
            return False  # Don't publish

        # Create DHT entry
        entry = {
            "instance_id": self.instance_id,
            "icv_hash": self.icv_hash,
            "endpoints": self.public_endpoints,
            "attributes": attributes or {},
            "visibility": visibility,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Sign entry
        entry["signature"] = sign_message(entry, self.private_key)

        # Determine storage key
        if visibility == "public":
            # Store under instance ID
            key = hash(self.instance_id)
        elif visibility == "selective":
            # Store under attribute hash (discoverable by those who know attributes)
            key = hash(json.dumps(attributes, sort_keys=True))

        # Store in DHT
        return self.store(key, entry)

    async def find_instances(self,
                           criteria: dict,
                           max_results: int = 10) -> List[dict]:
        """
        Find instances matching criteria.
        """
        results = []

        # Search by different strategies
        if "instance_id" in criteria:
            # Direct lookup
            key = hash(criteria["instance_id"])
            entry = await self.get(key)
            if entry and self.verify_entry(entry):
                results.append(entry)

        elif "attributes" in criteria:
            # Attribute-based search
            key = hash(json.dumps(criteria["attributes"], sort_keys=True))
            entries = await self.get_all(key)
            for entry in entries:
                if self.verify_entry(entry):
                    results.append(entry)

        else:
            # Broad search (expensive, rate-limited)
            results = await self.search_dht(criteria, max_results)

        return results[:max_results]

    def verify_entry(self, entry: dict) -> bool:
        """Verify DHT entry integrity."""
        return verify_signature(
            entry,
            entry["signature"],
            self.get_public_key(entry["instance_id"])
        )
```

### 4. DNS-Based Hints (Optional)

For instances with domain names:

```python
class DNSDiscovery:
    """DNS TXT records for instance hints."""

    async def publish_dns_record(self, domain: str) -> bool:
        """
        Publish instance info as DNS TXT record.

        Example:
        _mnemosyne.alice.example.com IN TXT "v=mnem1 id=xxx endpoints=https://..."
        """
        txt_record = self.create_txt_record()

        # This would use DNS API of domain provider
        # Showing conceptual structure only
        return await dns_provider.set_txt_record(
            f"_mnemosyne.{domain}",
            txt_record
        )

    async def lookup_instance(self, domain: str) -> dict:
        """Look up instance via DNS."""
        import dns.resolver

        try:
            answers = dns.resolver.resolve(f"_mnemosyne.{domain}", "TXT")
            for rdata in answers:
                txt = str(rdata).strip('"')
                if txt.startswith("v=mnem1"):
                    return self.parse_txt_record(txt)
        except:
            pass

        return None
```

## Routing Protocol

### 1. Routing Table

Each instance maintains a routing table:

```python
class RoutingTable:
    """
    Local routing table for known instances.
    """

    def __init__(self):
        self.direct_peers = {}      # Directly connected instances
        self.indirect_peers = {}    # Reachable through others
        self.trust_scores = {}      # Trust level per instance
        self.last_seen = {}         # Last successful contact
        self.capabilities = {}      # What each instance supports

    def add_peer(self,
                instance_id: str,
                instance_card: dict,
                trust_score: float = 0.0,
                is_direct: bool = True):
        """Add or update peer in routing table."""

        peer_info = {
            "instance_id": instance_id,
            "icv_hash": instance_card["instance"]["icv_hash"],
            "endpoints": instance_card["endpoints"],
            "public_key": instance_card["public_key"],
            "capabilities": instance_card["capabilities"],
            "added": datetime.utcnow().isoformat()
        }

        if is_direct:
            self.direct_peers[instance_id] = peer_info
        else:
            self.indirect_peers[instance_id] = peer_info

        self.trust_scores[instance_id] = trust_score
        self.last_seen[instance_id] = datetime.utcnow()
        self.capabilities[instance_id] = set(instance_card["capabilities"])

    def find_route(self,
                  target_id: str,
                  max_hops: int = 6) -> List[str]:
        """
        Find route to target instance.

        Returns list of instance IDs representing the path.
        """
        # Check direct connection
        if target_id in self.direct_peers:
            return [self.instance_id, target_id]

        # Check indirect (known route)
        if target_id in self.indirect_peers:
            # We know someone who knows them
            intermediary = self.indirect_peers[target_id].get("via")
            if intermediary:
                return [self.instance_id, intermediary, target_id]

        # Use trust-weighted shortest path algorithm
        return self._find_trust_path(target_id, max_hops)

    def _find_trust_path(self,
                        target: str,
                        max_hops: int) -> List[str]:
        """
        Find path through trust network using modified Dijkstra's.
        """
        import heapq

        # Priority queue: (negative_trust_score, path)
        queue = [(-1.0, [self.instance_id])]
        visited = set()

        while queue:
            trust_score, path = heapq.heappop(queue)
            current = path[-1]

            if current == target:
                return path

            if current in visited or len(path) > max_hops:
                continue

            visited.add(current)

            # Get neighbors of current
            neighbors = self.get_neighbors(current)

            for neighbor in neighbors:
                if neighbor not in visited:
                    # Calculate path trust (product of edge trusts)
                    edge_trust = self.get_trust(current, neighbor)
                    path_trust = -trust_score * edge_trust * 0.9  # Decay

                    heapq.heappush(
                        queue,
                        (-path_trust, path + [neighbor])
                    )

        return []  # No path found
```

### 2. Message Routing

How messages are routed between instances:

```python
class MessageRouter:
    """Routes messages through the trust network."""

    async def send_message(self,
                         target_id: str,
                         message: dict,
                         routing_strategy: str = "trust_path") -> bool:
        """
        Send message to target instance.
        """
        # Find route
        if routing_strategy == "trust_path":
            route = self.routing_table.find_route(target_id)
        elif routing_strategy == "broadcast":
            route = ["broadcast"]
        elif routing_strategy == "direct_only":
            if target_id not in self.routing_table.direct_peers:
                return False
            route = [self.instance_id, target_id]
        else:
            raise ValueError(f"Unknown routing strategy: {routing_strategy}")

        if not route:
            return False

        # Create routable message
        routable_message = self.create_routable_message(
            message,
            route,
            target_id
        )

        # Send to next hop
        next_hop = route[1] if len(route) > 1 else route[0]
        return await self.send_to_instance(next_hop, routable_message)

    def create_routable_message(self,
                               payload: dict,
                               route: List[str],
                               final_destination: str) -> dict:
        """
        Create a routable message with onion-like encryption.
        """
        # For privacy, we can use onion routing
        # Simplified version shown here

        routable = {
            "version": "1.0",
            "type": "routable_message",
            "route": route,
            "current_hop": 0,
            "final_destination": final_destination,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Sign with our key
        routable["signatures"] = [
            sign_message(routable, self.private_key)
        ]

        return routable

    async def handle_routable_message(self, message: dict) -> bool:
        """
        Handle incoming routable message.
        """
        # Check if we're the destination
        if message["final_destination"] == self.instance_id:
            # Process the payload
            return await self.process_message(message["payload"])

        # We're an intermediary - forward it
        current_hop = message["current_hop"]
        route = message["route"]

        if current_hop >= len(route) - 1:
            # Route exhausted but not at destination
            return False

        # Forward to next hop
        message["current_hop"] += 1
        next_hop = route[current_hop + 1]

        # Add our signature (proof of handling)
        message["signatures"].append(
            sign_message(message, self.private_key)
        )

        return await self.send_to_instance(next_hop, message)
```

### 3. Gossip Protocol

For information propagation:

```python
class GossipProtocol:
    """
    Gossip protocol for information dissemination.
    """

    def __init__(self):
        self.seen_messages = set()  # Message IDs we've seen
        self.gossip_peers = []       # Peers we gossip with
        self.fanout = 3              # Number of peers to forward to

    async def gossip(self,
                    message: dict,
                    ttl: int = 3) -> None:
        """
        Spread message through gossip.
        """
        message_id = hash(json.dumps(message, sort_keys=True))

        # Check if we've seen this before
        if message_id in self.seen_messages:
            return

        self.seen_messages.add(message_id)

        # Decrease TTL
        ttl -= 1
        if ttl <= 0:
            return

        # Select random peers to gossip to
        import random
        selected_peers = random.sample(
            self.gossip_peers,
            min(self.fanout, len(self.gossip_peers))
        )

        # Forward to selected peers
        gossip_message = {
            "type": "gossip",
            "message": message,
            "ttl": ttl,
            "originator": message.get("originator", self.instance_id),
            "timestamp": datetime.utcnow().isoformat()
        }

        for peer in selected_peers:
            await self.send_to_instance(peer, gossip_message)

    async def handle_gossip(self, gossip_message: dict) -> None:
        """Handle incoming gossip."""
        # Process the message
        await self.process_message(gossip_message["message"])

        # Continue gossiping if TTL > 0
        if gossip_message["ttl"] > 0:
            await self.gossip(
                gossip_message["message"],
                gossip_message["ttl"]
            )
```

## Privacy Considerations

### 1. Selective Disclosure

Instances control what information they share:

```python
class PrivacyControls:
    """Privacy controls for discovery and routing."""

    def __init__(self):
        self.visibility_levels = {
            "hidden": [],           # Not discoverable
            "direct": [],           # Only direct contact
            "friends": [],          # Friends of friends
            "network": [],          # Entire trust network
            "public": []            # Globally discoverable
        }

    def set_visibility(self,
                      attribute: str,
                      level: str) -> None:
        """Set visibility level for an attribute."""
        self.visibility_levels[level].append(attribute)

    def get_discoverable_info(self,
                             requester_trust: float) -> dict:
        """Get information visible to requester based on trust."""
        info = {}

        # Determine what to share based on trust
        if requester_trust >= 0.7:
            # High trust - share network level
            info.update(self._get_attributes("network"))
        elif requester_trust >= 0.3:
            # Medium trust - share friends level
            info.update(self._get_attributes("friends"))
        elif requester_trust > 0:
            # Low trust - share direct level only
            info.update(self._get_attributes("direct"))
        # No trust - share nothing (hidden)

        return info
```

### 2. Anonymous Routing

Optional Tor-like routing for privacy:

```python
class AnonymousRouting:
    """Anonymous routing through the network."""

    def create_anonymous_route(self,
                              destination: str,
                              min_hops: int = 3) -> List[str]:
        """Create anonymous route with random intermediaries."""
        import random

        # Get possible intermediaries (trusted peers)
        candidates = [
            peer for peer, trust in self.trust_scores.items()
            if trust >= 0.5 and peer != destination
        ]

        # Select random intermediaries
        num_hops = random.randint(min_hops, min_hops + 2)
        intermediaries = random.sample(
            candidates,
            min(num_hops, len(candidates))
        )

        # Build route
        route = [self.instance_id] + intermediaries + [destination]

        return route
```

## Implementation Status

### Phase 1: Basic Discovery (Q1 2025)
- [ ] Direct instance card exchange
- [ ] QR code generation/scanning
- [ ] Basic routing table
- [ ] HTTP message passing

### Phase 2: Trust-Based Routing (Q2 2025)
- [ ] Friend-of-friend discovery
- [ ] Trust path calculation
- [ ] Message routing through network
- [ ] Gossip protocol

### Phase 3: Advanced Features (Q3 2025)
- [ ] DHT integration
- [ ] Anonymous routing
- [ ] DNS hints
- [ ] Onion routing

### Phase 4: Optimization (Q4 2025)
- [ ] Route caching
- [ ] Peer reputation
- [ ] Network topology optimization
- [ ] Byzantine fault tolerance

## Conclusion

This routing and discovery protocol enables Mnemosyne instances to form sovereign trust networks while maintaining complete control over their visibility and connections. The multi-mechanism approach ensures resilience while the trust-based routing provides Sybil resistance.

The protocol supports everything from completely isolated instances to large federated networks, always respecting instance sovereignty and user choice.

---

*"The best network is one you choose to join, not one you're forced into."*