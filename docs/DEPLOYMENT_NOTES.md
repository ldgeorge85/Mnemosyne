# CRITICAL DEPLOYMENT NOTES

## NEVER USE docker-compose COMMAND

**⚠️ IMPORTANT: NEVER use `docker-compose` (hyphenated)**

### Use Instead:
- `docker compose` (space, not hyphen) - for development
- `docker stack deploy` - for production (Swarm mode preferred)

### Examples:
```bash
# WRONG ❌
docker-compose up
docker-compose down

# CORRECT ✅
docker compose up
docker compose down
docker stack deploy -c docker-compose.yml mnemosyne
```

### Why:
- `docker-compose` is the old Python-based command (deprecated)
- `docker compose` is the new Go-based command integrated into Docker
- `docker stack deploy` is for production Swarm deployments

---

## Current Status
- Original Mnemosyne deployment should be down
- Ready to deploy under new protocol structure

---

*This file exists specifically to prevent using the wrong Docker commands.*