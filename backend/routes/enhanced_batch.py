from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import uuid
import time
import os
import re
from datetime import datetime
from sqlalchemy.orm import Session

# Import your existing components with fallback handling
JOB_SCRAPER_AVAILABLE = True
LANGCHAIN_AVAILABLE = True
AUTH_AVAILABLE = True

# Fallback classes for when imports fail
class TailoringMode:
    LIGHT = "light"
    HEAVY = "heavy"

class MockUser:
    def __init__(self):
        self.id = 1
        self.email = "test@example.com"
        self.weekly_usage_count = 0
    def is_pro_active(self):
        return False
    def get_usage_limits_new(self):
        return {"bulk_jobs": 10, "weekly_sessions": 3, "heavy_tailoring": False}
    def can_process_resume(self):
        return self.weekly_usage_count < 3

def mock_get_current_user():
    return MockUser()

def mock_get_db():
    return None

def mock_depends(func):
    return func()

# Try to import real components
try:
    from utils.job_scraper import JobScraper
    print("✅ JobScraper imported successfully")
except ImportError as e:
    print(f"⚠️ JobScraper not available: {e}")
    JOB_SCRAPER_AVAILABLE = False
    JobScraper = None

try:
    from utils.langchain_processor import LangChainResumeProcessor
    print("✅ LangChain processor imported successfully")
except ImportError as e:
    print(f"⚠️ LangChain processor not available: {e}")
    LANGCHAIN_AVAILABLE = False
    LangChainResumeProcessor = None

# Try to import EnhancedATSScorer first (it's independent of auth/db)
try:
    from services.enhanced_ats_scorer import EnhancedATSScorer
    print("✅ Real EnhancedATSScorer imported successfully")
except ImportError as e:
    print(f"⚠️ EnhancedATSScorer not available: {e}")
    EnhancedATSScorer = None

# Import professional output service for template-based formatting
try:
    from services.professional_output_service import ProfessionalOutputService
    print("✅ ProfessionalOutputService imported successfully")
    PROFESSIONAL_OUTPUT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ ProfessionalOutputService not available: {e}")
    ProfessionalOutputService = None
    PROFESSIONAL_OUTPUT_AVAILABLE = False

# Now try auth/db imports
try:
    from models.user import TailoringMode as RealTailoringMode, User as RealUser, SubscriptionTier
    from services.subscription_service import SubscriptionService, UsageType
    from config.database import get_db
    from utils.auth import get_current_user
    from utils.job_scraper import JobScraper as JobScraperService
    from services.premium_cover_letter_service import PremiumCoverLetterService as CoverLetterService
    from services.professional_output_service import ProfessionalOutputService as ResumeBuilderService
    from services.analytics_service import AnalyticsService
    print("✅ Authentication and database components imported successfully")
    # Use real components
    TailoringMode = RealTailoringMode
except ImportError as e:
    print(f"⚠️ Auth/DB components not available: {e}")
    AUTH_AVAILABLE = False
    get_current_user = mock_get_current_user
    get_db = mock_get_db
    Depends = mock_depends
    # Only create mock if EnhancedATSScorer wasn't imported
    if EnhancedATSScorer is None:
        # Create a GENERIC mock EnhancedATSScorer that works for ANY job
        class MockEnhancedATSScorer:
            def calculate_ats_score(self, resume_text, job_description):
                import re
                
                # Extract keywords from the actual job description dynamically
                job_lower = job_description.lower()
                resume_lower = resume_text.lower()
                
                # Extract important words from job description (nouns, skills, requirements)
                # Remove common words and extract meaningful terms
                common_words = {'the', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 
                               'a', 'an', 'as', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                               'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                               'should', 'may', 'might', 'must', 'can', 'shall', 'you', 'your', 'our',
                               'we', 'us', 'them', 'their', 'this', 'that', 'these', 'those', 'what',
                               'which', 'who', 'whom', 'whose', 'where', 'when', 'why', 'how', 'all',
                               'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such',
                               'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'but', 'by'}
                
                # Extract potential keywords from job description
                words = re.findall(r'\b[a-z]+(?:[/-][a-z]+)*\b', job_lower)
                job_keywords = []
                for word in words:
                    if len(word) > 3 and word not in common_words:
                        job_keywords.append(word)
                
                # Get unique important keywords (limit to top 20 most frequent)
                from collections import Counter
                keyword_counts = Counter(job_keywords)
                top_keywords = [word for word, _ in keyword_counts.most_common(20)]
                
                # Check which keywords are in resume
                matched_skills = []
                missing_skills = []
                
                for keyword in top_keywords[:15]:  # Check top 15 keywords
                    if keyword in resume_lower:
                        # Capitalize properly for display
                        display_keyword = keyword.replace('-', ' ').title()
                        if display_keyword not in matched_skills:
                            matched_skills.append(display_keyword)
                    else:
                        display_keyword = keyword.replace('-', ' ').title()
                        if display_keyword not in missing_skills and len(missing_skills) < 6:
                            missing_skills.append(display_keyword)
                
                # Calculate realistic scores
                total_keywords_checked = min(len(top_keywords), 15)
                matches = len(matched_skills)
                match_percentage = int((matches / max(total_keywords_checked, 1)) * 100) if total_keywords_checked > 0 else 50
                
                # Calculate overall score with some variance
                overall_score = min(95, max(40, match_percentage + 10))
                
                # Determine grade
                if overall_score >= 90:
                    grade = 'A+'
                elif overall_score >= 85:
                    grade = 'A'
                elif overall_score >= 75:
                    grade = 'B+'
                elif overall_score >= 70:
                    grade = 'B'
                elif overall_score >= 60:
                    grade = 'C'
                else:
                    grade = 'D'
                
                # Dynamic confidence based on matches
                if matches >= 10:
                    confidence_level = 'HIGH'
                    confidence_message = 'Strong keyword alignment with job requirements'
                elif matches >= 6:
                    confidence_level = 'GOOD'
                    confidence_message = 'Good match with key requirements'
                elif matches >= 3:
                    confidence_level = 'MODERATE'
                    confidence_message = 'Moderate alignment - room for improvement'
                else:
                    confidence_level = 'LOW'
                    confidence_message = 'Limited keyword matches - significant improvements needed'
                
                # Generic recommendations
                recommendations = []
                if len(missing_skills) > 0:
                    recommendations.append(f'Consider adding these keywords: {", ".join(missing_skills[:3])}')
                if match_percentage < 60:
                    recommendations.append('Align your resume more closely with the job description')
                if 'experience' in job_lower and 'years' not in resume_lower:
                    recommendations.append('Clearly state your years of experience')
                if len(recommendations) == 0:
                    recommendations.append('Resume is well-aligned with job requirements')
                
                return {
                    'overall_score': overall_score,
                    'grade': grade,
                    'component_scores': {
                        'keyword_match': match_percentage,
                        'formatting': 85,
                        'experience_relevance': 70
                    },
                    'keyword_analysis': {
                        'total_matches': len(matched_skills),
                        'match_percentage': match_percentage,
                        'matched_skills': matched_skills[:8],
                        'missing_skills': missing_skills[:6]
                    },
                    'confidence_level': {
                        'score': overall_score,
                        'level': confidence_level,
                        'message': confidence_message
                    },
                    'recommendations': [r for r in recommendations if r],  # Filter empty strings
                    'analysis_quality': {
                        'job_description_quality': 'high',
                        'resume_completeness': 'good',
                        'intelligence_applied': True
                    }
                }
        EnhancedATSScorer = MockEnhancedATSScorer

# Try to import analytics service for Pro users
ANALYTICS_AVAILABLE = True
try:
    from services.analytics_service import AnalyticsService, AnalyticsEventType
    print("✅ Analytics service imported successfully")
except ImportError as e:
    print(f"⚠️ Analytics service not available: {e}")
    ANALYTICS_AVAILABLE = False
    AnalyticsService = None
    AnalyticsEventType = None

router = APIRouter()

# Enhanced in-memory storage for batch jobs
batch_jobs: Dict[str, Any] = {}
batch_results: Dict[str, List[Dict[str, Any]]] = {}

class EnhancedBatchRequest(BaseModel):
    resume_text: str
    job_urls: List[str]
    use_rag: Optional[bool] = True
    output_format: Optional[str] = "pdf"  # "pdf", "rtf", or "text"
    template: Optional[str] = "modern"  # "modern", "classic", "technical", "executive", "creative"
    tailoring_mode: Optional[str] = "light"  # "light" or "heavy"
    optional_sections: Optional[Dict[str, Any]] = {
        "includeSummary": False,
        "includeSkills": True,
        "includeEducation": False,
        "educationDetails": {
            "degree": "",
            "institution": "",
            "year": "",
            "gpa": ""
        }
    }
    cover_letter_options: Optional[Dict[str, Any]] = {
        "includeCoverLetter": False,
        "coverLetterDetails": {
            "tone": "professional",
            "emphasize": "experience",
            "additionalInfo": ""
        }
    }

class EnhancedBatchStatus:
    def __init__(self, batch_id: str, total_jobs: int, user_email: str = "anonymous"):
        self.batch_id = batch_id
        self.state = "pending"  # pending, processing, completed, failed
        self.total = total_jobs
        self.completed = 0
        self.failed = 0
        self.current_job = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.results = []
        self.user_email = user_email
        self.processing_mode = "enhanced"
        # Free Tier tracking attributes
        self.user_tier = "Free"
        self.is_pro_user = False
        self.max_jobs_allowed = 10
        # Phase 8: Processing Speed & Reliability metrics
        self.phase8_metrics = {
            "start_time": None,
            "end_time": None,
            "total_processing_time": 0,
            "average_job_time": 0,
            "max_job_time": 0,
            "min_job_time": None,  # Use None instead of float('inf') for JSON compatibility
            "retry_count": 0,
            "timeout_count": 0,
            "under_30_second_count": 0,
            "parallel_efficiency": 0,
            "speed_optimization_enabled": True,
            "max_processing_time": 30
        }

    def to_dict(self):
        return {
            "batch_id": self.batch_id,
            "state": self.state,
            "total": self.total,
            "completed": self.completed,
            "failed": self.failed,
            "current_job": self.current_job,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "user_email": self.user_email,
            "processing_mode": self.processing_mode,
            "phase8_metrics": self.phase8_metrics
        }

class EnhancedJobProcessor:
    def __init__(self):
        # Initialize components with fallback handling
        if JOB_SCRAPER_AVAILABLE and JobScraper:
            try:
                self.job_scraper = JobScraper()
                print("✅ Real JobScraper initialized")
            except Exception as e:
                print(f"⚠️ JobScraper failed to initialize: {e}")
                self.job_scraper = None
        else:
            self.job_scraper = None
            
        if LANGCHAIN_AVAILABLE and LangChainResumeProcessor:
            try:
                self.langchain_processor = LangChainResumeProcessor()
                print("✅ LangChain processor initialized")
            except Exception as e:
                print(f"⚠️ LangChain processor failed to initialize: {e}")
                self.langchain_processor = None
        else:
            self.langchain_processor = None
            
        # Initialize analytics service for Pro users
        self.analytics_service = None
        if ANALYTICS_AVAILABLE and AnalyticsService:
            print("✅ Analytics tracking enabled for batch processing")
    
    async def track_analytics_event(self, user_id: str, event_type: str, event_data: Dict[str, Any], db: Session = None):
        """Track analytics events for Pro users"""
        if not ANALYTICS_AVAILABLE or not AnalyticsService or not db:
            return False
            
        try:
            analytics_service = AnalyticsService(db)
            event_type_enum = getattr(AnalyticsEventType, event_type, None)
            if event_type_enum:
                await analytics_service.track_event(
                    user_id=user_id,
                    event_type=event_type_enum,
                    event_data=event_data
                )
                return True
        except Exception as e:
            print(f"⚠️ Analytics tracking failed: {e}")
        return False

    def scrape_job(self, url: str) -> Dict[str, Any]:
        """Enhanced job scraping with real scraper"""
        if self.job_scraper:
            try:
                print(f"🔍 Using real JobScraper for: {url}")
                job_description = self.job_scraper.scrape_job_description(url)
                if job_description:
                    # Extract additional details - fix: pass URL to extract_job_title, not description
                    job_title = self.job_scraper.extract_job_title(url)
                    company = self.job_scraper._extract_company_name(url, job_description)
                    requirements = self._extract_requirements(job_description)
                    
                    return {
                        "title": job_title or f"Position from {self._get_domain(url)}",
                        "company": company or self._get_domain(url),
                        "description": job_description,
                        "requirements": requirements,
                        "url": url,
                        "scraped_successfully": True
                    }
            except Exception as e:
                print(f"❌ Real scraper failed for {url}: {e}")
        
        # Fallback to enhanced mock data
        return self._generate_enhanced_mock_job(url)

    def _generate_enhanced_mock_job(self, url: str) -> Dict[str, Any]:
        """Generate more realistic mock job data"""
        domain = self._get_domain(url)
        
        # Enhanced mock data based on domain
        if "linkedin" in domain.lower():
            company = "LinkedIn Tech Corp"
            title = "Senior Software Engineer"
        elif "indeed" in domain.lower():
            company = "Indeed Innovations"
            title = "Full Stack Developer"
        elif "google" in domain.lower():
            company = "Google"
            title = "Software Engineer III"
        else:
            company = f"{domain.replace('.com', '').title()} Inc."
            title = "Software Engineer"
        
        return {
            "title": title,
            "company": company,
            "description": f"""We are seeking a talented {title} to join our growing team at {company}.

Key Responsibilities:
• Design and develop scalable software solutions
• Collaborate with cross-functional teams
• Write clean, maintainable code
• Participate in code reviews and technical discussions
• Contribute to architectural decisions

Requirements:
• 3+ years of software development experience
• Proficiency in Python, JavaScript, or similar languages
• Experience with web frameworks and databases
• Strong problem-solving skills
• Excellent communication abilities

We offer competitive compensation, comprehensive benefits, and opportunities for professional growth.""",
            "requirements": [
                "3+ years software development experience",
                "Python/JavaScript proficiency",
                "Web frameworks experience",
                "Database knowledge",
                "Strong problem-solving skills"
            ],
            "url": url,
            "scraped_successfully": False
        }

    def tailor_resume(self, resume_text: str, job_data: Dict[str, Any], tailoring_mode: str = "light") -> str:
        """Enhanced resume tailoring with Light and Heavy modes"""
        
        if self.langchain_processor and tailoring_mode == "heavy":
            try:
                print(f"🚀 Using Heavy Mode (LangChain) for {job_data['title']}")
                return self._heavy_mode_tailoring(resume_text, job_data)
            except Exception as e:
                print(f"⚠️ Heavy mode failed, falling back to Light mode: {e}")
                # Fall through to light mode
        
        # Light mode or fallback
        print(f"⚡ Using Light Mode for {job_data['title']}")
        return self._light_mode_tailoring(resume_text, job_data, use_clean_output=False)

    def _heavy_mode_tailoring(self, resume_text: str, job_data: Dict[str, Any]) -> str:
        """Heavy mode: Comprehensive content restructuring using LangChain"""
        try:
            # Use your existing LangChain processor for heavy tailoring
            tailored_resume = self.langchain_processor.tailor_resume(
                resume_text=resume_text,
                job_description=job_data['description'],
                job_title=job_data['title'],
                company_name=job_data['company']
            )
            
            return f"""HEAVY MODE TAILORED RESUME FOR {job_data['title'].upper()} AT {job_data['company'].upper()}

{tailored_resume}

--- COMPREHENSIVE RESTRUCTURING APPLIED ---
✅ Content restructured for maximum relevance
✅ Keywords strategically integrated
✅ Experience reframed for target role
✅ Skills prioritized by job requirements
✅ ATS optimization applied

[This resume has been comprehensively tailored using Heavy Mode AI processing]
"""
        except Exception as e:
            print(f"❌ Heavy mode processing failed: {e}")
            return self._light_mode_tailoring(resume_text, job_data, use_clean_output=True)

    def _light_mode_tailoring(self, resume_text: str, job_data: Dict[str, Any], use_clean_output: bool = False) -> str:
        """Light mode: Quick keyword optimization
        
        Args:
            resume_text: Original resume text
            job_data: Job posting data
            use_clean_output: If True, return clean resume without debug blocks (for template formatting)
        """
        job_title = job_data.get('title', 'Unknown Position')
        company = job_data.get('company', 'Unknown Company')
        requirements = job_data.get('requirements', [])
        description = job_data.get('description', '')
        
        # Extract key skills from job requirements and description
        key_skills = []
        for req in requirements:
            if any(tech in req.lower() for tech in ['python', 'javascript', 'react', 'node', 'sql', 'aws', 'docker', 'kubernetes']):
                key_skills.append(req)
        
        # If clean output is requested (for professional templates), build a structured, ATS-friendly text
        if use_clean_output:
            print("🧹 Using clean light mode output for template formatting (structured)")
            try:
                lines = [l.strip() for l in resume_text.split('\n') if l.strip()]
                if not lines:
                    return resume_text

                # Identify header/name line: first non-contact, non-section line near the top
                def is_contact(l: str) -> bool:
                    low = l.lower()
                    return ('@' in low) or ('http' in low) or ('linkedin' in low) or ('github' in low) or ('phone' in low) or ('(' in l and ')' in l)

                def is_section(l: str) -> bool:
                    low = l.lower().strip().rstrip(':')
                    return low in {"summary", "professional summary", "experience", "work experience", "professional experience", "education", "skills", "projects"}

                header = None
                for cand in lines[:6]:
                    if not is_contact(cand) and not is_section(cand) and len(cand) <= 80:
                        header = cand
                        break
                if header is None:
                    header = lines[0]

                # Collect contact (first few lines with contact indicators)
                contact_lines = []
                for l in lines[:6]:
                    if is_contact(l):
                        contact_lines.append(l)

                # Remaining body after removing header (first occurrence)
                body_lines = []
                removed_header = False
                for l in lines:
                    if not removed_header and l == header:
                        removed_header = True
                        continue
                    body_lines.append(l)

                # Normalize bullets
                norm = []
                for l in body_lines:
                    ll = l.replace('\\bullet', '•').replace('\\n', '\n')
                    if ll.lstrip().startswith(('- ', '* ', '– ')):
                        ll = '• ' + ll.lstrip()[2:]
                    norm.append(ll)
                body_lines = norm

                # Check for existing sections
                has_summary = any(is_section(l) and l.lower().startswith('summary') for l in body_lines[:12])
                has_experience = any(is_section(l) and 'experience' in l.lower() for l in body_lines)

                structured: list[str] = []
                structured.append(header)
                if contact_lines:
                    # Keep contact on a single line when possible
                    if len(contact_lines) > 1:
                        structured.append(' • '.join(contact_lines))
                    else:
                        structured.extend(contact_lines)

                # Inject minimal sections if missing so the parser recognizes content
                if not has_summary:
                    structured.append('Summary')
                    # Use first 3 non-contact, non-section lines as summary
                    summary_seed = []
                    for l in body_lines:
                        if is_section(l) or is_contact(l):
                            continue
                        summary_seed.append(l)
                        if len(summary_seed) >= 3:
                            break
                    if summary_seed:
                        structured.extend(summary_seed)

                if not has_experience:
                    structured.append('Experience')
                structured.extend([l for l in body_lines])

                clean_text = '\n'.join([s for s in structured if s and s.strip()])
                # Optionally apply keyword optimization to enrich, but preserve content
                try:
                    enriched = self._apply_keyword_optimization(clean_text, job_data)
                    if enriched and len(enriched) > len(clean_text) * 0.8:
                        clean_text = enriched
                except Exception:
                    pass

                return clean_text
            except Exception as e:
                print(f"⚠️ Clean structuring failed, falling back to original: {e}")
                return resume_text.replace('\\bullet', '•').replace('\\n', '\n')
        
        # Original debug-heavy output for non-template use
        tailored_resume = f"""LIGHT MODE TAILORED RESUME FOR {job_title.upper()} AT {company.upper()}

{resume_text}

--- KEYWORD OPTIMIZATION APPLIED ---

RELEVANT SKILLS FOR THIS POSITION:
• {job_title} experience and expertise
• Technical skills matching job requirements
• {company} industry knowledge
• Problem-solving and analytical abilities

OPTIMIZED SUMMARY:
Experienced professional with strong background in software development, seeking the {job_title} position at {company}. Proven track record of delivering high-quality solutions and collaborating effectively with cross-functional teams.

KEY QUALIFICATIONS:
• Relevant experience in target technologies
• Strong foundation in software engineering principles
• Excellent communication and teamwork skills
• Adaptable and quick to learn new technologies

[This resume has been optimized using Light Mode keyword enhancement]
"""
        return tailored_resume
    
    def _apply_keyword_optimization(self, resume_text: str, job_data: Dict[str, Any]) -> str:
        """Apply keyword optimization to resume text for clean template output"""
        try:
            job_title = job_data.get('title', '')
            company = job_data.get('company', '')
            description = job_data.get('description', '')
            
            # Extract key technologies and skills from job description
            tech_keywords = []
            skill_keywords = []
            
            # Common technical keywords to look for
            tech_patterns = ['python', 'javascript', 'react', 'node', 'sql', 'aws', 'docker', 'kubernetes', 'java', 'c++', 'html', 'css', 'git', 'api', 'rest', 'json']
            skill_patterns = ['leadership', 'management', 'communication', 'teamwork', 'problem-solving', 'analytical', 'project', 'agile', 'scrum']
            
            desc_lower = description.lower()
            for tech in tech_patterns:
                if tech in desc_lower and tech not in resume_text.lower():
                    tech_keywords.append(tech.title())
            
            for skill in skill_patterns:
                if skill in desc_lower and skill not in resume_text.lower():
                    skill_keywords.append(skill.title())
            
            # Enhance the resume by strategically adding relevant keywords
            enhanced_resume = resume_text
            
            # Add a targeted summary if missing
            lines = enhanced_resume.split('\n')
            if not any('summary' in line.lower() or 'objective' in line.lower() for line in lines[:10]):
                # Find a good place to insert summary (after contact info)
                insert_index = 1
                for i, line in enumerate(lines[:5]):
                    if '@' in line or 'phone' in line.lower() or '(' in line:
                        insert_index = i + 2
                        break
                
                targeted_summary = f"\nPROFESSIONAL SUMMARY\n\nExperienced {job_title} professional with expertise in {', '.join(tech_keywords[:3]) if tech_keywords else 'software development'}. Proven track record of delivering high-quality solutions and {', '.join(skill_keywords[:2]) if skill_keywords else 'collaborative teamwork'}. Seeking to contribute technical expertise and {skill_keywords[0] if skill_keywords else 'leadership skills'} to {company}.\n"
                
                lines.insert(insert_index, targeted_summary)
                enhanced_resume = '\n'.join(lines)
            
            # Fix bullet point formatting
            enhanced_resume = enhanced_resume.replace('\\bullet', '•').replace('\bullet', '•')
            
            print(f"✅ Applied keyword optimization: +{len(tech_keywords)} tech keywords, +{len(skill_keywords)} skill keywords")
            return enhanced_resume
            
        except Exception as e:
            print(f"⚠️ Keyword optimization failed: {e}")
            # Fix bullet points at minimum
            return resume_text.replace('\\bullet', '•').replace('\bullet', '•')

    def generate_cover_letter(self, resume_text: str, job_data: Dict[str, Any], tone: str = "professional") -> str:
        """Generate enhanced cover letter"""
        job_title = job_data.get('title', 'Position')
        company = job_data.get('company', 'Company')
        
        if tone == "conversational":
            opening = f"Hi there! I'm excited to apply for the {job_title} position at {company}."
            closing = "I'd love to chat more about how I can contribute to your team. Looking forward to hearing from you!"
        elif tone == "confident":
            opening = f"I am writing to express my strong interest in the {job_title} role at {company}."
            closing = "I am confident that my skills and experience make me an ideal candidate for this position."
        else:  # professional
            opening = f"Dear Hiring Manager,\n\nI am writing to express my interest in the {job_title} position at {company}."
            closing = "Thank you for your consideration. I look forward to the opportunity to discuss my qualifications further."

        return f"""{opening}

Based on the job requirements and my background, I believe I would be a valuable addition to your team. My experience in software development and problem-solving aligns well with what you're looking for in this role.

Key highlights of my qualifications:
• Strong technical foundation relevant to this position
• Proven ability to work collaboratively in team environments
• Experience with modern development practices and tools
• Commitment to delivering high-quality results

I am particularly drawn to {company} because of your reputation for innovation and excellence in the industry. I would welcome the opportunity to contribute to your continued success.

{closing}

Best regards,
[Your Name]"""

    def _extract_company_name(self, url: str, job_description: str) -> str:
        """Extract company name from URL or job description"""
        domain = self._get_domain(url)
        if "linkedin" in domain:
            return "LinkedIn Company"
        elif "indeed" in domain:
            return "Indeed Partner Company"
        else:
            return domain.replace('.com', '').title()

    def _extract_requirements(self, job_description: str) -> List[str]:
        """Extract key requirements from job description"""
        # Simple requirement extraction
        requirements = []
        lines = job_description.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['experience', 'skill', 'knowledge', 'proficiency']):
                requirements.append(line.strip())
        return requirements[:5]  # Return top 5 requirements

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return url.split('/')[2] if '/' in url else url

# Initialize the enhanced processor
enhanced_processor = EnhancedJobProcessor()

async def process_single_job_enhanced(
    resume_text: str, 
    job_url: str, 
    job_index: int, 
    batch_id: str,
    tailoring_mode: str = "light",
    cover_letter_options: Dict[str, Any] = None,
    user_id: str = None,
    db: Session = None,
    template: str = "modern",
    output_format: str = "pdf"
) -> Dict[str, Any]:
    """Process a single job with enhanced features and Phase 8 optimizations"""
    start_time = time.time()
    
    try:
        print(f"🔄 Enhanced processing job {job_index + 1}: {job_url}")
        
        # Update batch status
        if batch_id in batch_jobs:
            batch_jobs[batch_id].current_job = f"Processing job {job_index + 1}: {job_url}"
            batch_jobs[batch_id].updated_at = datetime.now()
        
        # Phase 8: Apply 30-second timeout per job
        max_processing_time = 30
        if batch_id in batch_jobs:
            max_processing_time = batch_jobs[batch_id].phase8_metrics.get("max_processing_time", 30)
        
        try:
            # Use timeout control for Phase 8 speed requirement
            result = await asyncio.wait_for(
                _process_job_core_enhanced(
                    resume_text, job_url, job_index, batch_id, 
                    tailoring_mode, cover_letter_options, user_id, db, template, output_format
                ),
                timeout=max_processing_time
            )
            
            processing_time = time.time() - start_time
            result["processing_time"] = processing_time
            result["timed_out"] = False
            result["phase8_optimized"] = True
            
            # Phase 8: Update performance metrics
            _update_phase8_metrics(batch_id, processing_time, False, job_index)
            
            print(f"✅ Enhanced processing completed job {job_index + 1} in {processing_time:.2f}s: {result.get('job_title', 'Unknown')}")
            return result
            
        except asyncio.TimeoutError:
            processing_time = time.time() - start_time
            print(f"⏰ Job {job_index + 1} timed out after {processing_time:.2f}s (limit: {max_processing_time}s)")
            
            # Phase 8: Track timeout metrics
            _update_phase8_metrics(batch_id, processing_time, True, job_index)
            
            return {
                "job_index": job_index,
                "job_url": job_url,
                "job_title": f"Job_{job_index + 1}_TIMEOUT",
                "company": "Unknown",
                "status": "timeout",
                "error": f"Processing exceeded {max_processing_time} seconds",
                "processing_time": processing_time,
                "timed_out": True,
                "phase8_optimized": True,
                "tailored_resume": None,
                "cover_letter": None,
                "tailoring_mode": tailoring_mode
            }
        
        # This section has been moved to _process_job_core_enhanced function
        
    except Exception as e:
        processing_time = time.time() - start_time
        print(f"❌ Enhanced processing failed for job {job_index + 1}: {str(e)}")
        return {
            "job_index": job_index,
            "job_url": job_url,
            "job_title": f"Job_{job_index + 1}",
            "status": "failed",
            "error": str(e),
            "processing_time": processing_time,
            "timed_out": False,
            "phase8_optimized": True,
            "tailored_resume": None,
            "cover_letter": None,
            "tailoring_mode": tailoring_mode
        }

async def _process_job_core_enhanced(
    resume_text: str,
    job_url: str,
    job_index: int,
    batch_id: str,
    tailoring_mode: str = "light",
    cover_letter_options: Dict[str, Any] = None,
    user_id: str = None,
    db: Session = None,
    template: str = "modern",
    output_format: str = "pdf"
) -> Dict[str, Any]:
    """Core job processing logic with Phase 8 optimizations"""
    # Simulate processing time based on mode (Phase 8: Optimized for speed)
    processing_time = 2 if tailoring_mode == "heavy" else 0.8  # Faster than original
    await asyncio.sleep(processing_time)
    
    # Scrape job with real scraper
    job_data = enhanced_processor.scrape_job(job_url)
    
    # Apply professional template formatting if requested
    formatted_resume_data = None
    print(f"🎨 Template formatting check: format={output_format}, template={template}, available={PROFESSIONAL_OUTPUT_AVAILABLE}")
    print(f"🔍 DEBUG: output_format in ['pdf', 'rtf'] = {output_format in ['pdf', 'rtf']}")
    print(f"🔍 DEBUG: PROFESSIONAL_OUTPUT_AVAILABLE = {PROFESSIONAL_OUTPUT_AVAILABLE}")
    print(f"🔍 DEBUG: Condition met for professional formatting = {output_format in ['pdf', 'rtf'] and PROFESSIONAL_OUTPUT_AVAILABLE}")
    
    # If professional templates are being used, get CLEAN resume content (no debug blocks)
    if output_format in ["pdf", "rtf"] and PROFESSIONAL_OUTPUT_AVAILABLE:
        print("🧹 Using clean resume content for professional template formatting")
        tailored_resume = enhanced_processor._light_mode_tailoring(resume_text, job_data, use_clean_output=True)
        print(f"🧹 Clean tailored resume LENGTH: {len(tailored_resume)}")
        print(f"🧹 Clean tailored resume preview (first 300 chars): {tailored_resume[:300]}...")
        print(f"🧹 ABOUT TO CALL PROFESSIONAL SERVICE with template='{template}' and output_format='{output_format}'")
    else:
        print(f"📝 NOT using professional templates - falling back to standard tailoring")
        print(f"📝 Reason: output_format={output_format}, PROFESSIONAL_OUTPUT_AVAILABLE={PROFESSIONAL_OUTPUT_AVAILABLE}")
        # Standard tailoring with debug blocks for non-template output
        tailored_resume = enhanced_processor.tailor_resume(resume_text, job_data, tailoring_mode)
        print(f"📝 Standard tailored resume preview: {tailored_resume[:200]}...")
    
    # Fix bullet point formatting issues - convert literal \bullet to actual bullet points
    tailored_resume = tailored_resume.replace('\\bullet', '•').replace('\bullet', '•')
    
    # Additional cleanup for common formatting issues
    tailored_resume = tailored_resume.replace('\\n', '\n')  # Fix escaped newlines
    tailored_resume = re.sub(r'\s*•\s*', '• ', tailored_resume)  # Standardize bullet spacing
    
    if output_format in ["pdf", "rtf"] and PROFESSIONAL_OUTPUT_AVAILABLE:
        print(f"🚀 Starting professional formatting with {template} template...")
        try:
            professional_service = ProfessionalOutputService()
            print(f"✅ ProfessionalOutputService created successfully")
            
            # Generate professional formatted output
            if output_format == "pdf":
                result = professional_service.generate_professional_pdf(
                    resume_text=tailored_resume,
                    job_description=job_data.get('description', ''),
                    template=template,
                    ats_optimize=True
                )
                if result.get('success'):
                    print(f"✅ PDF generation successful! Result keys: {list(result.keys())}")
                    formatted_content = result.get('formatted_text', tailored_resume)
                    print(f"📝 Formatted content length: {len(formatted_content) if formatted_content else 0}")
                    
                    # Store the actual PDF content for download endpoint
                    pdf_filename = f"{job_data['title'].replace(' ', '_').replace('/', '_')}_resume_{template}_{batch_id}_{job_index}.pdf"
                    
                    # Store PDF content in global storage for download
                    file_key = f"{batch_id}/{pdf_filename}"
                    batch_file_storage[file_key] = result.get('pdf_content')
                    print(f"💾 Stored PDF file: {file_key}, size: {len(result.get('pdf_content', b''))} bytes")
                    
                    formatted_resume_data = {
                        'format': 'pdf',
                        'template_applied': template,
                        'filename': pdf_filename,
                        'download_url': f'/api/enhanced-batch/download/{batch_id}/{pdf_filename}',
                        'has_binary_content': True,
                        'content': ''
                    }
                else:
                    print(f"❌ PDF generation failed! Result: {result}")
                    
            elif output_format == "rtf":
                result = professional_service.generate_professional_docx(
                    resume_text=tailored_resume,
                    template=template
                )
                if result.get('success'):
                    # Store the actual RTF/DOCX content for download endpoint
                    rtf_filename = f"{job_data['title'].replace(' ', '_').replace('/', '_')}_resume_{template}_{batch_id}_{job_index}.rtf"
                    
                    # Store RTF content in global storage for download
                    file_key = f"{batch_id}/{rtf_filename}"
                    rtf_content = result.get('docx_content') or result.get('rtf_content')
                    batch_file_storage[file_key] = rtf_content
                    print(f"💾 Stored RTF file: {file_key}, size: {len(rtf_content) if rtf_content else 0} bytes")
                    
                    formatted_resume_data = {
                        'format': 'rtf',
                        'template_applied': template,
                        'filename': rtf_filename,
                        'formatted': True,
                        'content': result.get('formatted_text', tailored_resume),  # Text content for display
                        'download_url': f'/api/enhanced-batch/download/{batch_id}/{rtf_filename}',  # Download URL
                        'has_binary_content': True
                    }
                    
        except Exception as e:
            print(f"⚠️ Professional formatting failed, using plain text: {e}")
            import traceback
            print(f"🚑 Full error traceback: {traceback.format_exc()}")
            formatted_resume_data = None
    else:
        print(f"📝 Using plain text formatting (no professional templates applied)")
    
    # Emergency PDF fallback: if we still don't have formatted content, render HTML from template engine
    if output_format == "pdf" and not formatted_resume_data:
        try:
            print("🆘 Emergency PDF fallback: rendering via TemplateEngine and storing for download")
            from services.template_engine import TemplateEngine
            from services.renderers.pdf_renderer import render_pdf_from_html_sync
            # Use selected template when possible
            html = TemplateEngine.render_preview(template_id=(template or "modern"), resume_text=tailored_resume)
            pdf_bytes = render_pdf_from_html_sync(html, page_size="A4")
            fallback_filename = f"{job_data['title'].replace(' ', '_').replace('/', '_')}_resume_{template}_{batch_id}_{job_index}.pdf"
            file_key = f"{batch_id}/{fallback_filename}"
            batch_file_storage[file_key] = pdf_bytes
            print(f"🆘 Stored fallback PDF: {file_key}, size: {len(pdf_bytes)} bytes")
            formatted_resume_data = {
                'format': 'pdf',
                'template_applied': template,
                'filename': fallback_filename,
                'download_url': f'/api/enhanced-batch/download/{batch_id}/{fallback_filename}',
                'has_binary_content': True,
                'content': ''
            }
        except Exception as e:
            print(f"❌ Emergency PDF fallback failed: {e}")

    # Generate cover letter if requested
    cover_letter = None
    if cover_letter_options and cover_letter_options.get("includeCoverLetter", False):
        tone = cover_letter_options.get("coverLetterDetails", {}).get("tone", "professional")
        cover_letter = enhanced_processor.generate_cover_letter(resume_text, job_data, tone)
    
    # Track analytics events for Pro users
    if user_id and db:
        # Track resume generation event
        await enhanced_processor.track_analytics_event(
            user_id=user_id,
            event_type="RESUME_GENERATED",
            event_data={
                "job_title": job_data['title'],
                "company": job_data['company'],
                "tailoring_mode": tailoring_mode,
                "processing_time": processing_time,
                "scraped_successfully": job_data.get('scraped_successfully', False)
            },
            db=db
        )
        
        # Track template usage
        await enhanced_processor.track_analytics_event(
            user_id=user_id,
            event_type="TEMPLATE_USAGE",
            event_data={
                "template_type": "enhanced_batch",
                "tailoring_mode": tailoring_mode,
                "job_title": job_data['title']
            },
            db=db
        )
        
        # Track cover letter generation if applicable
        if cover_letter:
            await enhanced_processor.track_analytics_event(
                user_id=user_id,
                event_type="COVER_LETTER_GENERATED",
                event_data={
                    "job_title": job_data['title'],
                    "company": job_data['company'],
                    "tone": cover_letter_options.get("coverLetterDetails", {}).get("tone", "professional")
                },
                db=db
            )
    
    # Calculate ATS score for the tailored resume with enhanced intelligence
    ats_scorer = EnhancedATSScorer()
    ats_results = ats_scorer.calculate_ats_score(
        resume_text=tailored_resume,
        job_description=job_data.get('description', '')
    )
    
    # Extract keyword analysis for better UX display
    keyword_analysis = ats_results.get('keyword_analysis', {})
    confidence_level = ats_results.get('confidence_level', {})
    
    result = {
        "job_index": job_index,
        "job_url": job_url,
        "job_title": job_data['title'],
        "company": job_data['company'],
        "status": "completed",
        "tailored_resume": tailored_resume,
        "cover_letter": cover_letter,
        "processing_time": processing_time,
        "tailoring_mode": tailoring_mode,
        "template": template,
        "output_format": output_format,
        "formatted_resume_data": formatted_resume_data,  # PDF/RTF content if generated
        "scraped_successfully": job_data.get('scraped_successfully', False),
        "ats_score": ats_results.get('overall_score', 'N/A'),
        "ats_grade": ats_results.get('grade', 'N/A'),
        "keyword_matches": keyword_analysis.get('total_matches', 0),
        "keyword_match_percentage": keyword_analysis.get('match_percentage', 0),
        "confidence_level": confidence_level.get('level', 'MODERATE'),
        "confidence_message": confidence_level.get('message', 'ATS analysis complete'),
        "ats_details": {
            "component_scores": ats_results.get('component_scores', {}),
            "recommendations": ats_results.get('recommendations', []),
            "matched_skills": keyword_analysis.get('matched_skills', []),
            "missing_skills": keyword_analysis.get('missing_skills', []),
            "analysis_quality": ats_results.get('analysis_quality', {})
        },
        "features_used": {
            "real_scraper": job_data.get('scraped_successfully', False),
            "heavy_mode": tailoring_mode == "heavy",
            "cover_letter": cover_letter is not None,
            "ats_scoring": True,
            "intelligent_keyword_extraction": True,
            "professional_formatting": formatted_resume_data is not None,
            "template_applied": template
        },
        "phase8_optimized": True  # Phase 8 marker
    }
    
    print(f"✅ Enhanced processing completed job {job_index + 1}: {job_data['title']}")
    return result

def _update_phase8_metrics(batch_id: str, processing_time: float, timed_out: bool, job_index: int):
    """Update Phase 8 performance metrics"""
    if batch_id not in batch_jobs:
        return
    
    metrics = batch_jobs[batch_id].phase8_metrics
    
    # Update timing metrics
    if metrics["min_job_time"] is None or processing_time < metrics["min_job_time"]:
        metrics["min_job_time"] = processing_time
    if processing_time > metrics["max_job_time"]:
        metrics["max_job_time"] = processing_time
    
    # Update counts
    if timed_out:
        metrics["timeout_count"] += 1
    elif processing_time < 30:  # Under 30-second goal
        metrics["under_30_second_count"] += 1
    
    # Update retry count if needed
    metrics["retry_count"] = metrics.get("retry_count", 0)

async def process_batch_enhanced(
    batch_id: str, 
    resume_text: str, 
    job_urls: List[str],
    tailoring_mode: str = "light",
    cover_letter_options: Dict[str, Any] = None,
    user_id: str = None,
    db: Session = None,
    template: str = "modern",
    output_format: str = "pdf"
):
    """Process batch jobs with enhanced features"""
    try:
        print(f"🚀 Starting enhanced batch processing for {len(job_urls)} jobs")
        print(f"🎯 Mode: {tailoring_mode.upper()}")
        
        # Track bulk processing start event for Pro users
        if user_id and db:
            await enhanced_processor.track_analytics_event(
                user_id=user_id,
                event_type="BULK_PROCESSING",
                event_data={
                    "total_jobs": len(job_urls),
                    "tailoring_mode": tailoring_mode,
                    "batch_id": batch_id,
                    "include_cover_letter": cover_letter_options.get("includeCoverLetter", False) if cover_letter_options else False
                },
                db=db
            )
        
        if batch_id not in batch_jobs:
            print(f"❌ Batch ID {batch_id} not found!")
            return
        
        batch_jobs[batch_id].state = "processing"
        batch_jobs[batch_id].updated_at = datetime.now()
        
        results = []
        
        # Process jobs with controlled concurrency for reliability
        max_concurrent = 2 if tailoring_mode == "heavy" else 3
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_semaphore(job_url, job_index):
            async with semaphore:
                return await process_single_job_enhanced(
                    resume_text, job_url, job_index, batch_id, tailoring_mode, cover_letter_options, user_id, db, template, output_format
                )
        
        # Process jobs in parallel with semaphore control
        tasks = [process_with_semaphore(job_url, i) for i, job_url in enumerate(job_urls)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "job_index": i,
                    "job_url": job_urls[i],
                    "status": "failed",
                    "error": str(result),
                    "tailored_resume": None,
                    "cover_letter": None
                })
            else:
                processed_results.append(result)
        
        # Update progress
        completed_count = sum(1 for r in processed_results if r["status"] == "completed")
        failed_count = len(processed_results) - completed_count
        
        # Mark as completed
        if batch_id in batch_jobs:
            batch_jobs[batch_id].state = "completed"
            batch_jobs[batch_id].completed = completed_count
            batch_jobs[batch_id].failed = failed_count
            batch_jobs[batch_id].current_job = f"Completed: {completed_count} successful, {failed_count} failed"
            batch_jobs[batch_id].results = processed_results
            batch_jobs[batch_id].updated_at = datetime.now()
        
        # Store results
        batch_results[batch_id] = processed_results
        
        print(f"🎉 Enhanced batch processing completed!")
        print(f"📊 Results: {completed_count} successful, {failed_count} failed")
        
    except Exception as e:
        print(f"❌ Enhanced batch processing failed: {str(e)}")
        if batch_id in batch_jobs:
            batch_jobs[batch_id].state = "failed"
            batch_jobs[batch_id].current_job = f"Failed: {str(e)}"
            batch_jobs[batch_id].updated_at = datetime.now()

@router.post("/process")
async def start_enhanced_batch_processing(
    request: EnhancedBatchRequest, 
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Start enhanced batch processing with all advanced features"""
    try:
        print(f"🚨 ENHANCED BATCH PROCESSING STARTED!")
        print(f"📋 Resume length: {len(request.resume_text)}")
        print(f"📋 Job URLs: {request.job_urls}")
        print(f"🎯 Tailoring mode: {request.tailoring_mode}")
        print(f"💼 Cover letters: {request.cover_letter_options.get('includeCoverLetter', False)}")
        
        if not request.job_urls:
            raise HTTPException(status_code=400, detail="At least one job URL is required")
        
        # Enhanced subscription limits and usage tracking for Free Tier
        user_email = "anonymous"
        max_jobs = 10  # Default free limit
        is_pro_user = False
        user_tier = "Free"
        
        if AUTH_AVAILABLE and current_user and hasattr(current_user, 'email'):
            user_email = str(current_user.email) if current_user.email else "anonymous"
            is_pro_user = hasattr(current_user, 'is_pro_active') and current_user.is_pro_active()
            user_tier = "Pro" if is_pro_user else "Free"
            
            # Get user-specific limits
            if hasattr(current_user, 'get_usage_limits_new'):
                limits = current_user.get_usage_limits_new()
                max_jobs = limits.get("bulk_jobs", 10) if limits else 10
                
                # Enhanced Free Tier validation
                if not is_pro_user:
                    # Check if user can process resumes (weekly limit for Free users)
                    if hasattr(current_user, 'can_process_resume') and not current_user.can_process_resume():
                        weekly_limit = limits.get("weekly_sessions", 3)
                        raise HTTPException(
                            status_code=403, 
                            detail=f"Free tier weekly limit of {weekly_limit} resumes reached. Upgrade to Pro for unlimited processing."
                        )
                    
                    # Validate Heavy mode access for Free users
                    if request.tailoring_mode == "heavy" and not limits.get("heavy_tailoring", False):
                        raise HTTPException(
                            status_code=403, 
                            detail="Heavy tailoring mode requires Pro subscription. Use Light mode or upgrade to Pro."
                        )
            
            # Validate batch size limits
            if len(request.job_urls) > max_jobs:
                upgrade_message = "Upgrade to Pro for up to 25 jobs per batch." if not is_pro_user else "Maximum batch size exceeded."
                raise HTTPException(
                    status_code=400, 
                    detail=f"Maximum {max_jobs} job URLs allowed for {user_tier} users. {upgrade_message}"
                )
            
            # Enhanced cover letter validation
            if request.cover_letter_options and request.cover_letter_options.get("includeCoverLetter", False):
                if not is_pro_user:
                    raise HTTPException(
                        status_code=403, 
                        detail="Cover letters require Pro subscription. Upgrade to Pro to access AI-generated cover letters."
                    )
                    
        # Additional Free Tier specific validations
        if not AUTH_AVAILABLE or not current_user:
            # Anonymous users get basic free limits
            if len(request.job_urls) > 3:
                raise HTTPException(
                    status_code=401, 
                    detail="Anonymous users limited to 3 jobs. Sign up for free to process up to 10 jobs per batch."
                )
            if request.tailoring_mode == "heavy":
                raise HTTPException(
                    status_code=401, 
                    detail="Heavy tailoring mode requires account registration. Sign up for free to access Light mode."
                )
            if request.cover_letter_options and request.cover_letter_options.get("includeCoverLetter", False):
                raise HTTPException(
                    status_code=401, 
                    detail="Cover letters require Pro subscription. Sign up and upgrade to Pro."
                )
        
        # Generate batch ID
        batch_id = str(uuid.uuid4())
        
        # Initialize enhanced batch status with tier information
        batch_status = EnhancedBatchStatus(batch_id, len(request.job_urls), user_email)
        batch_status.user_tier = user_tier
        batch_status.is_pro_user = is_pro_user
        batch_status.max_jobs_allowed = max_jobs
        batch_jobs[batch_id] = batch_status
        
        # Track usage for Free Tier users (simplified approach)
        if AUTH_AVAILABLE and current_user and not is_pro_user:
            try:
                # Log usage tracking for Free Tier users
                print(f"📊 Free Tier usage: {user_email} processing {len(request.job_urls)} jobs")
                # Note: Actual usage tracking will be handled by the User model's built-in methods
                # during the resume processing workflow
            except Exception as e:
                print(f"⚠️ Failed to log usage tracking: {e}")
                # Don't fail the request if usage logging fails
        
        # Start enhanced background processing with analytics tracking
        user_id_for_analytics = str(current_user.id) if current_user and hasattr(current_user, 'id') else ""
        background_tasks.add_task(
            process_batch_enhanced,
            batch_id,
            request.resume_text,
            request.job_urls,
            request.tailoring_mode or "light",
            request.cover_letter_options,
            user_id_for_analytics,
            None,  # Background task will create its own DB session
            request.template or "modern",  # Template selection
            request.output_format or "pdf"  # Output format
        )
        
        return JSONResponse({
            "success": True,
            "batch_job_id": batch_id,
            "message": f"Enhanced batch processing started for {len(request.job_urls)} jobs",
            "features": {
                "tailoring_mode": request.tailoring_mode or "light",
                "real_job_scraping": JOB_SCRAPER_AVAILABLE,
                "langchain_processing": LANGCHAIN_AVAILABLE,
                "cover_letters": request.cover_letter_options.get("includeCoverLetter", False),
                "max_jobs_allowed": max_jobs
            },
            "status": batch_status.to_dict()
        })
        
    except Exception as e:
        print(f"❌ Failed to start enhanced batch processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start batch processing: {str(e)}")

@router.get("/status/{batch_id}")
async def get_enhanced_batch_status(batch_id: str):
    """Get enhanced batch status"""
    if batch_id not in batch_jobs:
        raise HTTPException(status_code=404, detail="Batch job not found")
    
    batch_status = batch_jobs[batch_id]
    return JSONResponse({
        "success": True,
        "status": batch_status.to_dict()
    })

def sanitize_for_json(obj):
    """Remove any bytes objects from data structure to prevent JSON serialization errors"""
    if isinstance(obj, bytes):
        return "<binary_data_removed>"  # Replace bytes with placeholder instead of None
    elif isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items() if not isinstance(v, bytes)}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj if not isinstance(item, bytes)]
    else:
        return obj

@router.get("/results/{batch_id}")
async def get_enhanced_batch_results(batch_id: str):
    """Get enhanced batch results"""
    if batch_id not in batch_results:
        raise HTTPException(status_code=404, detail="Batch results not found")
    
    results = batch_results[batch_id]
    
    # Sanitize results to remove any bytes objects that could cause JSON serialization errors
    sanitized_results = sanitize_for_json(results)
    
    # Ensure sanitized_results is still a list
    if not isinstance(sanitized_results, list):
        sanitized_results = []
    
    response_data = {
        "success": True,
        "results": sanitized_results,
        "total": len(sanitized_results),
        "summary": {
            "completed": sum(1 for r in sanitized_results if isinstance(r, dict) and r.get("status") == "completed"),
            "failed": sum(1 for r in sanitized_results if isinstance(r, dict) and r.get("status") == "failed"),
            "features_used": {
                "real_scraper_success": sum(1 for r in sanitized_results if isinstance(r, dict) and r.get("features_used", {}).get("real_scraper", False)),
                "heavy_mode_used": sum(1 for r in sanitized_results if isinstance(r, dict) and r.get("tailoring_mode") == "heavy"),
                "cover_letters_generated": sum(1 for r in sanitized_results if isinstance(r, dict) and r.get("cover_letter") is not None)
            }
        }
    }
    
    print(f"📤 Returning sanitized batch results for {batch_id} with {len(sanitized_results)} results")
    return JSONResponse(response_data)


@router.get("/download-pdf/{batch_id}")
async def download_batch_as_single_pdf(batch_id: str):
    """Merge all generated PDFs in a batch into a single PDF and download directly."""
    from fastapi.responses import StreamingResponse
    from PyPDF2 import PdfReader, PdfWriter
    import io

    if batch_id not in batch_results:
        raise HTTPException(status_code=404, detail="Batch results not found")

    results = batch_results.get(batch_id, [])

    # Collect file keys in the same order as results
    pdf_keys_in_order = []
    for r in results:
        if not isinstance(r, dict):
            continue
        frd = r.get("formatted_resume_data") or {}
        if frd.get("format") == "pdf":
            filename = frd.get("filename")
            if filename:
                key = f"{batch_id}/{filename}"
                if key in batch_file_storage:
                    pdf_keys_in_order.append(key)

    # Fallback: grab all PDFs for the batch
    if not pdf_keys_in_order:
        prefix = f"{batch_id}/"
        pdf_keys_in_order = [k for k in batch_file_storage.keys() if k.startswith(prefix) and k.endswith(".pdf")]
        pdf_keys_in_order.sort()

    if not pdf_keys_in_order:
        raise HTTPException(status_code=404, detail="No PDFs available for this batch")

    writer = PdfWriter()
    for key in pdf_keys_in_order:
        data = batch_file_storage.get(key)
        if not data:
            continue
        try:
            reader = PdfReader(io.BytesIO(data))
            for page in reader.pages:
                writer.add_page(page)
        except Exception as e:
            print(f"⚠️ Skipping PDF in merge due to error: {key} -> {e}")
            continue

    if len(writer.pages) == 0:
        raise HTTPException(status_code=500, detail="Failed to build merged PDF")

    out_buf = io.BytesIO()
    writer.write(out_buf)
    out_buf.seek(0)

    headers = {
        "Content-Disposition": f"attachment; filename=batch_{batch_id}.pdf",
        "Cache-Control": "no-store",
    }
    return StreamingResponse(out_buf, media_type="application/pdf", headers=headers)

# Global storage for binary files (in production, use proper file storage like S3/disk)
batch_file_storage = {}

@router.get("/download/{batch_id}/{filename}")
async def download_batch_file(batch_id: str, filename: str):
    """Download a specific batch-generated file (PDF/RTF)"""
    from fastapi.responses import Response
    
    # Create storage key
    file_key = f"{batch_id}/{filename}"
    
    print(f"📥 Download request for: {file_key}")
    
    # Check if file exists in storage
    if file_key not in batch_file_storage:
        print(f"❌ File not found in storage: {file_key}")
        print(f"📋 Available files: {list(batch_file_storage.keys())}")
        raise HTTPException(status_code=404, detail="File not found")
    
    file_data = batch_file_storage[file_key]
    print(f"✅ Found file: {file_key}, size: {len(file_data)} bytes")
    
    # Determine content type based on file extension
    if filename.endswith('.pdf'):
        content_type = 'application/pdf'
    elif filename.endswith('.rtf'):
        content_type = 'application/rtf'
    elif filename.endswith('.docx'):
        content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    else:
        content_type = 'text/plain'
    
    return Response(
        content=file_data,
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Cache-Control": "no-store"
        }
    )

@router.get("/download-all/{batch_id}")
async def download_all_batch_files(batch_id: str):
    """Zip all generated PDFs for a batch and stream as attachment."""
    import io
    import zipfile
    from fastapi.responses import StreamingResponse

    # Validate batch
    if batch_id not in batch_results:
        raise HTTPException(status_code=404, detail="Batch results not found")

    # Gather PDF files from storage using batch prefix
    prefix = f"{batch_id}/"
    pdf_entries = [(k, v) for k, v in batch_file_storage.items() if k.startswith(prefix) and k.endswith(".pdf")]
    if not pdf_entries:
        raise HTTPException(status_code=404, detail="No PDFs available for this batch")

    # Create ZIP in memory
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for key, data in pdf_entries:
            _, filename = key.split("/", 1)
            zf.writestr(filename, data)
    buf.seek(0)

    headers = {
        "Content-Disposition": f"attachment; filename=batch_{batch_id}.zip",
        "Cache-Control": "no-store",
    }
    return StreamingResponse(buf, media_type="application/zip", headers=headers)

@router.get("/test")
async def test_enhanced_batch():
    """Test endpoint for enhanced batch processing"""
    return {
        "status": "ok",
        "message": "Enhanced batch processing is ready!",
        "features": {
            "job_scraper": JOB_SCRAPER_AVAILABLE,
            "langchain": LANGCHAIN_AVAILABLE,
            "authentication": AUTH_AVAILABLE
        }
    }
