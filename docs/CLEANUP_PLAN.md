# Documentation Cleanup Plan

## Files to Archive (Outdated)

### Root docs/ files - OUTDATED
- `CURRENT_STATUS.md` - References old sprint approach, superseded by dual-track
- `MVP_REQUIREMENTS.md` - Old MVP approach, now using dual-track
- `ITERATIVE_TEST_PLAN.md` - Needs review for dual-track compatibility
- `DEPLOYMENT_NOTES.md` - May need updating for new architecture
- `AGENT_LIFECYCLE.md` - Experimental concept, should be in Track 2
- `UX_VISION.md` - Needs review for current approach
- `PITCH.md` - Marketing-focused, may not reflect current scientific approach
- `SECURITY.md` - Should be updated with new standards

### Notes files - TO DELETE
- `notes.txt` - Old research notes
- `notes_latest.txt` - Old research notes

## Files to Keep (Current)

### Root docs/ files - CURRENT
- ✅ `README.md` - Updated with dual-track
- ✅ `ROADMAP.md` - Updated with dual-track
- ✅ `AI_SPRINT_ROADMAP.md` - Updated with dual-track
- ✅ `DUAL_TRACK_IMPLEMENTATION.md` - Core new document
- ✅ `GLOSSARY.md` - Recently created
- ✅ `AI-MC.md` - Important reference for standards

## Directory Status

### Keep and Maintain
- ✅ `docs/spec/` - All updated (OVERVIEW, PROTOCOL, KARTOUCHE)
- ✅ `docs/hypotheses/` - Needed for Track 2 (contains id_compression.md)
- ✅ `docs/research/` - Contains AI-MC integration docs
- ✅ `docs/archive/` - For old documents

### Needs Review
- ⚠️ `docs/guides/` - May need updates for dual-track
  - FRONTEND.md
  - IMPLEMENTATION.md 
  - QUICK_START.md
- ⚠️ `docs/reference/` - Only has API.md, needs expansion
- ⚠️ `docs/decisions/` - Has one file, needs more decisions documented
- ⚠️ `docs/philosophy/` - Only SUSTAINABLE_GROWTH.md
- ⚠️ `docs/technical/` - Empty, could be removed or populated

## Recommended Actions

1. **Archive outdated files**:
   ```bash
   mkdir -p docs/archive/pre_dual_track
   mv docs/CURRENT_STATUS.md docs/archive/pre_dual_track/
   mv docs/MVP_REQUIREMENTS.md docs/archive/pre_dual_track/
   mv docs/ITERATIVE_TEST_PLAN.md docs/archive/pre_dual_track/
   mv docs/AGENT_LIFECYCLE.md docs/archive/pre_dual_track/
   mv docs/UX_VISION.md docs/archive/pre_dual_track/
   mv docs/PITCH.md docs/archive/pre_dual_track/
   ```

2. **Delete notes**:
   ```bash
   rm docs/notes.txt docs/notes_latest.txt
   ```

3. **Update critical files**:
   - Move SECURITY.md content into PROTOCOL.md security section
   - Update DEPLOYMENT_NOTES.md for dual-track

4. **Populate hypotheses/**:
   - Add behavioral_stability.md
   - Add resonance_mechanics.md
   - Add symbolic_representation.md

5. **Clean up empty directories**:
   - Remove docs/technical/ if not needed
   - Or populate with architecture diagrams

6. **Update guides/**:
   - Ensure QUICK_START.md reflects dual-track
   - Update IMPLEMENTATION.md for new approach
   - FRONTEND.md may need Track 1/Track 2 separation