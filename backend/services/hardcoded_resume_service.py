"""
Hardcoded Resume Service
Generates a specific resume format exactly as requested by the user.
This replaces all template and enhancement logic with a fixed format.
"""

from typing import Dict, Any
import re
from datetime import datetime
import os

class HardcodedResumeService:
    """Service that generates a hardcoded resume format with exact formatting"""
    
    @staticmethod
    def generate_hardcoded_resume(
        resume_text: str = "",
        job_description: str = "",
        job_title: str = "",
        **kwargs
    ) -> str:
        """
        Generate a hardcoded resume in the exact format requested.
        All parameters are ignored - this returns a fixed format.
        """
        
        # Single-source plain-text representation of the resume matching the olive-green PDF layout
        hardcoded_resume = """Manu Maddali
Product Manager
Atlanta, GA • Manumaddali7@gmail.com • (229) 449-0671

Summary
• Product Manager focused on building what users want while balancing technical feasibility.
• Built an AI resume optimizer that processes 25 applications simultaneously.
• Comfortable digging into APIs, presenting to executives, or debugging issues end-to-end.

Professional Experience

Product Manager | InComm Payments | Atlanta, GA | June 2022—Present
• Launched an innovative B2C Retail App; led product strategy and development.
• Grew monthly active users from 12K to 800K through data-driven enhancements and research.
• Managed adjudication workflow at Point-of-Sale for catalog pipeline.
• Acted as Product SME for catalog inventory management; improved internal tooling.
• Increased ICP and API usage by 73% across enterprise segments by building new REST APIs and docs.
• Reduced customer escalations by enabling self-serve features.
• Drove 60% support-ticket decrease across four products via targeted product improvements.
• Built PowerBI dashboards and aligned leadership with OKRs and KPIs.

Product Analyst Intern | Okta | San Francisco, CA | May 2021—August 2021
• Integrated internal platforms to improve engagement and collaboration with technical teams.
• Tracked platform performance with Analytics to improve training by 40% and user engagement.

Personal Projects | ApplyAI | June 2025—Present
• Designed an AI-powered resume optimization agent (OpenAI GPT-4o-mini, LangChain RAG).
• Implemented FAISS similarity search across 650+ jobs for context-aware tailoring.
• Built real-time batch processing with FastAPI; queues up to 25 jobs with 95% success.
• Engineered text processing pipeline (PyPDF2, pdfplumber, custom NLP) for robust parsing.

Education
• B.S. in Computer Science — University of Technology — GPA 3.7/4.0
• Coursework: Data Structures, Algorithms, Database Systems, Software Engineering

Skills
• Product: Roadmapping, Metrics (OKRs/KPIs), A/B Testing, User Research, Analytics
• Technical: Python, FastAPI, Node.js, React, SQL, AWS, Docker, Git
• Tools: PowerBI, JIRA, Confluence, Postman, Figma
"""

        return hardcoded_resume
    
    @staticmethod
    def generate_html_resume(resume_text: str = "", **kwargs) -> str:
        """Generate HTML version of the hardcoded resume"""
        
        resume_content = HardcodedResumeService.generate_hardcoded_resume()
        
        # Convert to HTML matching the olive-green single-page layout
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manu Maddali - Resume</title>
    <style>
        @page {{ size: Letter; margin: 0.75in; }}
        :root {{ --accent: #5c7d68; /* light olive green */ }}
        body {{
            font-family: 'Georgia', 'Times New Roman', Times, serif;
            color: #222;
            line-height: 1.45;
            max-width: 7.0in;
            margin: 0 auto;
            background: #fff;
        }}
        .header {{ text-align: center; margin-bottom: 8px; }}
        .name {{
            font-size: 30px;
            font-weight: 700;
            color: var(--accent);
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }}
        .contact {{
            font-size: 12.5px;
            color: #444;
        }}
        .rule {{
            height: 2px; background: #2b2b2b; margin: 10px 0 16px 0;
        }}
        h2 {{
            color: var(--accent);
            font-size: 16.5px;
            margin: 16px 0 8px 0;
            font-weight: 700;
        }}
        .role {{ margin-bottom: 10px; }}
        .role-head {{ display: flex; justify-content: space-between; align-items: baseline; }}
        .role-title {{ font-weight: 700; color: #2c2c2c; }}
        .role-dates {{ font-style: italic; color: #6b8b6f; font-size: 13px; }}
        .company {{ font-weight: 600; color: #2c2c2c; margin: 2px 0 6px 0; }}
        .company span {{ color: #666; font-weight: 400; }}
        ul {{ margin: 0 0 8px 18px; padding: 0; }}
        li {{ margin: 3px 0; }}
        .two-col {{ columns: 2; column-gap: 24px; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="name">Manu Maddali</div>
        <div class="contact">Atlanta, GA • Manumaddali7@gmail.com • (229) 449-0671</div>
    </div>
    <div class="rule"></div>

    <h2>Summary</h2>
    <ul>
        <li>Product Manager that finds the sweet spot between user needs and what’s technically possible.</li>
        <li>Built an AI resume optimizer that processes 25 applications simultaneously.</li>
        <li>Equally comfortable diving into APIs, presenting to executives, or solving tough bugs end‑to‑end.</li>
    </ul>

    <h2>Professional Experience</h2>
    <div class="role">
        <div class="role-head">
            <div class="role-title">Product Manger</div>
            <div class="role-dates">June 2022—Present</div>
        </div>
        <div class="company">InComm Payments, <span>Atlanta, GA</span></div>
        <ul>
            <li>Spearheaded launch of an innovative B2C Retail App; led strategy and delivery.</li>
            <li>Grew monthly active users from <strong>12K</strong> to <strong>800K</strong> using data‑driven insights.</li>
            <li>Managed retail catalog pipeline supporting adjudication at Point‑of‑Sale.</li>
            <li>Acted as <strong>Product SME</strong> for catalog platform; improved internal tooling.</li>
            <li>Expanded ICP and increased API usage by <strong>73%</strong> with new REST APIs and docs.</li>
            <li>Decreased support tickets by <strong>60%</strong> through targeted improvements.</li>
            <li>Built PowerBI dashboards for leadership to guide execution via OKRs and KPIs.</li>
        </ul>
    </div>

    <div class="role">
        <div class="role-head">
            <div class="role-title">Product Analyst Intern</div>
            <div class="role-dates">May 2021—August 2021</div>
        </div>
        <div class="company">Okta, <span>San Francisco, CA</span></div>
        <ul>
            <li>Drove integration of internal platforms; improved engagement and collaboration.</li>
            <li>Partnered with Analytics to track performance; improved training efficiency by <strong>40%</strong>.</li>
        </ul>
    </div>

    <h2>Personal Projects</h2>
    <div class="role">
        <div class="role-head">
            <div class="role-title">ApplyAI</div>
            <div class="role-dates">June 2025—Present</div>
        </div>
        <ul>
            <li>Designed AI resume optimizer (OpenAI GPT‑4o‑mini, LangChain RAG) achieving <strong>40%+</strong> keyword alignment.</li>
            <li>Built FAISS similarity search across <strong>650+</strong> job descriptions for context‑aware tailoring.</li>
            <li>Implemented FastAPI batch processing to queue up to <strong>25</strong> jobs with <strong>95%</strong> success rate.</li>
            <li>Engineered robust text pipeline (PyPDF2, pdfplumber, custom NLP) preserving professional structure.</li>
        </ul>
    </div>

    <h2>Education</h2>
    <ul>
        <li>B.S. in Computer Science — University of Technology — GPA 3.7/4.0</li>
        <li>Coursework: Data Structures, Algorithms, Database Systems, Software Engineering</li>
    </ul>

    <h2>Skills</h2>
    <ul>
        <li><strong>Product:</strong> Roadmapping, Metrics (OKRs/KPIs), A/B Testing, User Research, Analytics</li>
        <li><strong>Technical:</strong> Python, FastAPI, Node.js, React, SQL, AWS, Docker, Git</li>
        <li><strong>Tools:</strong> PowerBI, JIRA, Confluence, Postman, Figma</li>
    </ul>
</body>
</html>"""
        
        return html_content

    @staticmethod
    def get_static_pdf_bytes() -> bytes | None:
        """Return bytes of the static, approved PDF if available.

        We prefer this to guarantee exact look/spacing (olive design with bullets),
        matching the provided Resume_ManuM.pdf.
        """
        try:
            # Try absolute path first (workspace root) then backend root
            candidates = [
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Resume_ManuM.pdf'),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'Resume_ManuM.pdf'),
                os.path.abspath('Resume_ManuM.pdf')
            ]
            for p in candidates:
                if os.path.exists(p):
                    with open(p, 'rb') as f:
                        return f.read()
        except Exception as e:
            print(f"⚠️ Static PDF load failed: {e}")
        return None
