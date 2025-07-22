"""
Job-Specific Premium Templates Service - Pro-only industry-tailored resume templates

This service provides:
- Industry-specific resume templates for popular job categories
- Each category offers all 7 template variations (Standard, Modern, Executive, etc.)
- Industry-specific sections and formatting optimizations
- ATS-friendly templates with role-specific keywords and sections
- Pro-only access with fallback to standard templates for Free users
"""

from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass
import logging

from services.advanced_formatting_service import (
    AdvancedFormattingService,
    FormattingOptions,
    FormattingTemplate,
    ColorScheme,
    FontFamily
)

logger = logging.getLogger(__name__)


class JobCategory(Enum):
    """Available job categories for industry-specific templates"""
    # Tech & Data Roles
    SOFTWARE_ENGINEER = "software_engineer"
    DATA_SCIENTIST = "data_scientist"
    IT_ANALYST = "it_analyst"
    AI_ML_SPECIALIST = "ai_ml_specialist"
    ENGINEERING_MANAGER = "engineering_manager"
    PRODUCT_MANAGER = "product_manager"
    DEVOPS_ENGINEER = "devops_engineer"
    CYBERSECURITY_SPECIALIST = "cybersecurity_specialist"
    CLOUD_ARCHITECT = "cloud_architect"
    
    # Healthcare Roles
    NURSE_PRACTITIONER = "nurse_practitioner"
    PHYSICIAN_ASSISTANT = "physician_assistant"
    MEDICAL_MANAGER = "medical_manager"
    HEALTHCARE_ADMINISTRATOR = "healthcare_administrator"
    CLINICAL_RESEARCHER = "clinical_researcher"
    
    # Finance & Business Roles
    FINANCIAL_MANAGER = "financial_manager"
    ACCOUNTANT = "accountant"
    MARKET_RESEARCH_ANALYST = "market_research_analyst"
    BUSINESS_ANALYST = "business_analyst"
    INVESTMENT_ADVISOR = "investment_advisor"
    
    # Sales & Operations Roles
    SALES_REPRESENTATIVE = "sales_representative"
    OPERATIONS_MANAGER = "operations_manager"
    CUSTOMER_SERVICE_REP = "customer_service_rep"
    ACCOUNT_MANAGER = "account_manager"
    SUPPLY_CHAIN_MANAGER = "supply_chain_manager"
    
    # Legal Roles
    LAWYER = "lawyer"
    PARALEGAL = "paralegal"
    LEGAL_ASSISTANT = "legal_assistant"
    COMPLIANCE_OFFICER = "compliance_officer"
    
    # Additional High-Usage Roles
    MARKETING_MANAGER = "marketing_manager"
    HR_MANAGER = "hr_manager"
    PROJECT_MANAGER = "project_manager"
    CONSULTANT = "consultant"
    TEACHER = "teacher"
    NURSE = "nurse"


@dataclass
class JobSpecificSection:
    """Configuration for job-specific resume sections"""
    title: str
    priority: int  # Lower number = higher priority
    required: bool = False
    ats_keywords: List[str] = None
    description: str = ""
    
    def __post_init__(self):
        if self.ats_keywords is None:
            self.ats_keywords = []


@dataclass
class JobTemplateConfig:
    """Configuration for job-specific template"""
    category: JobCategory
    display_name: str
    description: str
    industry: str
    specific_sections: List[JobSpecificSection]
    recommended_templates: List[FormattingTemplate]
    recommended_colors: List[ColorScheme]
    ats_keywords: List[str]
    section_order: List[str]
    
    def __post_init__(self):
        if not self.recommended_templates:
            self.recommended_templates = [FormattingTemplate.STANDARD]
        if not self.recommended_colors:
            self.recommended_colors = [ColorScheme.CLASSIC_BLUE]


class JobSpecificTemplateService:
    """Service for managing job-specific premium templates"""
    
    def __init__(self):
        self.advanced_formatting_service = AdvancedFormattingService()
        self.job_configs = self._initialize_job_configs()
    
    def _initialize_job_configs(self) -> Dict[JobCategory, JobTemplateConfig]:
        """Initialize job-specific template configurations"""
        return {
            # Tech & Data Roles
            JobCategory.SOFTWARE_ENGINEER: JobTemplateConfig(
                category=JobCategory.SOFTWARE_ENGINEER,
                display_name="Software Engineer/Developer",
                description="Optimized for software development roles with emphasis on technical skills and projects",
                industry="Technology",
                specific_sections=[
                    JobSpecificSection("Technical Skills", 1, True, 
                                     ["programming", "languages", "frameworks", "databases", "tools"],
                                     "Programming languages, frameworks, and development tools"),
                    JobSpecificSection("Projects", 2, True,
                                     ["github", "portfolio", "open source", "applications", "systems"],
                                     "Software projects, applications, and contributions"),
                    JobSpecificSection("Certifications", 3, False,
                                     ["aws", "azure", "google cloud", "certified", "certification"],
                                     "Technical certifications and professional credentials")
                ],
                recommended_templates=[FormattingTemplate.TECHNICAL, FormattingTemplate.MODERN, FormattingTemplate.MINIMAL],
                recommended_colors=[ColorScheme.TECH_GREEN, ColorScheme.MODERN_GRAY, ColorScheme.CLASSIC_BLUE],
                ats_keywords=["software", "developer", "programming", "coding", "agile", "scrum", "git", "api", "database"],
                section_order=["Professional Summary", "Technical Skills", "Professional Experience", "Projects", "Education", "Certifications"]
            ),
            
            JobCategory.DATA_SCIENTIST: JobTemplateConfig(
                category=JobCategory.DATA_SCIENTIST,
                display_name="Data Scientist/Analyst",
                description="Tailored for data science roles with focus on analytics, modeling, and insights",
                industry="Technology/Analytics",
                specific_sections=[
                    JobSpecificSection("Technical Skills", 1, True,
                                     ["python", "r", "sql", "machine learning", "statistics", "visualization"],
                                     "Programming languages, statistical tools, and ML frameworks"),
                    JobSpecificSection("Data Projects", 2, True,
                                     ["analysis", "modeling", "insights", "datasets", "algorithms"],
                                     "Data analysis projects and machine learning models"),
                    JobSpecificSection("Publications", 3, False,
                                     ["research", "papers", "publications", "conferences"],
                                     "Research publications and conference presentations")
                ],
                recommended_templates=[FormattingTemplate.ACADEMIC, FormattingTemplate.TECHNICAL, FormattingTemplate.MODERN],
                recommended_colors=[ColorScheme.TECH_GREEN, ColorScheme.CLASSIC_BLUE, ColorScheme.MODERN_GRAY],
                ats_keywords=["data science", "analytics", "machine learning", "python", "sql", "statistics", "modeling", "visualization"],
                section_order=["Professional Summary", "Technical Skills", "Professional Experience", "Data Projects", "Education", "Publications"]
            ),
            
            JobCategory.PRODUCT_MANAGER: JobTemplateConfig(
                category=JobCategory.PRODUCT_MANAGER,
                display_name="Product Manager",
                description="Designed for product management roles emphasizing strategy, roadmaps, and cross-functional leadership",
                industry="Technology/Business",
                specific_sections=[
                    JobSpecificSection("Product Achievements", 1, True,
                                     ["product launch", "roadmap", "strategy", "metrics", "growth"],
                                     "Product launches, growth metrics, and strategic initiatives"),
                    JobSpecificSection("Technical Skills", 2, False,
                                     ["analytics", "sql", "jira", "figma", "data analysis"],
                                     "Technical tools and analytical capabilities"),
                    JobSpecificSection("Leadership Experience", 3, True,
                                     ["cross-functional", "stakeholder", "team leadership", "collaboration"],
                                     "Team leadership and cross-functional collaboration")
                ],
                recommended_templates=[FormattingTemplate.EXECUTIVE, FormattingTemplate.MODERN, FormattingTemplate.STANDARD],
                recommended_colors=[ColorScheme.CLASSIC_BLUE, ColorScheme.EXECUTIVE_BLACK, ColorScheme.MODERN_GRAY],
                ats_keywords=["product manager", "roadmap", "strategy", "agile", "stakeholder", "analytics", "growth", "launch"],
                section_order=["Professional Summary", "Professional Experience", "Product Achievements", "Leadership Experience", "Technical Skills", "Education"]
            ),
            
            # Healthcare Roles
            JobCategory.NURSE_PRACTITIONER: JobTemplateConfig(
                category=JobCategory.NURSE_PRACTITIONER,
                display_name="Nurse Practitioner",
                description="Specialized for advanced nursing roles with clinical expertise and patient care focus",
                industry="Healthcare",
                specific_sections=[
                    JobSpecificSection("Clinical Specializations", 1, True,
                                     ["clinical", "patient care", "diagnosis", "treatment", "specialization"],
                                     "Areas of clinical expertise and specialization"),
                    JobSpecificSection("Certifications & Licenses", 2, True,
                                     ["licensed", "certified", "board certified", "credentials", "continuing education"],
                                     "Professional licenses, certifications, and credentials"),
                    JobSpecificSection("Patient Outcomes", 3, True,
                                     ["patient satisfaction", "outcomes", "quality metrics", "care improvement"],
                                     "Patient care metrics and quality improvement initiatives")
                ],
                recommended_templates=[FormattingTemplate.STANDARD, FormattingTemplate.ACADEMIC, FormattingTemplate.MINIMAL],
                recommended_colors=[ColorScheme.CLASSIC_BLUE, ColorScheme.MODERN_GRAY, ColorScheme.EXECUTIVE_BLACK],
                ats_keywords=["nurse practitioner", "clinical", "patient care", "licensed", "certified", "healthcare", "diagnosis", "treatment"],
                section_order=["Professional Summary", "Clinical Specializations", "Professional Experience", "Certifications & Licenses", "Patient Outcomes", "Education"]
            ),
            
            # Finance & Business Roles
            JobCategory.FINANCIAL_MANAGER: JobTemplateConfig(
                category=JobCategory.FINANCIAL_MANAGER,
                display_name="Financial Manager",
                description="Optimized for finance leadership roles with emphasis on analysis, planning, and compliance",
                industry="Finance",
                specific_sections=[
                    JobSpecificSection("Financial Achievements", 1, True,
                                     ["budget", "cost reduction", "revenue growth", "roi", "financial planning"],
                                     "Financial performance improvements and strategic initiatives"),
                    JobSpecificSection("Technical Skills", 2, True,
                                     ["excel", "financial modeling", "erp", "quickbooks", "sap", "analytics"],
                                     "Financial software and analytical tools"),
                    JobSpecificSection("Certifications", 3, False,
                                     ["cpa", "cfa", "frm", "certified", "professional"],
                                     "Professional certifications and credentials")
                ],
                recommended_templates=[FormattingTemplate.EXECUTIVE, FormattingTemplate.STANDARD, FormattingTemplate.MINIMAL],
                recommended_colors=[ColorScheme.EXECUTIVE_BLACK, ColorScheme.CLASSIC_BLUE, ColorScheme.MODERN_GRAY],
                ats_keywords=["financial manager", "budget", "analysis", "planning", "compliance", "forecasting", "reporting", "finance"],
                section_order=["Professional Summary", "Professional Experience", "Financial Achievements", "Technical Skills", "Certifications", "Education"]
            ),
            
            # Sales & Operations Roles
            JobCategory.SALES_REPRESENTATIVE: JobTemplateConfig(
                category=JobCategory.SALES_REPRESENTATIVE,
                display_name="Sales Representative/Person",
                description="Tailored for sales roles with focus on achievements, targets, and relationship building",
                industry="Sales",
                specific_sections=[
                    JobSpecificSection("Sales Achievements", 1, True,
                                     ["quota", "revenue", "targets", "growth", "deals", "pipeline"],
                                     "Sales performance metrics and achievement highlights"),
                    JobSpecificSection("Key Accounts", 2, False,
                                     ["accounts", "clients", "relationships", "retention", "expansion"],
                                     "Major accounts managed and client relationships"),
                    JobSpecificSection("Sales Tools", 3, False,
                                     ["crm", "salesforce", "hubspot", "pipeline management", "forecasting"],
                                     "Sales technology and CRM platforms")
                ],
                recommended_templates=[FormattingTemplate.MODERN, FormattingTemplate.CREATIVE, FormattingTemplate.STANDARD],
                recommended_colors=[ColorScheme.CREATIVE_TEAL, ColorScheme.WARM_BROWN, ColorScheme.CLASSIC_BLUE],
                ats_keywords=["sales", "revenue", "quota", "targets", "crm", "pipeline", "clients", "growth", "negotiation"],
                section_order=["Professional Summary", "Sales Achievements", "Professional Experience", "Key Accounts", "Sales Tools", "Education"]
            ),
            
            # Legal Roles
            JobCategory.LAWYER: JobTemplateConfig(
                category=JobCategory.LAWYER,
                display_name="Lawyer/Attorney",
                description="Professional template for legal practitioners with emphasis on expertise and case experience",
                industry="Legal",
                specific_sections=[
                    JobSpecificSection("Legal Specializations", 1, True,
                                     ["litigation", "corporate law", "contracts", "compliance", "legal research"],
                                     "Areas of legal practice and specialization"),
                    JobSpecificSection("Bar Admissions", 2, True,
                                     ["bar admission", "licensed", "state bar", "jurisdiction"],
                                     "Bar admissions and professional licenses"),
                    JobSpecificSection("Notable Cases", 3, False,
                                     ["cases", "litigation", "settlements", "legal victories", "precedent"],
                                     "Significant cases and legal achievements")
                ],
                recommended_templates=[FormattingTemplate.EXECUTIVE, FormattingTemplate.ACADEMIC, FormattingTemplate.STANDARD],
                recommended_colors=[ColorScheme.EXECUTIVE_BLACK, ColorScheme.CLASSIC_BLUE, ColorScheme.MODERN_GRAY],
                ats_keywords=["attorney", "lawyer", "legal", "litigation", "contracts", "compliance", "bar admission", "law"],
                section_order=["Professional Summary", "Legal Specializations", "Professional Experience", "Bar Admissions", "Notable Cases", "Education"]
            ),
        }
    
    def get_available_job_categories(self, is_pro: bool = False) -> List[Dict[str, Any]]:
        """Get list of available job categories based on user subscription"""
        if not is_pro:
            # Free users get a limited preview
            return [{
                'category': 'preview',
                'display_name': 'Job-Specific Templates (Pro Only)',
                'description': 'Upgrade to Pro to access industry-tailored templates',
                'industry': 'All Industries',
                'available': False,
                'pro_only': True,
                'template_count': len(FormattingTemplate),
                'upgrade_url': '/upgrade'
            }]
        
        categories = []
        for config in self.job_configs.values():
            categories.append({
                'category': config.category.value,
                'display_name': config.display_name,
                'description': config.description,
                'industry': config.industry,
                'available': True,
                'pro_only': True,
                'template_count': len(FormattingTemplate),
                'recommended_templates': [t.value for t in config.recommended_templates],
                'recommended_colors': [c.value for c in config.recommended_colors],
                'specific_sections': [
                    {
                        'title': section.title,
                        'description': section.description,
                        'required': section.required,
                        'priority': section.priority
                    }
                    for section in config.specific_sections
                ]
            })
        
        # Sort by industry and then by display name
        categories.sort(key=lambda x: (x['industry'], x['display_name']))
        return categories
    
    def get_job_category_templates(self, category: str, is_pro: bool = False) -> Dict[str, Any]:
        """Get all template variations for a specific job category"""
        if not is_pro:
            return {
                'error': 'Pro subscription required',
                'message': 'Job-specific templates require a Pro subscription',
                'upgrade_url': '/upgrade'
            }
        
        try:
            job_category = JobCategory(category)
        except ValueError:
            return {
                'error': 'Invalid job category',
                'message': f'Job category "{category}" not found',
                'available_categories': [cat.value for cat in JobCategory]
            }
        
        if job_category not in self.job_configs:
            return {
                'error': 'Job category not configured',
                'message': f'Templates for "{category}" are not yet available'
            }
        
        config = self.job_configs[job_category]
        
        # Get all template variations for this job category
        templates = []
        for template in FormattingTemplate:
            template_info = {
                'id': f"{category}_{template.value}",
                'template': template.value,
                'category': category,
                'display_name': f"{config.display_name} - {template.value.title()}",
                'description': f"{template.value.title()} template optimized for {config.display_name.lower()} roles",
                'recommended': template in config.recommended_templates,
                'preview_url': f'/static/templates/{category}_{template.value}_preview.png',
                'ats_optimized': True
            }
            templates.append(template_info)
        
        return {
            'category': config.category.value,
            'display_name': config.display_name,
            'description': config.description,
            'industry': config.industry,
            'templates': templates,
            'specific_sections': [
                {
                    'title': section.title,
                    'description': section.description,
                    'required': section.required,
                    'priority': section.priority,
                    'ats_keywords': section.ats_keywords
                }
                for section in config.specific_sections
            ],
            'recommended_colors': [c.value for c in config.recommended_colors],
            'ats_keywords': config.ats_keywords,
            'section_order': config.section_order
        }
    
    def create_job_specific_resume(
        self,
        resume_text: str,
        job_category: str,
        template: str,
        formatting_options: FormattingOptions,
        output_path: str,
        job_title: str = ""
    ) -> bool:
        """Create a job-specific resume with industry optimizations"""
        try:
            # Validate job category
            try:
                category_enum = JobCategory(job_category)
            except ValueError:
                logger.error(f"Invalid job category: {job_category}")
                return False
            
            if category_enum not in self.job_configs:
                logger.error(f"Job category not configured: {job_category}")
                return False
            
            config = self.job_configs[category_enum]
            
            # Enhance the resume text with job-specific optimizations
            enhanced_resume_text = self._enhance_resume_for_job_category(resume_text, config)
            
            # Create job-specific formatting options
            job_specific_options = self._create_job_specific_formatting_options(
                formatting_options, config
            )
            
            # Generate the resume using the advanced formatting service
            success = self.advanced_formatting_service.create_advanced_formatted_resume(
                enhanced_resume_text,
                job_specific_options,
                output_path,
                job_title
            )
            
            if success:
                logger.info(f"Successfully created job-specific resume for {job_category} with template {template}")
            else:
                logger.error(f"Failed to create job-specific resume for {job_category}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error creating job-specific resume: {e}")
            return False
    
    def _enhance_resume_for_job_category(self, resume_text: str, config: JobTemplateConfig) -> str:
        """Enhance resume text with job-specific optimizations"""
        # This is a simplified enhancement - in a full implementation,
        # you might use AI to restructure content based on job category
        
        enhanced_text = resume_text
        
        # Add job-specific section headers if they don't exist
        for section in config.specific_sections:
            if section.required and section.title.upper() not in enhanced_text.upper():
                # Add placeholder for missing required sections
                enhanced_text += f"\n\n{section.title.upper()}\n• [Add relevant {section.description.lower()}]"
        
        return enhanced_text
    
    def _create_job_specific_formatting_options(
        self,
        base_options: FormattingOptions,
        config: JobTemplateConfig
    ) -> FormattingOptions:
        """Create job-specific formatting options based on category recommendations"""
        
        # Use recommended template if the current one isn't recommended
        template = base_options.template
        if template not in config.recommended_templates and config.recommended_templates:
            template = config.recommended_templates[0]
        
        # Use recommended color scheme if available
        color_scheme = base_options.color_scheme
        if color_scheme not in config.recommended_colors and config.recommended_colors:
            color_scheme = config.recommended_colors[0]
        
        # Create new formatting options with job-specific enhancements
        job_options = FormattingOptions(
            template=template,
            color_scheme=color_scheme,
            font_family=base_options.font_family,
            font_size=base_options.font_size,
            line_spacing=base_options.line_spacing,
            margin_size=base_options.margin_size,
            section_spacing=base_options.section_spacing,
            use_two_columns=base_options.use_two_columns,
            include_border=base_options.include_border,
            header_style=base_options.header_style,
            bullet_style=base_options.bullet_style,
            page_size=base_options.page_size,
            section_order=config.section_order,
            custom_colors=base_options.custom_colors,
            custom_fonts=base_options.custom_fonts
        )
        
        return job_options
    
    def validate_job_specific_request(
        self,
        job_category: str,
        template: str,
        is_pro: bool
    ) -> Tuple[bool, str]:
        """Validate job-specific template request"""
        if not is_pro:
            return False, "Job-specific templates require Pro subscription"
        
        try:
            category_enum = JobCategory(job_category)
        except ValueError:
            return False, f"Invalid job category: {job_category}"
        
        if category_enum not in self.job_configs:
            return False, f"Job category '{job_category}' is not yet available"
        
        try:
            FormattingTemplate(template)
        except ValueError:
            return False, f"Invalid template: {template}"
        
        return True, "Valid job-specific template request"
    
    def get_job_category_by_title(self, job_title: str) -> Optional[JobCategory]:
        """Suggest job category based on job title"""
        job_title_lower = job_title.lower()
        
        # Simple keyword matching - in production, you might use ML for better matching
        category_keywords = {
            JobCategory.SOFTWARE_ENGINEER: ["software", "developer", "engineer", "programmer", "coding"],
            JobCategory.DATA_SCIENTIST: ["data", "scientist", "analyst", "analytics", "machine learning"],
            JobCategory.PRODUCT_MANAGER: ["product", "manager", "pm"],
            JobCategory.NURSE_PRACTITIONER: ["nurse", "practitioner", "np"],
            JobCategory.FINANCIAL_MANAGER: ["financial", "finance", "manager", "accounting"],
            JobCategory.SALES_REPRESENTATIVE: ["sales", "representative", "account", "business development"],
            JobCategory.LAWYER: ["lawyer", "attorney", "legal", "counsel"],
            # Add more mappings as needed
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in job_title_lower for keyword in keywords):
                return category
        
        return None