"""
Premium Cover Letter Service for Pro Users

This service provides enhanced cover letter generation with premium templates,
advanced AI prompts, and Pro-only features for ApplyAI subscribers.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum

from sqlalchemy.orm import Session
from openai import AsyncOpenAI

from models.user import User
from services.subscription_service import SubscriptionService
from utils.gpt_prompt import GPTProcessor


class CoverLetterTemplate(Enum):
    """Premium cover letter templates available to Pro users"""
    PROFESSIONAL = "professional"  # General professional template
    EXECUTIVE = "executive"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    CONSULTING = "consulting"
    STARTUP = "startup"
    ACADEMIC = "academic"
    SALES = "sales"
    HEALTHCARE = "healthcare"


class CoverLetterTone(Enum):
    """Cover letter tone options for Pro users"""
    PROFESSIONAL = "professional"
    CONVERSATIONAL = "conversational"
    CONFIDENT = "confident"
    ENTHUSIASTIC = "enthusiastic"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"


class PremiumCoverLetterService:
    """Enhanced cover letter service with Pro-only features"""
    
    def __init__(self, db: Session):
        self.db = db
        self.subscription_service = SubscriptionService(db)
        self.gpt_processor = GPTProcessor()
        self.logger = logging.getLogger(__name__)
        
        # Premium templates configuration
        self.premium_templates = {
            CoverLetterTemplate.PROFESSIONAL: {
                "name": "Professional Standard",
                "description": "General professional cover letter template",
                "focus": "professional experience, skills, achievements",
                "tone": "professional and polished"
            },
            CoverLetterTemplate.EXECUTIVE: {
                "name": "Executive Leadership",
                "description": "For C-suite and senior leadership positions",
                "focus": "strategic vision, leadership experience, business impact",
                "tone": "authoritative and results-focused"
            },
            CoverLetterTemplate.CREATIVE: {
                "name": "Creative Professional",
                "description": "For design, marketing, and creative roles",
                "focus": "creativity, portfolio highlights, innovative thinking",
                "tone": "engaging and personality-driven"
            },
            CoverLetterTemplate.TECHNICAL: {
                "name": "Technical Expert",
                "description": "For engineering and technical positions",
                "focus": "technical skills, problem-solving, system architecture",
                "tone": "precise and competency-focused"
            },
            CoverLetterTemplate.CONSULTING: {
                "name": "Management Consulting",
                "description": "For consulting and strategy roles",
                "focus": "analytical thinking, client impact, problem-solving",
                "tone": "structured and results-oriented"
            },
            CoverLetterTemplate.STARTUP: {
                "name": "Startup Innovator",
                "description": "For startup and entrepreneurial roles",
                "focus": "adaptability, growth mindset, innovation",
                "tone": "dynamic and growth-focused"
            },
            CoverLetterTemplate.ACADEMIC: {
                "name": "Academic Research",
                "description": "For research and academic positions",
                "focus": "research experience, publications, academic achievements",
                "tone": "scholarly and research-focused"
            },
            CoverLetterTemplate.SALES: {
                "name": "Sales Professional",
                "description": "For sales and business development roles",
                "focus": "revenue generation, relationship building, targets",
                "tone": "persuasive and achievement-focused"
            },
            CoverLetterTemplate.HEALTHCARE: {
                "name": "Healthcare Professional",
                "description": "For medical and healthcare positions",
                "focus": "patient care, clinical experience, certifications",
                "tone": "compassionate and professional"
            }
        }
    
    async def generate_premium_cover_letter(
        self,
        user_id: str,
        resume_text: str,
        job_description: str,
        company_name: str,
        job_title: str,
        template: CoverLetterTemplate = CoverLetterTemplate.PROFESSIONAL,
        tone: CoverLetterTone = CoverLetterTone.PROFESSIONAL,
        custom_instructions: Optional[str] = None,
        include_metrics: bool = True,
        include_company_research: bool = True
    ) -> Dict:
        """
        Generate a premium cover letter with advanced features for Pro users
        
        Args:
            user_id: User ID
            resume_text: User's resume content
            job_description: Job posting description
            company_name: Target company name
            job_title: Target job title
            template: Premium template to use
            tone: Desired tone for the cover letter
            custom_instructions: Additional user instructions
            include_metrics: Whether to emphasize quantifiable achievements
            include_company_research: Whether to include company-specific insights
            
        Returns:
            Dict containing cover letter and metadata
        """
        try:
            # Verify Pro subscription
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("User not found")
            
            # Check Pro subscription status
            can_use_premium = await self.subscription_service.can_use_feature(user_id, "premium_cover_letters")
            if not can_use_premium:
                # Fall back to basic cover letter for non-Pro users
                return await self._generate_basic_cover_letter(
                    resume_text, job_description, company_name, job_title
                )
            
            # Generate premium cover letter with advanced prompt
            cover_letter_content = await self._generate_advanced_cover_letter(
                resume_text=resume_text,
                job_description=job_description,
                company_name=company_name,
                job_title=job_title,
                template=template,
                tone=tone,
                custom_instructions=custom_instructions,
                include_metrics=include_metrics,
                include_company_research=include_company_research
            )
            
            # Track usage for analytics
            await self._track_cover_letter_generation(
                user_id=user_id,
                template=template,
                tone=tone,
                success=True
            )
            
            return {
                "cover_letter": cover_letter_content,
                "template_used": template.value,
                "tone_used": tone.value,
                "premium_features": {
                    "advanced_prompts": True,
                    "custom_template": True,
                    "company_research": include_company_research,
                    "metrics_emphasis": include_metrics
                },
                "generated_at": datetime.utcnow().isoformat(),
                "word_count": len(cover_letter_content.split()),
                "character_count": len(cover_letter_content)
            }
            
        except Exception as e:
            self.logger.error(f"Premium cover letter generation failed for user {user_id}: {str(e)}")
            await self._track_cover_letter_generation(
                user_id=user_id,
                template=template,
                tone=tone,
                success=False,
                error=str(e)
            )
            raise
    
    async def _generate_advanced_cover_letter(
        self,
        resume_text: str,
        job_description: str,
        company_name: str,
        job_title: str,
        template: CoverLetterTemplate,
        tone: CoverLetterTone,
        custom_instructions: Optional[str],
        include_metrics: bool,
        include_company_research: bool
    ) -> str:
        """Generate cover letter using advanced AI prompts for Pro users"""
        
        template_config = self.premium_templates[template]
        
        # Build advanced prompt
        system_prompt = f"""You are an elite cover letter specialist with expertise in {template_config['name']} positions. You create compelling, personalized cover letters that demonstrate deep understanding of industry nuances and company culture.

TEMPLATE FOCUS: {template_config['focus']}
DESIRED TONE: {template_config['tone']}
TARGET ROLE: {job_title} at {company_name}

Your cover letters are known for:
- Industry-specific language and terminology
- Compelling storytelling that connects experience to opportunity
- Quantifiable achievements and impact metrics
- Company-specific insights and cultural alignment
- Professional yet engaging tone that stands out

Create a cover letter that positions this candidate as the ideal choice through strategic narrative and compelling evidence."""

        user_prompt = f"""
CANDIDATE RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

COMPANY: {company_name}
POSITION: {job_title}

PREMIUM REQUIREMENTS:
- Template Style: {template_config['name']} - {template_config['description']}
- Tone: {tone.value.title()}
- Focus Areas: {template_config['focus']}
{'- Emphasize quantifiable metrics and achievements' if include_metrics else ''}
{'- Include company-specific research and cultural insights' if include_company_research else ''}
{f'- Additional Instructions: {custom_instructions}' if custom_instructions else ''}

ADVANCED COVER LETTER STRUCTURE:

1. **Opening Hook** (1-2 sentences)
   - Compelling opening that immediately demonstrates fit
   - Reference specific company achievement or recent news
   - Show genuine enthusiasm for the role and company

2. **Value Proposition** (2-3 paragraphs)
   - Connect 2-3 most relevant experiences to job requirements
   - Use specific metrics and quantifiable achievements
   - Demonstrate industry knowledge and terminology
   - Show understanding of company challenges/opportunities

3. **Cultural Alignment** (1 paragraph)
   - Demonstrate understanding of company values and culture
   - Show how personal values and work style align
   - Reference company mission, recent initiatives, or leadership

4. **Forward-Looking Close** (1 paragraph)
   - Articulate specific contributions you'll make
   - Reference next steps and express eagerness to discuss
   - Professional yet confident closing

CRITICAL REQUIREMENTS:
- Use industry-specific terminology and demonstrate deep role understanding
- Include 3-4 specific, quantifiable achievements from the resume
- Reference the company by name 2-3 times naturally
- Maintain {tone.value} tone throughout
- Keep to 3-4 paragraphs, approximately 250-350 words
- Make every sentence add value - no filler content
- End with a strong call to action

Generate a premium cover letter that showcases why this candidate is the perfect fit for this specific role at this specific company.
"""

        try:
            # Use OpenAI API for advanced generation
            client = AsyncOpenAI()
            response = await self.gpt_processor.process_prompt(
                model="gpt-4",  # Use GPT-4 for premium quality
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"Advanced cover letter generation failed: {str(e)}")
            # Fallback to basic generation
            return await self._generate_basic_cover_letter(
                resume_text, job_description, company_name, job_title
            )
    
    async def _generate_basic_cover_letter(
        self,
        resume_text: str,
        job_description: str,
        company_name: str,
        job_title: str
    ) -> str:
        """Fallback to basic cover letter generation for non-Pro users"""
        return await self.gpt_prompt.generate_cover_letter(
            resume_text=resume_text,
            job_description=job_description,
            company_name=company_name,
            job_title=job_title
        )
    
    async def _track_cover_letter_generation(
        self,
        user_id: str,
        template: CoverLetterTemplate,
        tone: CoverLetterTone,
        success: bool,
        error: Optional[str] = None
    ):
        """Track cover letter generation for analytics"""
        try:
            # This will be used by the analytics service
            analytics_data = {
                "user_id": user_id,
                "feature": "premium_cover_letter",
                "template": template.value,
                "tone": tone.value,
                "success": success,
                "error": error,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Log for now - will integrate with analytics service
            self.logger.info(f"Cover letter analytics: {json.dumps(analytics_data)}")
            
        except Exception as e:
            self.logger.error(f"Failed to track cover letter analytics: {str(e)}")
    
    def get_available_templates(self, user_id: str) -> List[Dict]:
        """Get list of available templates for user based on subscription"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return []
            
            # Pro users get all templates
            if user.subscription_tier == "pro":
                return [
                    {
                        "id": template.value,
                        "name": config["name"],
                        "description": config["description"],
                        "focus": config["focus"],
                        "tone": config["tone"],
                        "premium": True
                    }
                    for template, config in self.premium_templates.items()
                ]
            else:
                # Free users get basic template only
                return [
                    {
                        "id": "basic",
                        "name": "Professional Standard",
                        "description": "Standard professional cover letter",
                        "focus": "general professional experience",
                        "tone": "professional",
                        "premium": False
                    }
                ]
                
        except Exception as e:
            self.logger.error(f"Failed to get available templates: {str(e)}")
            return []
    
    def get_available_tones(self) -> List[Dict]:
        """Get list of available tones for Pro users"""
        return [
            {
                "id": tone.value,
                "name": tone.value.title(),
                "description": self._get_tone_description(tone)
            }
            for tone in CoverLetterTone
        ]
    
    def _get_tone_description(self, tone: CoverLetterTone) -> str:
        """Get description for each tone option"""
        descriptions = {
            CoverLetterTone.PROFESSIONAL: "Formal and business-focused",
            CoverLetterTone.CONVERSATIONAL: "Friendly and approachable",
            CoverLetterTone.CONFIDENT: "Assertive and self-assured",
            CoverLetterTone.ENTHUSIASTIC: "Energetic and passionate",
            CoverLetterTone.ANALYTICAL: "Data-driven and logical",
            CoverLetterTone.CREATIVE: "Innovative and expressive"
        }
        return descriptions.get(tone, "Professional tone")
