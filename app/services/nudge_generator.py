"""
AI Nudge Generator Service
Generates personalized WhatsApp nudges for sales reps based on their performance and pending tasks
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from app.models import Rep, Conversation, Customer
from app.services.whatsapp_api import send_text
import logging
import httpx

logger = logging.getLogger(__name__)


async def _call_ai_for_nudge(prompt: str) -> str:
    """Simple AI call for nudge generation"""
    from app.config import settings
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{settings.AI_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.AI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.AI_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 300,
                    "temperature": 0.7
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
            else:
                logger.error(f"AI API error: {response.status_code} - {response.text}")
                return None
                
    except Exception as e:
        logger.error(f"Error calling AI: {e}")
        return None


class NudgeGenerator:
    """Generate personalized AI nudges for sales reps"""
    
    @staticmethod
    async def analyze_rep_performance(db: AsyncSession, rep_id: str) -> Dict:
        """
        Analyze a rep's performance and pending tasks
        
        Returns:
            Dict with performance metrics and pending tasks
        """
        # Get rep details
        rep_result = await db.execute(
            select(Rep).where(Rep.id == rep_id)
        )
        rep = rep_result.scalar_one_or_none()
        
        if not rep:
            return None
        
        # Get conversations assigned to this rep
        conv_result = await db.execute(
            select(Conversation).where(Conversation.rep_id == rep_id)
        )
        conversations = conv_result.scalars().all()
        
        # Calculate metrics
        total_conversations = len(conversations)
        
        # Pending conversations (not resolved)
        pending_convs = [c for c in conversations if not c.is_resolved]
        pending_count = len(pending_convs)
        
        # High priority conversations (escalated or urgent)
        high_priority = [c for c in conversations if c.handler in ["escalated", "senior", "mukul"] or c.urgency == "high"]
        high_priority_count = len(high_priority)
        
        # Stale conversations (no activity in 3+ days)
        three_days_ago = datetime.utcnow() - timedelta(days=3)
        stale_convs = [
            c for c in pending_convs 
            if c.updated_at and c.updated_at < three_days_ago
        ]
        stale_count = len(stale_convs)
        
        # Recent conversations (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_convs = [
            c for c in conversations 
            if c.updated_at and c.updated_at > yesterday
        ]
        recent_count = len(recent_convs)
        
        # Get customer names for top pending conversations
        top_pending = []
        for conv in pending_convs[:5]:  # Top 5 pending
            customer_result = await db.execute(
                select(Customer).where(Customer.id == conv.customer_id)
            )
            customer = customer_result.scalar_one_or_none()
            top_pending.append({
                "customer_name": customer.name if customer else "Unknown",
                "handler": conv.handler,
                "urgency": conv.urgency,
                "updated_at": conv.updated_at,
                "topic": conv.topic
            })
        
        return {
            "rep": {
                "id": rep.id,
                "name": rep.name,
                "phone": rep.phone,
                "rep_type": rep.rep_type
            },
            "metrics": {
                "total_conversations": total_conversations,
                "pending_count": pending_count,
                "high_priority_count": high_priority_count,
                "stale_count": stale_count,
                "recent_count": recent_count
            },
            "top_pending": top_pending
        }
    
    @staticmethod
    async def generate_nudge_text(performance_data: Dict, nudge_type: str = "daily") -> str:
        """
        Generate personalized nudge text using AI
        
        Args:
            performance_data: Rep performance data from analyze_rep_performance
            nudge_type: Type of nudge (daily, urgent, weekly)
        
        Returns:
            Personalized nudge message
        """
        rep = performance_data["rep"]
        metrics = performance_data["metrics"]
        top_pending = performance_data["top_pending"]
        
        # Build context for AI
        context = f"""
Generate a personalized WhatsApp nudge for sales rep {rep['name']}.

Rep Type: {rep['rep_type']}
Current Performance:
- Total Conversations: {metrics['total_conversations']}
- Pending: {metrics['pending_count']}
- High Priority: {metrics['high_priority_count']}
- Stale (3+ days): {metrics['stale_count']}
- Recent Activity (24h): {metrics['recent_count']}

Top Pending Conversations:
"""
        
        for i, conv in enumerate(top_pending[:3], 1):
            context += f"\n{i}. {conv['customer_name']} - {conv['topic'][:50]} ({conv['handler']})"
            if conv['urgency'] == 'high':
                context += f" [URGENT]"
        
        # Different prompts based on nudge type
        if nudge_type == "morning":
            prompt = f"""{context}

Create a motivating morning briefing message (max 150 words) that:
1. Greets them warmly
2. Highlights their pending tasks
3. Prioritizes urgent items
4. Encourages action
5. Ends with motivation

Use emojis appropriately. Be professional but friendly. Focus on actionable items."""
        
        elif nudge_type == "urgent":
            prompt = f"""{context}

Create an urgent nudge message (max 100 words) that:
1. Alerts about high priority items
2. Lists specific customers needing attention
3. Creates urgency without stress
4. Provides clear next steps

Use ⚠️ emoji for urgent items. Be direct and action-oriented."""
        
        elif nudge_type == "evening":
            prompt = f"""{context}

Create an evening summary message (max 150 words) that:
1. Acknowledges today's work
2. Summarizes pending items for tomorrow
3. Highlights any urgent follow-ups
4. Ends with encouragement

Be appreciative and forward-looking."""
        
        else:  # daily
            prompt = f"""{context}

Create a daily check-in message (max 150 words) that:
1. Greets professionally
2. Lists pending conversations
3. Highlights priorities
4. Encourages progress
5. Offers support

Be supportive and action-oriented."""
        
        try:
            # Generate AI response
            ai_response = await _call_ai_for_nudge(prompt)
            
            if not ai_response:
                # Fallback to template if AI fails
                return NudgeGenerator._generate_template_nudge(performance_data, nudge_type)
            
            # Add signature
            nudge_text = f"{ai_response}\n\n---\n🤖 Hi-Tech AI Sales Assistant"
            
            return nudge_text
            
        except Exception as e:
            logger.error(f"Error generating AI nudge: {e}")
            
            # Fallback to template-based nudge
            return NudgeGenerator._generate_template_nudge(performance_data, nudge_type)
    
    @staticmethod
    def _generate_template_nudge(performance_data: Dict, nudge_type: str) -> str:
        """Fallback template-based nudge if AI fails"""
        rep = performance_data["rep"]
        metrics = performance_data["metrics"]
        top_pending = performance_data["top_pending"]
        
        if nudge_type == "morning":
            message = f"🌅 Good Morning {rep['name']}!\n\n"
            message += f"📊 Your Dashboard:\n"
            message += f"• Pending: {metrics['pending_count']} conversations\n"
            
            if metrics['high_priority_count'] > 0:
                message += f"• ⚠️ High Priority: {metrics['high_priority_count']}\n"
            
            if metrics['stale_count'] > 0:
                message += f"• 🕐 Stale (3+ days): {metrics['stale_count']}\n"
            
            if top_pending:
                message += f"\n🎯 Top Priorities:\n"
                for i, conv in enumerate(top_pending[:3], 1):
                    message += f"{i}. {conv['customer_name']} - {conv['topic'][:40]}\n"
            
            message += f"\n💪 Let's make today productive!"
        
        elif nudge_type == "urgent":
            message = f"⚠️ {rep['name']}, Urgent Items!\n\n"
            message += f"🔥 {metrics['high_priority_count']} high priority conversations need attention:\n\n"
            
            for i, conv in enumerate(top_pending[:3], 1):
                if conv['handler'] in ['escalated', 'senior', 'mukul']:
                    message += f"{i}. {conv['customer_name']} - {conv['topic'][:40]}\n"
            
            message += f"\n⏰ Please review these ASAP!"
        
        else:  # daily
            message = f"👋 Hi {rep['name']},\n\n"
            message += f"📊 Quick Update:\n"
            message += f"• Pending: {metrics['pending_count']}\n"
            message += f"• Recent Activity: {metrics['recent_count']}\n"
            
            if top_pending:
                message += f"\n📋 Top Items:\n"
                for i, conv in enumerate(top_pending[:3], 1):
                    message += f"{i}. {conv['customer_name']}\n"
            
            message += f"\n✅ Keep up the great work!"
        
        message += "\n\n---\n🤖 Hi-Tech AI Sales Assistant"
        return message
    
    @staticmethod
    async def send_nudge_to_rep(
        db: AsyncSession,
        rep_id: str,
        nudge_type: str = "daily",
        dry_run: bool = False
    ) -> Dict:
        """
        Generate and send a nudge to a specific rep
        
        Args:
            db: Database session
            rep_id: Representative ID
            nudge_type: Type of nudge (morning, daily, urgent, evening)
            dry_run: If True, generate but don't send
        
        Returns:
            Dict with status and message details
        """
        try:
            # Analyze rep performance
            performance_data = await NudgeGenerator.analyze_rep_performance(db, rep_id)
            
            if not performance_data:
                return {
                    "success": False,
                    "error": f"Rep {rep_id} not found"
                }
            
            rep = performance_data["rep"]
            
            # Check if rep has phone number
            if not rep["phone"]:
                return {
                    "success": False,
                    "error": f"Rep {rep['name']} has no phone number"
                }
            
            # Generate nudge text
            nudge_text = await NudgeGenerator.generate_nudge_text(performance_data, nudge_type)
            
            if dry_run:
                return {
                    "success": True,
                    "dry_run": True,
                    "rep": rep,
                    "nudge_text": nudge_text,
                    "metrics": performance_data["metrics"]
                }
            
            # Send via WhatsApp
            result = await send_text(
                to=rep["phone"],
                text=nudge_text
            )
            
            return {
                "success": True,
                "rep": rep,
                "nudge_text": nudge_text,
                "whatsapp_result": result,
                "metrics": performance_data["metrics"]
            }
            
        except Exception as e:
            logger.error(f"Error sending nudge to rep {rep_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    async def send_bulk_nudges(
        db: AsyncSession,
        rep_type: Optional[str] = None,
        nudge_type: str = "daily",
        dry_run: bool = False
    ) -> List[Dict]:
        """
        Send nudges to multiple reps
        
        Args:
            db: Database session
            rep_type: Filter by rep type (sales, ccare, newbiz, etc.)
            nudge_type: Type of nudge
            dry_run: If True, generate but don't send
        
        Returns:
            List of results for each rep
        """
        # Get all reps (or filtered by type)
        query = select(Rep)
        
        if rep_type:
            query = query.where(Rep.rep_type == rep_type)
        
        result = await db.execute(query)
        reps = result.scalars().all()
        
        results = []
        
        for rep in reps:
            # Skip reps without phone numbers
            if not rep.phone:
                results.append({
                    "success": False,
                    "rep_id": rep.id,
                    "rep_name": rep.name,
                    "error": "No phone number"
                })
                continue
            
            # Send nudge
            nudge_result = await NudgeGenerator.send_nudge_to_rep(
                db=db,
                rep_id=rep.id,
                nudge_type=nudge_type,
                dry_run=dry_run
            )
            
            results.append(nudge_result)
        
        return results
