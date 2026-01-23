from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db, Competitor, SystemPrompt, KnowledgeBaseItem
from analytics import AnalyticsEngine
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
analytics_engine = AnalyticsEngine()

@router.get("/api/analytics/summary")
async def get_dashboard_summary(db: Session = Depends(get_db)):
    """Generate executive summary for the dashboard."""
    try:
        # 1. Fetch ALL active competitors
        competitors = db.query(Competitor).filter(Competitor.is_deleted == False).all()
        
        # 2. Get Custom System Prompt
        system_prompt = db.query(SystemPrompt).filter(SystemPrompt.key == "dashboard_summary").first()
        prompt_content = system_prompt.content if system_prompt else None
        
        # 3. Get Knowledge Base Context (RAG)
        kb_items = db.query(KnowledgeBaseItem).filter(KnowledgeBaseItem.is_active == True).all()
        kb_context = "\n".join([f"Note: {item.content_text}" for item in kb_items])
        
        # 4. Convert to dicts for the engine
        comp_dicts = []
        for c in competitors:
            comp_dicts.append({
                "name": c.name,
                "threat_level": c.threat_level,
                "base_price": c.base_price,
                "target_segments": c.target_segments,
                "key_features": c.key_features,
                "product_categories": c.product_categories
            })
            
        # 5. Generate Insight via Engine
        # We need to extend the insight generator to accept custom prompts and context
        # For now, we'll modify the context passed to the existing generator or handle it here if the engine doesn't support it yet.
        # Since we can't easily modify the engine instance's method signature dynamically, 
        # let's manually call the internal generator with enhanced context.
        
        if analytics_engine.insight_generator.client:
            # Custom generation logic to include RAG & System Prompt
            from openai import OpenAI
            client = analytics_engine.insight_generator.client
            
            # Prepare data context
            data_context = analytics_engine.insight_generator._prepare_context(comp_dicts)
            
            # Combine contexts
            full_user_content = f"Competitive Landscape Data:\n{data_context}\n\n"
            if kb_context:
                full_user_content += f"Internal Knowledge Base Context:\n{kb_context}\n"
                
            messages = [
                {"role": "system", "content": prompt_content or "You are a Chief Strategy Officer..."},
                {"role": "user", "content": full_user_content}
            ]
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7
            )
            
            summary_text = response.choices[0].message.content
            
            return {
                "summary": summary_text,
                "type": "ai",
                "data_points_analyzed": len(competitors),
                "generated_at": datetime.utcnow().isoformat(),
                "model": "gpt-4",
                "provider": "OpenAI"
            }
            
        else:
            # Fallback
            return analytics_engine.insight_generator.generate_insight(comp_dicts)

    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return {"error": str(e)}

@router.post("/api/analytics/chat")
async def chat_with_analytics(message: dict, db: Session = Depends(get_db)):
    """Chat with the AI about competitive intelligence."""
    user_msg = message.get("message", "")
    try:
        # Get Chat Persona
        persona = db.query(SystemPrompt).filter(SystemPrompt.key == "chat_persona").first()
        system_msg = persona.content if persona else "You are a competitive intelligence assistant."
        
        # Simple RAG: Fetch relevant KB items (naive keyword match for now, or just dump all if small)
        kb_items = db.query(KnowledgeBaseItem).filter(KnowledgeBaseItem.is_active == True).all()
        kb_context = "\n".join([f"- {item.content_text}" for item in kb_items])
        
        # Fetch Top Threats for context
        top_threats = db.query(Competitor).filter(
            Competitor.is_deleted == False, 
            Competitor.threat_level == "High"
        ).limit(5).all()
        threat_context = "\n".join([f"{c.name}: {c.notes}" for c in top_threats])
        
        from openai import OpenAI
        import os
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        context_block = f"""
        Internal Knowledge Base:
        {kb_context}
        
        Top Threats Context:
        {threat_context}
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "system", "content": f"Context data:\n{context_block}"},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.7
        )
        
        return {
            "success": True,
            "response": response.choices[0].message.content
        }
    except Exception as e:
        return {"success": False, "response": "I apologize, but I'm having trouble connecting to my brain right now. Please try again later.", "error": str(e)}

from datetime import datetime
