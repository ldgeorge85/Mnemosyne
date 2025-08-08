# AI-Mediated Communication, Trust Enablement, and Identity Mapping: An Expanded Survey

**Version:** Aug 2025 • **Prepared for:** Research Agent

## 1) What this document covers (and why)

This survey stitches together three pillars—AI-mediated communication (AI-MC), trust enablement, and identity mapping/compression—then pulls in adjacent foundations you’ll need to make a real system work: human trust theory, provenance standards, crypto protocols, privacy-preserving tech, reputation systems, and governance. It’s intentionally cross-disciplinary so you can compare/borrow rather than reinvent.

* Canonical definition & agenda for **AI-MC**: Hancock et al. (2020). ([Oxford Academic][1], [Social Media Lab][2])
* **Human trust in automation** (still the backbone): Lee & See (2004). ([SAGE Journals][3], [PubMed][4], [user.engineering.uiowa.edu][5])
* **Organizational trust** framing (ability/benevolence/integrity): Mayer–Davis–Schoorman (1995). ([JSTOR][6], [Western Kentucky University][7], [journals.aom.org][8])

## 2) Older, foundational theories that still matter

* **Communication & meaning:** Shannon’s information theory; Grice’s cooperative principle/implicature; Austin’s speech acts. These are surprisingly practical when you formalize “what the agent says” vs “what the user understands.” ([Harvard Math People][9], [ia803209.us.archive.org][10], [University College London][11], [ILLC Projects][12], [silverbronzo.files.wordpress.com][13])
* **Humans treat media as social:** Reeves & Nass’ *Media Equation*—baseline for anthropomorphism in AI interfaces. ([University of Chicago Press][14], [afirstlook.com][15])

## 3) Trust enablement (measurement, calibration, provenance)

* **Trust models & calibration:** Use Lee & See (appropriate reliance) + MDS (ability/benevolence/integrity) to design feedback and disclosure loops. ([SAGE Journals][3], [user.engineering.uiowa.edu][5], [journals.aom.org][8])
* **Content provenance for AI-MC outputs:**

  * **W3C PROV** data model (generic provenance) for graphs of *who/what/when/how*. ([W3C][16])
  * **C2PA** (coalition of Adobe, Microsoft, BBC, etc.) for cryptographically bound content credentials on media—“nutrition label” for generated/edited assets. ([C2PA][17], [C2PA][18])
* **Risk governance scaffolding:** **NIST AI RMF 1.0** (with the 2024 Generative AI profile) and **ISO/IEC 42001:2023** (AI management systems). These give you control/assurance language for stakeholders. ([NIST Publications][19], [NIST][20], [ISO][21])

## 4) Identity mapping & verification (interoperable, privacy-respecting)

* **Core web standards:** **W3C Verifiable Credentials (VCDM 1.1/2.0)** and **DIDs 1.0** are the mainstream path for portable identity claims. ([W3C][22])
* **AuthN/AuthZ plumbing:** **OAuth 2.0 (RFC 6749)**, **OpenID Connect 1.0**, **WebAuthn/FIDO2** for phishing-resistant, passkey-friendly logins. ([IETF Datatracker][23], [RFC Editor][24], [OpenID Foundation][25], [W3C][26], [FIDO Alliance][27])

## 5) Secure comms for AI-mediated messaging

* **Modern group E2EE:** **MLS (RFC 9420)**—asynchronous, log-scaling group keying with FS/PCS; useful if agents sit inside group chats. ([IETF Datatracker][28], [RFC Editor][29])
* **1:1 E2EE baseline:** **Signal Double Ratchet** and analyses thereof—great mental model for post-compromise security & forward secrecy. ([Signal Messenger][30], [crypto.iacr.org][31])

## 6) Privacy-preserving identity *compression* & matching

When you need “is this the same entity/capability/context?” without doxxing:

* **Differential Privacy** (Dwork et al.): noise-adding guarantees for aggregates. Use for telemetry & model evaluation, not identity per se. ([Computer and Information Science][32], [CiteSeerX][33])
* **Private Set Intersection (PSI)**: intersect identifiers or traits across parties sans leakage; see recent surveys and FHE-based constructions. ([ScienceDirect][34], [user.eng.umd.edu][35], [PubMed Central][36])
* **Bloom filters** (and counting variants): classic set-membership sketching for low-leakage “maybe same, maybe not”—be explicit about false-positive tradeoffs. ([Wikipedia][37], [tsapps.nist.gov][38])
* **Fully Homomorphic Encryption**: still heavy, but worth tracking for server-side identity scoring without decryption (Gentry 2009). ([CMU School of Computer Science][39], [crypto.stanford.edu][40])

## 7) Reputation & web-of-trust (progressive trust mechanisms)

* **Graph-based global trust:** **PageRank** (intuition + math) and **EigenTrust** (P2P) are directly reusable patterns for progressive trust scoring across identities/agents. ([Computer and Information Science][41], [ilpubs.stanford.edu][42], [nlp.stanford.edu][43])
* **User-centric trust webs:** **OpenPGP/Web of Trust** (vs. X.509 hierarchies) for decentralized attestations; conceptual grounding for “who vouches for whom.” ([IETF Datatracker][44], [OpenPGP][45])
* **Sybil resistance:** **SybilGuard** et al.—if you plan open reputation, you’ll need social-graph assumptions or costs. ([math.cmu.edu][46], [ACM Digital Library][47])

## 8) Documentation & transparency artifacts

* **Model Cards** (Mitchell et al. 2019) for model reporting; **Datasheets for Datasets** (Gebru et al. 2018) and **Data Statements** for NLP (Bender & Friedman 2018). These are great for AI-MC disclosure & trust calibration. ([ACM Digital Library][48], [arXiv][49], [Microsoft][50], [ACL Anthology][51])

## 9) Regulatory context (so you don’t get blindsided)

* **EU AI Act**: in force since **Aug 1, 2024**; staged applicability through **Aug 2025–Aug 2026** with some earlier obligations. Start aligning now (transparency, risk, provenance). ([EU Artificial Intelligence Act][52], [Digital Strategy][53])
* **ISO/IEC 42001** is already surfacing in enterprise guidance and news—useful signaling for partners/investors. ([KPMG][54], [Financial Times][55])

---

## 10) How to apply this (concise design map)

1. **Identity & claims:** DIDs + VCs for portable identity; OIDC/OAuth for sessioning; WebAuthn for strong auth. ([W3C][56], [OpenID Foundation][25], [IETF Datatracker][23])
2. **Trust signals:** Combine (a) provenance (PROV + C2PA), (b) reputation (EigenTrust/PageRank-style), and (c) disclosure artifacts (Model Cards/Data Sheets) surfaced in-UI for calibration. ([W3C][16], [C2PA][17], [nlp.stanford.edu][43], [Computer and Information Science][41], [ACM Digital Library][48], [arXiv][57])
3. **Privacy-preserving joins:** PSI + Bloom-filter sketches to match identities/features across silos; DP for aggregates; explore HE where latency allows. ([ScienceDirect][34], [Wikipedia][37], [Computer and Information Science][32])
4. **Secure channels:** MLS for groups, Double Ratchet for 1:1; add explicit AI-MC provenance headers to messages. ([IETF Datatracker][28], [Signal Messenger][30])
5. **Governance:** Map risks and controls to NIST AI RMF + ISO/IEC 42001; align disclosures with EU AI Act timelines. ([NIST Publications][19], [ISO][21], [Digital Strategy][53])

---

## 11) Annotated reading list (starter pack)

* **AI-MC core:** Hancock et al., *Journal of Computer-Mediated Communication*, 2020. ([Oxford Academic][1])
* **Trust in automation:** Lee & See, 2004—what “appropriate reliance” really means. ([SAGE Journals][3])
* **Org trust model:** Mayer–Davis–Schoorman, 1995—ABI model used everywhere. ([journals.aom.org][8])
* **Anthropomorphism:** Reeves & Nass, 1996—why polite chatbots “work.” ([University of Chicago Press][14])
* **Provenance:** W3C PROV Overview + PROV-DM. ([W3C][58])
* **Content authenticity:** C2PA spec + explainer. ([C2PA][17], [C2PA][59])
* **Identity:** VCDM 1.1/2.0; DIDs 1.0. ([W3C][22])
* **AuthN/AuthZ:** OAuth 2.0 (RFC 6749), OIDC Core, WebAuthn L2/L3. ([IETF Datatracker][23], [OpenID Foundation][25], [W3C][26])
* **Comms security:** MLS (RFC 9420); Signal Double Ratchet spec. ([IETF Datatracker][28]) ([Signal Messenger][30])
* **Privacy tech:** Dwork & Roth textbook (DP); PSI survey; Gentry FHE. ([Computer and Information Science][32], [ScienceDirect][34], [CMU School of Computer Science][39])
* **Reputation:** PageRank; EigenTrust. ([ilpubs.stanford.edu][42], [nlp.stanford.edu][43])
* **Governance:** NIST AI RMF 1.0 + GenAI profile; ISO/IEC 42001; EU AI Act timeline. ([NIST Publications][19], [ISO][21], [Digital Strategy][53])

---

If you want, I can package this as a clean **PDF/Docx** with the citations hyperlinked and a one-page executive summary for quick ingestion. Or I can tailor it to your specific “Mnemosyne/monosomy” architecture with a short migration map (what to adopt vs. build).

[1]: https://academic.oup.com/jcmc/article/25/1/89/5714020?utm_source=chatgpt.com "AI-Mediated Communication: Definition, Research Agenda ..."
[2]: https://sml.stanford.edu/publications/2020/ai-mediated-communication-definition-research-agenda-and-ethical-considerations?utm_source=chatgpt.com "AI-Mediated Communication: Definition, Research Agenda ..."
[3]: https://journals.sagepub.com/doi/10.1518/hfes.46.1.50_30392?utm_source=chatgpt.com "Trust in Automation: Designing for Appropriate Reliance"
[4]: https://pubmed.ncbi.nlm.nih.gov/15151155/?utm_source=chatgpt.com "Trust in automation: designing for appropriate reliance"
[5]: https://user.engineering.uiowa.edu/~csl/publications/pdf/leesee04.pdf?utm_source=chatgpt.com "Trust in Automation: Designing for Appropriate Reliance"
[6]: https://www.jstor.org/stable/258792?utm_source=chatgpt.com "An Integrative Model of Organizational Trust"
[7]: https://people.wku.edu/richard.miller/Mayer%20Trust%20article.pdf?utm_source=chatgpt.com "An Integrative Model of Organizational Trust"
[8]: https://journals.aom.org/doi/abs/10.5465/AMR.1995.9508080335?utm_source=chatgpt.com "An Integrative Model Of Organizational Trust"
[9]: https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf?utm_source=chatgpt.com "A Mathematical Theory of Communication"
[10]: https://ia803209.us.archive.org/27/items/bstj27-3-379/bstj27-3-379_text.pdf?utm_source=chatgpt.com "A Mathematical Theory of Communication. (Shannon, C.E.)"
[11]: https://www.ucl.ac.uk/ls/studypacks/Grice-Logic.pdf?utm_source=chatgpt.com "HP Grice - Logic and Conversation"
[12]: https://projects.illc.uva.nl/inquisitivesemantics/assets/files/papers/Grice1975.pdf?utm_source=chatgpt.com "LOGIC AND CONVERSATION*"
[13]: https://silverbronzo.files.wordpress.com/2017/10/austin-how-to-do-things-with-words-1962.pdf?utm_source=chatgpt.com "jl austin - how to do things - with words"
[14]: https://press.uchicago.edu/ucp/books/book/distributed/M/bo3618528.html?utm_source=chatgpt.com "The Media Equation: How People Treat Computers ..."
[15]: https://www.afirstlook.com/docs/mediaeq.pdf?utm_source=chatgpt.com "The Media Equation"
[16]: https://www.w3.org/TR/prov-dm/?utm_source=chatgpt.com "PROV-DM: The PROV Data Model"
[17]: https://c2pa.org/specifications/specifications/2.2/index.html?utm_source=chatgpt.com "C2PA Specifications"
[18]: https://spec.c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html?utm_source=chatgpt.com "Content Credentials : C2PA Technical Specification"
[19]: https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf?utm_source=chatgpt.com "Artificial Intelligence Risk Management Framework (AI RMF 1.0)"
[20]: https://www.nist.gov/itl/ai-risk-management-framework?utm_source=chatgpt.com "AI Risk Management Framework"
[21]: https://www.iso.org/standard/42001?utm_source=chatgpt.com "ISO/IEC 42001:2023 - AI management systems"
[22]: https://www.w3.org/TR/2022/REC-vc-data-model-20220303/?utm_source=chatgpt.com "Verifiable Credentials Data Model v1.1"
[23]: https://datatracker.ietf.org/doc/html/rfc6749?utm_source=chatgpt.com "RFC 6749 - The OAuth 2.0 Authorization Framework"
[24]: https://www.rfc-editor.org/info/rfc6749?utm_source=chatgpt.com "Information on RFC 6749"
[25]: https://openid.net/specs/openid-connect-core-1_0.html?utm_source=chatgpt.com "OpenID Connect Core 1.0 incorporating errata set 2"
[26]: https://www.w3.org/TR/webauthn-2/?utm_source=chatgpt.com "Web Authentication: An API for accessing Public Key ..."
[27]: https://fidoalliance.org/specifications/?utm_source=chatgpt.com "User Authentication Specifications Overview"
[28]: https://datatracker.ietf.org/doc/rfc9420/?utm_source=chatgpt.com "RFC 9420 - The Messaging Layer Security (MLS) Protocol"
[29]: https://www.rfc-editor.org/info/rfc9420?utm_source=chatgpt.com "Information on RFC 9420"
[30]: https://signal.org/docs/specifications/doubleratchet/doubleratchet.pdf?utm_source=chatgpt.com "The Double Ratchet Algorithm"
[31]: https://crypto.iacr.org/2022/papers/530630_1_En_27_Chapter_OnlinePDF.pdf?utm_source=chatgpt.com "A More Complete Analysis of the Signal Double Ratchet ..."
[32]: https://www.cis.upenn.edu/~aaroth/Papers/privacybook.pdf?utm_source=chatgpt.com "The Algorithmic Foundations of Differential Privacy - CIS UPenn"
[33]: https://citeseerx.ist.psu.edu/document?doi=283ecc8622694c070fa53aee7a1c37dadc603f8d&repid=rep1&type=pdf&utm_source=chatgpt.com "Differential Privacy"
[34]: https://www.sciencedirect.com/science/article/pii/S1574013723000345?utm_source=chatgpt.com "Private set intersection: A systematic literature review"
[35]: https://user.eng.umd.edu/~ulukus/papers/journal/psi-mmspir.pdf?utm_source=chatgpt.com "Private Set Intersection: A Multi-Message Symmetric Private ..."
[36]: https://pmc.ncbi.nlm.nih.gov/articles/PMC7760825/?utm_source=chatgpt.com "Two-Party Privacy-Preserving Set Intersection with FHE"
[37]: https://en.wikipedia.org/wiki/Bloom_filter?utm_source=chatgpt.com "Bloom filter"
[38]: https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=903775&utm_source=chatgpt.com "A New Analysis of the False-Positive Rate of a Bloom Filter"
[39]: https://www.cs.cmu.edu/~odonnell/hits09/gentry-homomorphic-encryption.pdf?utm_source=chatgpt.com "Fully Homomorphic Encryption Using Ideal Lattices"
[40]: https://crypto.stanford.edu/craig/craig-thesis.pdf?utm_source=chatgpt.com "A FULLY HOMOMORPHIC ENCRYPTION SCHEME A ..."
[41]: https://www.cis.upenn.edu/~mkearns/teaching/NetworkedLife/pagerank.pdf?utm_source=chatgpt.com "The PageRank Citation Ranking: Bringing Order to the Web"
[42]: https://ilpubs.stanford.edu/422/?utm_source=chatgpt.com "The PageRank Citation Ranking: Bringing Order to the Web."
[43]: https://nlp.stanford.edu/pubs/eigentrust.pdf?utm_source=chatgpt.com "The EigenTrust Algorithm for Reputation Management in P2P ..."
[44]: https://datatracker.ietf.org/doc/html/rfc4880?utm_source=chatgpt.com "RFC 4880 - OpenPGP Message Format"
[45]: https://www.openpgp.org/about/?utm_source=chatgpt.com "About"
[46]: https://www.math.cmu.edu/~adf/research/SybilGuard.pdf?utm_source=chatgpt.com "SybilGuard: Defending Against Sybil Attacks via Social ..."
[47]: https://dl.acm.org/doi/10.1145/1159913.1159945?utm_source=chatgpt.com "SybilGuard: defending against sybil attacks via social ..."
[48]: https://dl.acm.org/doi/10.1145/3287560.3287596?utm_source=chatgpt.com "Model Cards for Model Reporting | Proceedings of the ..."
[49]: https://arxiv.org/pdf/1810.03993?utm_source=chatgpt.com "Model Cards for Model Reporting"
[50]: https://www.microsoft.com/en-us/research/wp-content/uploads/2019/01/1803.09010.pdf?utm_source=chatgpt.com "Datasheets for Datasets"
[51]: https://aclanthology.org/Q18-1041/?utm_source=chatgpt.com "Data Statements for Natural Language Processing: Toward ..."
[52]: https://artificialintelligenceact.eu/the-act/?utm_source=chatgpt.com "The Act Texts | EU Artificial Intelligence Act"
[53]: https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai?utm_source=chatgpt.com "AI Act | Shaping Europe's digital future - European Union"
[54]: https://kpmg.com/ch/en/insights/artificial-intelligence/iso-iec-42001.html?utm_source=chatgpt.com "ISO/IEC 42001: a new standard for AI governance"
[55]: https://www.ft.com/content/46c3d395-b8c0-494e-803b-a533ff4a8c62?utm_source=chatgpt.com "Letter: Where business leaders can feel reassured on AI"
[56]: https://www.w3.org/TR/did-core/?utm_source=chatgpt.com "Decentralized Identifiers (DIDs) v1.0"
[57]: https://arxiv.org/abs/1803.09010?utm_source=chatgpt.com "[1803.09010] Datasheets for Datasets"
[58]: https://www.w3.org/TR/prov-overview/?utm_source=chatgpt.com "PROV-Overview"
[59]: https://spec.c2pa.org/specifications/specifications/1.3/explainer/Explainer.html?utm_source=chatgpt.com "C2PA Explainer :: C2PA Specifications"
