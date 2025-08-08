# Mnemosyne Research Critical Review — Batch 8

Scope: Findings for two research files—`docs/research/consensus_coordination_mechanisms.md` and `docs/research/quorum_dynamics.md`—with cross-document flags from `docs/research/protocol_comparison.md`. Does not modify source research files.

Date: 2025-08-08

---

## Reviewed Documents
- `docs/research/consensus_coordination_mechanisms.md`
- `docs/research/quorum_dynamics.md`
- Cross-file references: `docs/research/protocol_comparison.md`

---

## Batch 8 Findings

### 1) consensus_coordination_mechanisms.md

- __Strengths__
  - Clear separation of operations by consistency needs (critical vs eventual vs local).
  - Pragmatic "CRDT-first; BFT for critical paths" strategy.
  - Mentions HoneyBadger-style asynchronous consensus and Merkle-authenticated CRDTs.
  - Awareness of batching/pipelining and leader-election considerations.

- __Gaps/Risks__
  - __Fault thresholds__: Make n ≥ 3f + 1 explicit; note RBC/ABA typically O(n^2) messages.
  - __Asynchrony trade-offs__: HoneyBadger/ABA avoids timing assumptions but increases latency and crypto overhead.
  - __Threshold crypto posture__: Examples (BLS, Paillier) are not PQ by default; PQ threshold options are heavy/immature.
  - __Nullifier registration__: If double-spend prevention matters, eventual CRDTs alone are insufficient—require BFT finality or an external anchoring root.

- __Recommendations__
  - Prefer HotStuff/Tendermint lineage for production BFT (simpler view change, pipelining) over classic PBFT.
  - Specify operational envelopes: n, f, commit latency targets, partial-synchrony bounds, batch size/timeouts, and state-transfer costs.
  - Document current non-PQ threshold components; define a PQ roadmap or hybrid mitigations (auditable logs, transparency overlays).
  - Add authenticated gossip/anti-entropy details for Merkle-CRDT state sync.

- __Validation Hooks__
  - Throughput/commit latency across n ∈ {4, 16, 64, 256}; P50/P90/P99 latencies; batch size sweep.
  - Fault injection: equivocation, censorship, partitions; verify safety always; liveness under assumed bounds.
  - Churn tests: leader changes, DKG/resharing timings, state-transfer metrics.
  - Resource budgets: CPU/memory/network per replica; signature/verify costs; PQ variants’ size/latency deltas.

---

### 2) quorum_dynamics.md

- __Strengths__
  - Multi-scale quorum framing (micro/meso/macro/mega) with resonance-driven clustering.
  - Appropriate use of hierarchy/delegation; broad survey (Byzantine, swarm, liquid democracy, stigmergy).

- __Gaps/Risks__
  - __Parameters__: Constants like “critical mass 10%,” “phase transition 0.67,” “min_resonance 0.7,” “max_size 150” appear illustrative—avoid normative claims without calibration.
  - __Swarm/heuristic methods__: Useful for ideation/prioritization, not for safety/finality—avoid using for critical consensus.
  - __Weighted quorums__: Stake/reputation weighting risks centralization and sybil capture; add sybil resistance and fairness constraints.
  - __Security posture__: Threshold/consensus primitives referenced are typically non-PQ; mark posture and roadmap.

- __Recommendations__
  - Treat thresholds/resonance cutoffs as tunable; calibrate on real datasets; publish sensitivity analyses.
  - Reserve Byzantine consensus for critical decisions; scope swarm methods to low-stakes coordination.
  - Add fairness metrics (representation parity, influence Gini) and sybil resistance for weighted designs.

- __Validation Hooks__
  - Quorum formation quality: community-detection agreement, stability over time, decision quality.
  - Fairness audits across demographics; sybil-attack simulations and robustness curves.
  - For Byzantine phases: reuse consensus validation (commit latency, safety under faults, view-change performance).

---

## Cross-Document Flagged Claims (from protocol_comparison.md)

- __MLS group size and DS assumptions__
  - Replace “2–50,000 members” with: “Scales to large groups; provide implementation+Delivery Service (DS) benchmarks.”
  - Clarify that MLS commonly relies on a DS for asynchronous delivery/ordering; scope O(log n) to tree operations.

- __STARK performance numbers require context__
  - Bind prover/verify figures to: circuit (hash/function/cost), prover hardware (cores/RAM/cache), hash choice, and device class (desktop/mobile/server).
  - PQ posture: hash-based assumptions only; state this explicitly, not as a formal quantum security proof.

- __Verkle “constant-size” proof claims__
  - Clarify that end-to-end path proofs aggregate openings across nodes (typically hundreds of bytes), require KZG/trusted setup, and are not PQ by default.

- __RSA accumulators__
  - Non-PQ; call out trusted modulus generation and dynamic-witness update complexity.

---

## Implementation Guidance (near-term)

- __Consensus Layer__
  - Adopt HotStuff/Tendermint-style BFT for critical paths with explicit n, f, latency, and batching envelopes.
  - Publish RBC/ABA complexity notes; document state transfer and view-change behavior.
  - Track PQ posture for threshold primitives; define mitigation plan or roadmap.

- __Quorum Design__
  - Parameterize thresholds; calibrate via data; include fairness and sybil-resistance constraints.
  - Limit swarm/heuristics to non-critical phases; use BFT for finalization.

- __Messaging + Membership__
  - MLS: cite implementation/DS benchmarks; add application-layer metadata protections.
  - Membership: PQ-safe baseline using Sparse Merkle (Keccak-256/SHA-256) with multiproofs; evaluate Verkle/IPA in Phase 2 while keeping Merkle fallback.

- __ZK Stack__
  - For each target circuit (Merkle-path, set membership, small arithmetic), report proof size and prove/verify time across CPU classes; account for mobile feasibility.

---

## Metrics & Benchmarks to Run

- __Consensus/BFT__
  - n ∈ {4, 16, 64, 256}; throughput and P50/P90/P99 commit latency under fault/churn; resource budgets; PQ variant overheads.

- __MLS__
  - Implementation (e.g., OpenMLS) + DS emulator; measure join/leave/commit latency, client memory, throughput, out-of-order recovery.

- __Membership Proofs__
  - Sparse Merkle multiproofs vs Verkle/IPA at n ∈ {1e4, 1e6}; proof size, verify time, ZK circuit constraints; batch update costs.

- __ZK/STARK__
  - Circuit-bound evaluations with explicit hardware; proof sizes and times for desktop, server, and mobile.

---

## Next Small-Batch Queue (proposal)
1. `docs/research/final/FINAL_REPORT.md`
2. `docs/research/final/ROADMAP_INTEGRATION.md`

Each batch will add a new section to the consolidated document after review; this Batch 8 file serves as a standalone, citable record.
