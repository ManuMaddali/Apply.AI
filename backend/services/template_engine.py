from __future__ import annotations

from typing import Any, Dict
from models.resume_schema import Resume, parse_resume_text_to_schema
from services.renderers.html_renderer import render_html
from services.renderers.pdf_renderer import render_pdf_from_html


class TemplateEngine:
    """
    Facade for HTML preview and PDF rendering.
    """

    @staticmethod
    def _ensure_resume(resume_json: Dict[str, Any] | None, resume_text: str | None):
        from models.resume_schema import Resume
        
        if resume_json and isinstance(resume_json, dict):
            return Resume.model_validate(resume_json)
        if resume_text:
            print(f"🔍 TemplateEngine: Parsing resume text of length {len(resume_text)}")
            print(f"📝 Resume preview (first 200 chars): {resume_text[:200]}...")
            
            # Use our comprehensive resume parser for better section extraction
            try:
                from services.resume_parser import ResumeParser
                parser = ResumeParser()
                parsed_data = parser.parse(resume_text)
                print(f"✅ Comprehensive parser extracted: name='{parsed_data.get('name')}', experience={len(parsed_data.get('experience', []))} items")
                
                # Convert to Resume schema format
                from models.resume_schema import Resume, Contact, ExperienceItem, EducationItem, Skill
                
                # Create contact info
                contact = Contact(
                    email=parsed_data.get('email', ''),
                    phone=parsed_data.get('phone', ''),
                    location=parsed_data.get('location', ''),
                    links=[]
                )
                
                # Add LinkedIn/GitHub links
                if parsed_data.get('linkedin'):
                    contact.links.append({'label': 'LinkedIn', 'url': parsed_data['linkedin']})
                if parsed_data.get('github'):
                    contact.links.append({'label': 'GitHub', 'url': parsed_data['github']})
                
                # Convert experience with proper bullet points
                experience_items = []
                for exp in parsed_data.get('experience', []):
                    bullets = exp.get('responsibilities', [])
                    if isinstance(bullets, list) and bullets:
                        experience_items.append(ExperienceItem(
                            title=exp.get('title', ''),
                            company=exp.get('company', ''),
                            dates=exp.get('dates', ''),
                            bullets=bullets
                        ))
                
                # Convert education
                education_items = []
                for edu in parsed_data.get('education', []):
                    school_info = []
                    if edu.get('degree'):
                        school_info.append(edu['degree'])
                    if edu.get('field'):
                        school_info.append(edu['field'])
                    if edu.get('institution'):
                        school_info.append(f"from {edu['institution']}")
                    if edu.get('year'):
                        school_info.append(f"({edu['year']})")
                    
                    if school_info:
                        education_items.append(EducationItem(school=' '.join(school_info)))
                
                # Convert skills
                skills_list = []
                skills_dict = parsed_data.get('skills', {})
                if isinstance(skills_dict, dict):
                    for category, skill_list in skills_dict.items():
                        skills_list.extend([Skill(name=skill) for skill in skill_list if skill])
                
                resume = Resume(
                    name=parsed_data.get('name', ''),
                    headline=parsed_data.get('summary', '')[:100] if parsed_data.get('summary') else None,
                    contact=contact,
                    summary=parsed_data.get('summary', ''),
                    experience=experience_items,
                    education=education_items,
                    skills=skills_list
                )
                
                print(f"✅ Converted to Resume schema: {len(experience_items)} experience, {len(education_items)} education, {len(skills_list)} skills")
                return resume
                
            except Exception as e:
                print(f"⚠️ Comprehensive parser failed, using fallback: {e}")
                # Fallback to original parser
                return parse_resume_text_to_schema(resume_text)
        
        return Resume()

    @staticmethod
    def render_preview(template_id: str, resume_json: Dict[str, Any] | None = None, resume_text: str | None = None) -> str:
        print(f"🔥 TEMPLATE ENGINE RECEIVED:")
        print(f"  - template_id: {template_id}")
        print(f"  - resume_json keys: {resume_json.keys() if resume_json else 'None'}")
        print(f"  - resume_text length: {len(resume_text) if resume_text else 0}")
        if resume_json:
            print(f"  - resume_json['name']: {resume_json.get('name', 'NO NAME')}")
            print(f"  - resume_json['experience']: {str(resume_json.get('experience', ''))[:100]}")
        
        print(f"🎨 TemplateEngine: Rendering template '{template_id}' with resume_text length: {len(resume_text) if resume_text else 0}")
        resume = TemplateEngine._ensure_resume(resume_json, resume_text)
        print(f"📊 Resume object: name='{resume.name}', experience={len(resume.experience)}, education={len(resume.education)}")
        html = render_html(template_id, resume, raw_text=resume_text)
        print(f"📄 Generated HTML length: {len(html)} characters")
        return html

    @staticmethod
    async def render_pdf(template_id: str, resume_json: Dict[str, Any] | None = None, resume_text: str | None = None) -> bytes:
        resume = TemplateEngine._ensure_resume(resume_json, resume_text)
        html = render_html(template_id, resume, raw_text=resume_text)
        pdf_bytes = await render_pdf_from_html(html, page_size="A4")
        return pdf_bytes


