# Simple Trust Protocol: Paper, Notepad & Spreadsheet Version
*A Low-Tech Implementation of Modular Identity and Trust Systems*

## Overview

This document describes how to implement the core concepts of modular identity, trust validation, and dispute resolution using only:
- **Paper and pen** (individual cards)
- **Notepad** (personal records)
- **Basic spreadsheet** (community registry)
- **Optional: QR codes** (for verification)

No servers, no blockchain, no complex cryptography - just human-readable records that capture the essence of self-sovereign identity with community validation.

## Part 1: The Paper Identity Card

### 1.1 Basic Identity Card Template

```
╔══════════════════════════════════════════════════════╗
║                 IDENTITY CARD v1.0                   ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║ Name/Alias: _______________________  ID: ________   ║
║ Created: ___/___/____    Updated: ___/___/____     ║
║                                                      ║
║ ┌────────────────────────────────────────────────┐ ║
║ │ CORE IDENTITY (Required)           Score: ___  │ ║
║ │ □ Basic Info Verified                          │ ║
║ │ □ Unique ID Confirmed                          │ ║
║ │ □ Contact Method: _______________              │ ║
║ └────────────────────────────────────────────────┘ ║
║                                                      ║
║ ┌────────────────────────────────────────────────┐ ║
║ │ MODULES (Check all that apply)                 │ ║
║ │                                                 │ ║
║ │ □ PHYSICAL        Score: ___/10                │ ║
║ │   Height: _____ Eyes: _____ Hair: _____       │ ║
║ │                                                 │ ║
║ │ □ PROFESSIONAL    Score: ___/10                │ ║
║ │   Skills: ______________________________      │ ║
║ │   Years Exp: ___                              │ ║
║ │                                                 │ ║
║ │ □ SOCIAL          Score: ___/10                │ ║
║ │   Connections: Few/Some/Many                  │ ║
║ │   Helpful: Y/N  Reliable: Y/N                 │ ║
║ │                                                 │ ║
║ │ □ FINANCIAL       Score: ___/10                │ ║
║ │   Range: Low/Med/High                         │ ║
║ │   Reliable Payer: Y/N                         │ ║
║ │                                                 │ ║
║ │ □ CUSTOM: _________ Score: ___/10             │ ║
║ │   Details: ____________________________       │ ║
║ └────────────────────────────────────────────────┘ ║
║                                                      ║
║ VALIDATORS (People who verified claims)             ║
║ ┌────────────────────────────────────────────────┐ ║
║ │ Name         Module    Date      Signature     │ ║
║ │ _________    ______    ____     __________    │ ║
║ │ _________    ______    ____     __________    │ ║
║ │ _________    ______    ____     __________    │ ║
║ └────────────────────────────────────────────────┘ ║
║                                                      ║
║ TRUST SCORES (From others)                          ║
║ ┌────────────────────────────────────────────────┐ ║
║ │ From          Score    Context    Date         │ ║
║ │ _________     ___      _______    ____        │ ║
║ │ _________     ___      _______    ____        │ ║
║ └────────────────────────────────────────────────┘ ║
║                                                      ║
║ VERIFICATION: [QR Code or Hash: ___________]        ║
╚══════════════════════════════════════════════════════╝
```

### 1.2 How to Fill Out Your Card

```markdown
## CREATING YOUR IDENTITY CARD

### Step 1: Basic Information
- Choose a name/alias (can be real name or pseudonym)
- Generate unique ID (can be: initials+birthyear+number, e.g., "JD1990-001")
- Write creation date

### Step 2: Score Your Modules (Self-Assessment)
Rate yourself 1-10 on each module you want to include:
- 1-3: Low/Beginning
- 4-6: Medium/Competent
- 7-9: High/Expert
- 10: Exceptional

### Step 3: Get Validators
Ask trusted people to verify specific claims:
- They check your claim
- They sign and date
- Minimum 2 validators per module recommended

### Step 4: Collect Trust Scores
As you interact with others, they can give you trust scores:
- General trust: 1-10
- Context-specific (professional, social, etc.)
- Date helps track trust evolution

### Step 5: Create Verification
Option A: Calculate simple hash
- Add all scores, multiply by ID number
- Write result as verification code

Option B: Generate QR code (using free QR generator)
- Include: ID + Module scores + Validator count
- Print and attach to card
```

## Part 2: The Trust Ledger (Notepad Version)

### 2.1 Personal Trust Ledger Format

Keep in a notebook, one page per person you interact with:

```
═══════════════════════════════════════════════════════
TRUST LEDGER - Page 1

Subject: Alice Smith               ID: AS1985-001
First Interaction: Jan 15, 2024
My Trust Score for Them: 7/10

INTERACTIONS LOG:
Date     Type         Outcome    Trust Change   Notes
----     ----         -------    ------------   -----
1/15/24  Met          Good       +7 (initial)   Coffee meeting
1/20/24  Trade        Success    +1 (now 8)     Book exchange
2/01/24  Favor        Failed     -2 (now 6)     Didn't follow through
2/15/24  Apology      Good       +1 (now 7)     Made amends

VALIDATED CLAIMS:
Claim              Date Verified    My Confidence
-----              -------------    -------------
"Good at Python"   1/20/24         High (saw code)
"Has blue eyes"    1/15/24         Certain (met in person)
"Lived in Paris"   2/01/24         Medium (showed photos)

DISPUTES:
Claim              Issue           Resolution
-----              -----           ----------
"Never late"       Was late 2/1    Acknowledged, apologized

SHARED DATA:
What Shared        When       Why           Expiry
-----------        ----       ---           ------
Phone number       1/15/24    Future trade  None
Email             1/20/24    Project       6 months

NOTES:
- Reliable for technical matters
- Sometimes overcommits
- Good at resolving conflicts
═══════════════════════════════════════════════════════
```

### 2.2 Community Trust Summary (Monthly)

```
MONTHLY TRUST SUMMARY - February 2024

MY TRUST NETWORK:
High Trust (8-10): Bob, Carol, David
Medium Trust (5-7): Alice, Eve, Frank
Low Trust (1-4): Gary
No Trust (0): Henry

VALIDATIONS I PROVIDED:
For          Claim            Date
---          -----            ----
Bob          "Good chef"      2/10
Carol        "Speaks French"  2/15

VALIDATIONS I RECEIVED:
From         Claim            Date
----         -----            ----
David        "Reliable"       2/12
Eve          "Good writer"    2/20

DISPUTES THIS MONTH:
Target       Claim            Status
------       -----            ------
Frank        "Always honest"  Pending (gathering evidence)

TRUST SCORE CHANGES:
Person       Start    End     Change    Reason
------       -----    ---     ------    ------
Alice        8        7       -1        Broken promise
Gary         3        1       -2        Multiple issues
Carol        6        8       +2        Great collaboration
```

## Part 3: Spreadsheet Implementation

### 3.1 Master Identity Registry (Community Shared)

**IDENTITY_REGISTRY.xlsx - Sheet 1: Identities**

| ID | Name | Core | Physical | Professional | Social | Financial | Avg_Score | Validators | Disputes | Updated |
|----|------|------|----------|--------------|--------|-----------|-----------|------------|----------|---------|
| AS1985-001 | Alice S. | 8 | 7 | 9 | 6 | 5 | 7.0 | 5 | 1 | 2/20/24 |
| BD1990-002 | Bob D. | 7 | 6 | 8 | 9 | 7 | 7.4 | 4 | 0 | 2/19/24 |
| CC1992-003 | Carol C. | 9 | 8 | 7 | 8 | 6 | 7.6 | 6 | 2 | 2/21/24 |

**Sheet 2: Validations**

| Validator_ID | Subject_ID | Module | Claim | Verified | Date | Notes |
|--------------|------------|--------|-------|----------|------|-------|
| BD1990-002 | AS1985-001 | Professional | "Python Expert" | YES | 2/10/24 | Reviewed code |
| CC1992-003 | AS1985-001 | Physical | "Blue eyes" | YES | 2/11/24 | Met in person |
| AS1985-001 | BD1990-002 | Social | "Helpful" | YES | 2/12/24 | Helped with project |

**Sheet 3: Trust_Relationships**

| From_ID | To_ID | Trust_Score | Context | Date | Notes |
|---------|-------|-------------|---------|------|-------|
| AS1985-001 | BD1990-002 | 8 | General | 2/20/24 | Reliable partner |
| BD1990-002 | AS1985-001 | 7 | Professional | 2/20/24 | Good skills |
| CC1992-003 | AS1985-001 | 6 | Social | 2/21/24 | Sometimes flaky |

**Sheet 4: Disputes**

| Dispute_ID | Raised_By | Against | Module | Claim | Evidence | Status | Resolution | Date |
|------------|-----------|---------|--------|-------|----------|--------|------------|------|
| D001 | CC1992-003 | AS1985-001 | Professional | "10 years exp" | LinkedIn shows 5 | Resolved | Reduced to 5 years | 2/15/24 |
| D002 | BD1990-002 | CC1992-003 | Financial | "High range" | Failed payment | Pending | - | 2/21/24 |

### 3.2 Spreadsheet Formulas

```
Useful Excel/Google Sheets Formulas:

1. Calculate Average Trust Score:
=AVERAGE(C2:G2)  // Average of module scores

2. Count Validators:
=COUNTIF(Validations!B:B,A2)  // Count validations for this ID

3. Trust Network Score:
=AVERAGEIF(Trust_Relationships!B:B,A2,Trust_Relationships!C:C)

4. Dispute Impact:
=IF(COUNTIF(Disputes!C:C,A2)>0,
    H2-(COUNTIF(Disputes!C:C,A2)*0.5),
    H2)  // Reduce score by 0.5 per dispute

5. Trust Decay (time-based):
=H2*(0.95^((TODAY()-J2)/30))  // 5% decay per month

6. Weighted Module Score:
=(C2*2+D2*1+E2*3+F2*2+G2*1)/9  // Different weights per module
```

## Part 4: Operating Procedures

### 4.1 Daily Operations

```markdown
## DAILY TRUST PROTOCOL

### Morning Review (5 minutes)
1. Check your trust ledger
2. Note any pending validations
3. Review dispute status

### When Meeting Someone New
1. Exchange identity cards (or photos)
2. Verify 1-2 claims if possible
3. Record initial trust score
4. Add to your ledger

### When Someone Requests Validation
1. Only validate what you can verify
2. Be honest - your reputation depends on it
3. Sign and date their card
4. Record in your ledger

### Evening Update (5 minutes)
1. Update interaction log
2. Adjust trust scores if needed
3. Note any new disputes
```

### 4.2 Weekly Community Sync

```markdown
## WEEKLY COMMUNITY MEETING PROTOCOL

### Agenda (30 minutes total)

1. **New Members** (5 min)
   - Introduce with identity card
   - Initial validators volunteer
   - Add to registry

2. **Validation Requests** (10 min)
   - Members request specific validations
   - Validators volunteer or are nominated
   - Schedule validation meetings

3. **Dispute Resolution** (10 min)
   - Present evidence for open disputes
   - Community votes on resolution
   - Update registry and cards

4. **Trust Updates** (5 min)
   - Major trust changes announced
   - Registry updated
   - Patterns discussed

### Voting Rules
- Simple majority for validations
- 2/3 majority for dispute resolutions
- Unanimous for expulsions
```

### 4.3 Monthly Governance

```markdown
## MONTHLY GOVERNANCE MEETING

### Review Metrics
- Total members
- Average trust scores
- Validation rate
- Dispute frequency

### Policy Updates
- Vote on new module types
- Adjust scoring criteria
- Update procedures

### Trust Audit
- Review low-trust members
- Celebrate high-trust achievements
- Plan trust-building activities

### Archive
- Backup all spreadsheets
- Store paper cards safely
- Document major decisions
```

## Part 5: Dispute Resolution (Paper Process)

### 5.1 Dispute Form

```
═══════════════════════════════════════════════════════
           TRUST DISPUTE FORM

Dispute ID: _________ Date: ___/___/____

COMPLAINANT:
Name: _________________ ID: _____________

RESPONDENT:
Name: _________________ ID: _____________

DISPUTED CLAIM:
Module: _____________
Specific Claim: _________________________________
_________________________________________________

EVIDENCE:
□ Photo (attached)
□ Document (attached)
□ Witness statements (attached)
□ Other: _______________________________________

WITNESSES:
1. Name: __________ ID: _______ Statement attached: □
2. Name: __________ ID: _______ Statement attached: □
3. Name: __________ ID: _______ Statement attached: □

REQUESTED RESOLUTION:
□ Remove claim
□ Modify claim to: _____________________________
□ Trust score adjustment
□ Other: _______________________________________

COMPLAINANT SIGNATURE: _________________________

---OFFICIAL USE ONLY---

REVIEW PANEL:
1. _____________ Vote: Accept/Reject
2. _____________ Vote: Accept/Reject
3. _____________ Vote: Accept/Reject

RESOLUTION:
□ Dispute Upheld - Action: ____________________
□ Dispute Rejected - Reason: __________________

Date Resolved: ___/___/____
Panel Chair Signature: _________________________
═══════════════════════════════════════════════════════
```

### 5.2 Evidence Standards

```markdown
## EVIDENCE REQUIREMENTS

### Level 1: Direct Evidence (Highest)
- In-person observation
- Original documents
- Photographic proof with date

### Level 2: Corroborated Evidence (Medium)
- Multiple witness statements
- Documented pattern of behavior
- Third-party records

### Level 3: Circumstantial Evidence (Lowest)
- Single witness statement
- Indirect indicators
- Historical patterns

### Minimum Evidence for Dispute
- At least Level 2 evidence
- OR two pieces of Level 3 evidence
- Plus good faith basis for dispute
```

## Part 6: Security Without Cryptography

### 6.1 Tamper Detection

```markdown
## SECURITY MEASURES (No-Tech Version)

### For Identity Cards
1. **Watermark**: Draw unique pattern on back
2. **Witness Signatures**: Multiple people sign
3. **Date Stamps**: Use consistent date format
4. **Sequential Numbering**: Number all updates
5. **Photo**: Attach small photo if possible

### For Ledgers
1. **Pen Only**: No erasable writing
2. **Sequential Pages**: Number all pages
3. **Cross-References**: Reference other records
4. **Witness Initials**: Have someone initial important entries
5. **Carbon Copies**: Keep duplicate in separate location

### For Community Registry
1. **Version Control**: Save dated copies
2. **Change Log**: Document all changes
3. **Multiple Copies**: Different people keep copies
4. **Regular Audits**: Monthly comparison of copies
5. **Public Posting**: Post summary publicly
```

### 6.2 Privacy Protection

```markdown
## PRIVACY GUIDELINES

### Information Minimization
- Only share necessary modules
- Use ranges not exact values (e.g., "High" not "$100K")
- Time-limit shared information

### Selective Disclosure
- Create module-specific cards
- Black out irrelevant sections
- Use references instead of details

### Consent Tracking
What: ____________ To Whom: ____________
Purpose: _________ Expiry: _____________
Signature: _______ Date: _______________
```

## Part 7: Scaling Beyond Paper

### 7.1 Hybrid Approach

```markdown
## PROGRESSIVE DIGITALIZATION

### Level 0: Pure Paper
- Identity cards
- Personal ledgers
- Meeting-based updates

### Level 1: Digital Records
- Spreadsheet registry
- Email validations
- Photo documentation

### Level 2: Simple Verification
- QR codes on cards
- Hash calculations
- Basic encryption

### Level 3: Full Digital
- Implement full protocol
- Cryptographic signatures
- Automated validation
```

### 7.2 Network Growth Patterns

```markdown
## GROWTH STRATEGIES

### Starting (2-10 people)
- Everyone knows everyone
- All validations in-person
- Single shared spreadsheet

### Growing (10-50 people)
- Sub-groups form
- Validation committees
- Multiple spreadsheet managers

### Scaling (50-200 people)
- Regional chapters
- Standardized procedures
- Consider digital tools

### Large (200+ people)
- Migrate to digital system
- Keep paper as backup
- Formal governance structure
```

## Part 8: Real-World Examples

### 8.1 Coffee Shop Trust Network

```markdown
## EXAMPLE: Local Coffee Shop Implementation

### Setup
- Regular customers get identity cards
- Barista maintains trust ledger
- Weekly "trust coffee" meetings

### Modules Used
- Social (friendliness)
- Financial (pays on time)
- Reliability (shows up)

### Benefits
- "High trust" customers get informal credit
- Disputes resolved quickly
- Community bonds strengthen

### One Month Results
- 15 participants
- 43 validations
- 2 disputes resolved
- Average trust: 7.2/10
```

### 8.2 Neighborhood Skill Share

```markdown
## EXAMPLE: Skill Sharing Network

### Setup
- Neighbors create Professional module cards
- Skills validated by recipients
- Monthly skill swap meetings

### Tracking
- Spreadsheet of skills offered/needed
- Trust scores affect priority
- Successful swaps increase trust

### Three Month Results
- 30 participants
- 120 skill validations
- 200+ successful skill swaps
- 5 disputes (all resolved)
```

### 8.3 Student Study Group

```markdown
## EXAMPLE: University Study Group

### Setup
- Students create academic identity cards
- Modules: Knowledge, Reliability, Teaching
- Validation through completed assignments

### Benefits
- Find trusted study partners
- Identify subject experts
- Build reputation over semester

### Semester Results
- 25 students
- Average GPA increased 0.3
- 90% found regular study partners
- Trust network continued next semester
```

## Part 9: Templates and Forms

### 9.1 Quick Start Kit

```markdown
## WHAT YOU NEED TO START

### Materials
□ Index cards (for identity cards)
□ Notebook (for trust ledger)
□ Pen (non-erasable)
□ Folder (for dispute forms)
□ Optional: Smartphone (for QR codes)

### Documents
□ Identity card template (copy by hand)
□ Trust ledger pages (create format)
□ Dispute forms (copy template)
□ Validation log (simple list)

### People
□ 2+ others to start network
□ Agreement on basic rules
□ Regular meeting time

### First Week
□ Everyone creates identity card
□ Exchange initial validations
□ Set trust scores
□ Schedule weekly check-in
```

### 9.2 Simplified Mobile Version

```markdown
## SMARTPHONE NOTES VERSION

### Identity (Notes App)
==MY IDENTITY==
ID: JD1990-001
Core: 8
Professional: 9
Social: 7
Trust Avg: 8.0
Validators: 5

### Trust Log (Per Person)
==ALICE - AS1985-001==
Trust: 7/10
Met: 1/15/24
Good: Reliable, Smart
Bad: Sometimes late
Validated: Python skills

### Quick Dispute
TO: Community
RE: Bob claim "Never late"
Evidence: Late 3 times in Jan
Photos: [attached]
Request: Reduce claim
```

## Part 10: Philosophy and Principles

### 10.1 Why This Works

```markdown
## CORE PRINCIPLES

### 1. Trust is Local
- Start with who you know
- Build outward gradually
- Quality over quantity

### 2. Validation is Valuable
- Costs reputation to lie
- Benefits to tell truth
- Community enforces honesty

### 3. Disputes are Healthy
- Keeps system honest
- Prevents trust inflation
- Resolves conflicts peacefully

### 4. Simplicity is Strength
- Anyone can participate
- No technical barriers
- Transparent process
```

### 10.2 Social Dynamics

```markdown
## MAKING IT WORK SOCIALLY

### Building Buy-In
- Start with enthusiasts
- Show early benefits
- Celebrate successes

### Maintaining Momentum
- Regular meetings
- Visible updates
- Recognize validators

### Handling Resistance
- Address privacy concerns
- Start with opt-in
- Show value through examples

### Cultural Adaptation
- Adjust to local norms
- Respect existing hierarchies
- Build on current trust systems
```

## Conclusion

This Simple Trust Protocol proves that the core concepts of self-sovereign identity, modular trust, and community validation don't require complex technology. With just paper, pen, and human cooperation, communities can:

- Create verifiable identities
- Build trust networks
- Resolve disputes
- Share validated information
- Maintain privacy
- Scale gradually

The system works because it relies on the most fundamental technology: human social dynamics and the value of reputation. Whether implemented with index cards in a coffee shop or spreadsheets in a neighborhood, the principles remain the same:

**You declare who you are.**
**Your community validates what's true.**
**Trust emerges from the process.**

This isn't just a fallback for when technology fails - it's proof that the protocol itself is fundamentally human, not technological. The computers, cryptography, and networks just make it faster and larger-scale. The trust itself comes from people.

---

*"The highest technology is no technology - just humans trusting humans, one validation at a time."*