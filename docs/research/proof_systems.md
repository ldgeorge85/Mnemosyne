# Mnemosyne Proof Systems: SNARK vs STARK & Integration Plan

## 0) Executive Summary

This artifact defines (1) the practical differences between ZK‑SNARKs and ZK‑STARKs, (2) concrete selection criteria for Mnemosyne, and (3) a pluggable proof layer design that slots into the Mnemosyne Engine, Deep Signal Protocol (identity), and Quiet Network (peer/trust layer). TL;DR:

* Short term: use a **universal‑setup SNARK** (PLONK/Halo2) for compact proofs and broad tooling.
* Medium/long term: keep a **STARK backend** available for transparency, hash‑based assumptions, and post‑quantum posture.

---

## 1) What You Actually Trade Off

| Property                  | ZK‑SNARK (Groth16 / PLONK / Halo2)                                                     | ZK‑STARK                                                                    |
| ------------------------- | -------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| **Trusted setup**         | Groth16: circuit‑specific; **PLONK/Halo2: universal** (one ceremony for many circuits) | **None** (transparent)                                                      |
| **Assumptions**           | Pairing‑friendly elliptic curves + DLOG; Fiat‑Shamir; polynomial commitments (KZG)     | Collision‑resistant hash functions; FRI for low‑degree testing; Fiat‑Shamir |
| **Proof size**            | Tiny (∼ hundred bytes to a few KB)                                                     | Bigger (∼ tens to hundreds of KB; sometimes MB)                             |
| **Verify cost**           | Very fast (constant or quasi‑linear)                                                   | Usually higher than SNARK but improving                                     |
| **Prover cost**           | Generally lower for small/medium circuits; very optimized paths                        | Heavier but scales well for large computations                              |
| **Post‑quantum**          | **Not** PQ‑safe (curve DLOG breaks with large quantum computers)                       | Hash‑based → **more PQ‑amenable**                                           |
| **Maturity & ecosystems** | Very mature; many wallets/L2s; auditors experienced                                    | Rapidly maturing; fewer auditors, but strong momentum                       |
| **Security footguns**     | Setup ceremony hygiene; KZG structured reference string (SRS) risks                    | Soundness tightly tied to hash choices and FRI parameters                   |

**Rule of thumb:** If bandwidth/latency and verifier lightness dominate → SNARKs. If transparency/PQ/ceremony‑avoidance dominate → STARKs.

---

## 2) Recommendation for Mnemosyne

* **Phase A (MVP / Early Fielding)**: **PLONK/Halo2 SNARK** backend for identity attestations and trust‑predicate proofs. Rationale: compact proofs for mobile/edge verifiers; rich tooling; universal setup reduces ceremony churn.
* **Phase B (Dual‑Stack)**: Add **STARK** backend for high‑sensitivity contexts (anonymity sets, regulator‑sensitive proofs, long‑horizon archival) and for venues where transparency/anti‑ceremony is a hard requirement.
* **Policy Switches**: Per‑realm policy can force STARKs (e.g., “cold‑quorum” governance actions) or allow SNARKs (e.g., routine attribute checks).

---

## 3) Pluggable Proof Layer (PPL)

### 3.1 Goals

* **ABI‑stable** interface to the engine: circuits/artifacts become content‑addressed assets.
* **Hot‑swappable** backends (SNARK, STARK).
* **Deterministic artifact pipeline**: (spec → circuit → CRS/SRS (if needed) → proving/verifying keys → proof object → verification result).

### 3.2 Interface Sketch

```text
trait ProofBackend {
  // Compile a circuit spec to backend-specific keys/artifacts
  compile(spec: CircuitSpec) -> { pk: ProvingKey, vk: VerifyingKey, meta }

  // Produce a zero-knowledge proof for inputs/witness
  prove(pk, public_inputs, private_witness) -> Proof

  // Verify a proof against a verifying key
  verify(vk, public_inputs, proof: Proof) -> VerificationResult

  // Optional: batch verify / aggregate / recursive prove
  verify_batch(vk, batch_inputs, batch_proofs) -> VerificationResult
}
```

`CircuitSpec` is a backend‑agnostic IR (e.g., Rank‑1 constraints (R1CS) or arithmetic DSL) stored under a content hash.

### 3.3 Artifact Model

```text
/circuits/<name>/<version>/spec.cir
/circuits/<name>/<version>/snark/{pk,vk}.bin
/circuits/<name>/<version>/stark/{air,pk,vk}.bin
/proofs/<circuit>/<realm>/<txid>.proof
```

---

## 4) Where Proofs Fit in Mnemosyne

### 4.1 Deep Signal Protocol (Identity)

**Use cases**

* **Attribute disclosure**: “over‑18”, “member‑of‑X”, “has stake≥T”, “holds delegation Y”.
* **Selective credential reveal**: Present one attribute from a composite credential without doxxing the rest.
* **Linkability control**: One‑time pseudonyms tied to identity fragments via NIZK to prevent Sybil while preserving anonymity.

**Circuit primitives**

* Set membership (Merkle proof) with blinded leaf.
* Range proofs (Pedersen or Poseidon commitments → prove value in \[a,b]).
* Signature knowledge (prove knowledge of valid signature under issuer key without revealing signature).

### 4.2 Quiet Network (Peer / Trust Layer)

* **Progressive trust exchange**: challenge/response rounds where each side posts minimal proofs satisfying policy predicates.
* **Quorum attestations**: threshold voting where votes are zero‑knowledge (prove eligibility + unique vote without revealing identity).
* **Rate‑limiters**: proof‑of‑personhood/ stake without revealing real‑world identity.

### 4.3 Mnemosyne Engine (Memory / Orchestration)

* **Provenance sealing**: hash‑chains of artifacts with proofs of policy‑compliant derivations.
* **Audit‑on‑demand**: verifiers check that a memory operation followed allowed transforms without learning the data.

---

## 5) Messaging Stack Interop (MLS + PPL)

* **MLS** handles *transport confidentiality/integrity* for groups.
* **PPL** handles *semantic assertions* about identities/rights *inside* the MLS payloads.

**Flow**

1. Parties join MLS group (TreeKEM, authenticated joins).
2. A proposes a trust predicate `P` (e.g., member‑of set `S`).
3. B sends `Proof(P)` inside an MLS Application message.
4. Group verifies `Proof(P)` locally (fast) or via delegated verifier (batch).
5. Policy enforcer updates group ACL / capabilities based on `P`.

---

## 6) Concrete Proof Catalog (Initial)

| Name             | Predicate             | Public Inputs           | Witness             | Backend Notes                                  |
| ---------------- | --------------------- | ----------------------- | ------------------- | ---------------------------------------------- |
| `age≥18`         | value in \[18, max]   | hash(commitment), bound | DOB, salt           | SNARK preferred (compact)                      |
| `memberOf(S)`    | leaf∈Merkle(S)        | Merkle root             | leaf preimage, path | Either; STARK good for large sets              |
| `stake≥T`        | balance range         | commitment, T           | balance             | SNARK w/ range proof; or STARK for heavy state |
| `issuerSig`      | knows σ on m under pk | pk, m hash              | secret σ, sk\_user  | SNARK typical                                  |
| `one‑per‑person` | unique nullifier      | epoch, nullifier        | secret key          | Use linkable ring‑sig NIZK or SNARK nullifiers |

---

## 7) Data Structures

```text
ProofEnvelope {
  circuit_id: CID,
  backend: enum { SNARK, STARK },
  public_inputs: bytes,
  proof: bytes,
  meta: { version, curves_or_hashes, vk_ref, created_at }
}

IdentityFragment {
  fragment_id: CID,
  attributes: { k: v* }, // clear or committed
  commitments: { name: CID },
  proofs: [ProofEnvelope]
}
```

---

## 8) Security & Threat Model

* **Setup risk (SNARK)**: Use **universal SRS** (Powers‑of‑Tau) with multi‑party computation; pin ceremony transcript CID; rotate on schedule.
* **Hash choice (STARK)**: Standardize on conservative hashes (e.g., Rescue/Poseidon for circuits; SHA‑2/Keccak for commitments) with versioning.
* **Side‑channels**: Avoid leaking inputs via timing/length; normalize envelopes; pad MLS frames when required.
* **Linkability**: Enforce one‑time pseudonyms and nullifiers per realm/epoch.
* **Replay**: Bind proofs to context (realm id, epoch, nonce) and include MLS transcript hash.
* **Revocation**: Use accumulator or Merkle epoch roots; require freshness proofs (e.g., latest root signed by issuer quorum).

---

## 9) Implementation Plan & Milestones

**M1 — PPL Skeleton (2–3 weeks)**

* Define `CircuitSpec` IR and `ProofBackend` ABI.
* Implement SNARK backend (PLONK/Halo2) with dummy circuits; artifact registry (CID addressing).

**M2 — Identity Primitives (3–4 weeks)**

* Circuits: set‑membership, range proof, signature knowledge.
* Envelope formats + MLS embedding (Application msg subtype `mime=application/x-mnemo-proof`).

**M3 — Policy Engine & Quiet Network Hooks (3–4 weeks)**

* Policy DSL to express predicates; verifier integration; on‑verify capability updates.
* Nullifier design for “one‑per‑person”.

**M4 — STARK Backend (4–6 weeks)**

* AIR definition for membership/range; FRI parameters; batch verifier.

**M5 — Dual‑Stack & Governance (2–3 weeks)**

* Realm policies to select backend; audit telemetry; proving key distribution.

**M6 — Hardening & Audit (ongoing)**

* External cryptography review, transcript pinning, test vectors, interop tests.

---

## 10) Tooling & Libraries (suggested)

* **SNARK**: Halo2 (zk), PLONK variants; KZG commitments (with universal SRS).
* **STARK**: Winterfell / Plonky3‑style stacks / StarkWare‑like AIR patterns.
* **Hashes/Commitments**: Poseidon/Rescue inside circuits; SHA‑256/Keccak out‑of‑circuit.
* **MLS**: OpenMLS for group transport.

---

## 11) Test Strategy

* Golden test vectors per circuit; differential tests SNARK vs STARK backends on same `CircuitSpec`.
* Fuzz public input parsing; property tests for linking/nullifier collisions.
* MLS integration tests: join/leave, predicate gating, replay/rollback.

---

## 12) Migration & Future‑Proofing

* Version all circuits and proofs; embed `context_id` (realm/epoch).
* Allow **recursive proving** later (SNARK‑inside‑STARK or vice‑versa) for aggregation and chain anchoring.
* PQ roadmap: phase‑down SNARK usage for long‑lived, non‑upgradable artifacts.

---

## 13) Open Questions (to close before M2)

1. Minimum viable anonymity set per realm?
2. Issuer set model: centralized CA vs multi‑issuer accumulator?
3. Recursion requirements (batch attestations, roll‑up to anchor chain)?
4. On‑device proving targets (mobile) → pick proof complexity budgets.

---

## 14) Appendix: Minimal Message Examples

**Proof presentation over MLS**

```json
{
  "t": "mnemo.proof.present",
  "realm": "quietnet:alpha",
  "circuit": "memberOf:v1",
  "backend": "SNARK",
  "vk": "cid:Qm...",
  "pub": { "root": "0xabc...", "ctx": "epoch-42" },
  "proof": "base64:...",
  "meta": { "nonce": "0x...", "mls_tr_hash": "0x..." }
}
```

**Predicate policy example**

```hcl
rule "join_read" {
  when {
    proof.circuit == "memberOf:v1" && proof.verified && proof.pub.root in realm.allowed_roots
  }
  grant ["read", "react"]
}
```
