"""
Webhook handlers for external integrations
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
import hmac
import hashlib
import json

from api.deps import get_db
from core.config import get_settings
from core.redis_client import RedisClient
from services.memory_service import MemoryService

router = APIRouter()
settings = get_settings()


# Webhook models
class WebhookEvent(BaseModel):
    event_type: str
    payload: Dict[str, Any]
    timestamp: str
    signature: Optional[str] = None


class GitHubWebhook(BaseModel):
    action: str
    repository: Optional[dict] = None
    sender: dict
    installation: Optional[dict] = None


class DiscordWebhook(BaseModel):
    type: int
    data: dict


def verify_webhook_signature(
    payload: bytes,
    signature: str,
    secret: str
) -> bool:
    """
    Verify webhook signature (GitHub style)
    """
    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(
        f"sha256={expected_signature}",
        signature
    )


@router.post("/github")
async def handle_github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Handle GitHub webhooks for repository events
    """
    # Get signature from headers
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature and settings.WEBHOOK_VERIFY_SIGNATURE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing signature"
        )
    
    # Get raw payload
    payload = await request.body()
    
    # Verify signature if configured
    if settings.WEBHOOK_VERIFY_SIGNATURE:
        if not verify_webhook_signature(
            payload,
            signature,
            settings.GITHUB_WEBHOOK_SECRET
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature"
            )
    
    # Parse event
    event_type = request.headers.get("X-GitHub-Event", "unknown")
    data = json.loads(payload)
    
    # Process based on event type
    if event_type == "push":
        # Create memory from push event
        commits = data.get("commits", [])
        if commits:
            memory_content = f"GitHub Push Event:\n"
            memory_content += f"Repository: {data['repository']['full_name']}\n"
            memory_content += f"Commits:\n"
            for commit in commits[:5]:  # Limit to 5 commits
                memory_content += f"- {commit['message'][:100]}\n"
            
            # Queue memory creation
            background_tasks.add_task(
                create_webhook_memory,
                content=memory_content,
                metadata={
                    "source": "github",
                    "event": event_type,
                    "repository": data['repository']['full_name']
                },
                db=db
            )
    
    elif event_type == "issues":
        action = data.get("action")
        issue = data.get("issue", {})
        
        if action in ["opened", "closed"]:
            memory_content = f"GitHub Issue {action.capitalize()}:\n"
            memory_content += f"Title: {issue.get('title', 'Unknown')}\n"
            memory_content += f"Number: #{issue.get('number', 'Unknown')}\n"
            
            background_tasks.add_task(
                create_webhook_memory,
                content=memory_content,
                metadata={
                    "source": "github",
                    "event": event_type,
                    "action": action,
                    "issue_number": issue.get('number')
                },
                db=db
            )
    
    return {"message": "Webhook processed", "event": event_type}


@router.post("/discord")
async def handle_discord_webhook(
    webhook_data: DiscordWebhook,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Handle Discord webhooks for bot events
    """
    # Process based on event type
    if webhook_data.type == 1:  # PING
        return {"type": 1}  # PONG
    
    elif webhook_data.type == 2:  # APPLICATION_COMMAND
        command = webhook_data.data.get("name")
        options = webhook_data.data.get("options", [])
        
        # Create memory from command
        memory_content = f"Discord Command: /{command}\n"
        if options:
            memory_content += f"Options: {options}\n"
        
        background_tasks.add_task(
            create_webhook_memory,
            content=memory_content,
            metadata={
                "source": "discord",
                "command": command,
                "options": options
            },
            db=db
        )
        
        return {
            "type": 4,  # CHANNEL_MESSAGE_WITH_SOURCE
            "data": {
                "content": f"Command `{command}` processed and stored in memory"
            }
        }
    
    return {"message": "Webhook processed"}


@router.post("/generic")
async def handle_generic_webhook(
    event: WebhookEvent,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    redis: RedisClient = Depends(get_redis)
) -> Any:
    """
    Handle generic webhooks with custom event types
    """
    # Rate limiting
    rate_limit_key = f"webhook_rate:{event.event_type}"
    count = await redis.client.incr(rate_limit_key)
    if count == 1:
        await redis.client.expire(rate_limit_key, 60)  # 1 minute window
    
    if count > 10:  # Max 10 events per minute per type
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    # Process based on event type
    if event.event_type.startswith("memory."):
        # Memory-related events
        memory_content = f"Webhook Event: {event.event_type}\n"
        memory_content += f"Payload: {json.dumps(event.payload, indent=2)[:500]}\n"
        
        background_tasks.add_task(
            create_webhook_memory,
            content=memory_content,
            metadata={
                "source": "webhook",
                "event_type": event.event_type,
                "timestamp": event.timestamp
            },
            db=db
        )
    
    elif event.event_type.startswith("agent."):
        # Agent-related events
        # Could trigger agent reflections based on webhook data
        pass
    
    # Store event in Redis for processing
    event_key = f"webhook_event:{event.event_type}:{event.timestamp}"
    await redis.client.setex(
        event_key,
        3600,  # Keep for 1 hour
        json.dumps(event.model_dump())
    )
    
    return {
        "message": "Webhook received",
        "event_type": event.event_type,
        "processed": True
    }


async def create_webhook_memory(
    content: str,
    metadata: dict,
    db: AsyncSession
) -> None:
    """
    Background task to create memory from webhook
    """
    try:
        memory_service = MemoryService(db)
        
        # Get system user or first user (for MVP)
        # In production, webhooks would be associated with specific users
        from sqlalchemy import select
        from models.user import User
        
        result = await db.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        
        if user:
            await memory_service.create_memory(
                user_id=user.id,
                content=content,
                metadata=metadata,
                importance=0.3  # Lower importance for automated captures
            )
    except Exception as e:
        print(f"Error creating webhook memory: {e}")


@router.get("/test")
async def test_webhook() -> Any:
    """
    Test endpoint to verify webhook configuration
    """
    return {
        "status": "active",
        "endpoints": [
            "/webhooks/github",
            "/webhooks/discord",
            "/webhooks/generic"
        ],
        "signature_verification": settings.WEBHOOK_VERIFY_SIGNATURE
    }