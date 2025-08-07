"""
ATS Scoring Service
Provides comprehensive ATS (Applicant Tracking System) compatibility scoring
"""

import re
from typing import Dict, List, Any

class ATSScorer:
    """ATS compatibility scoring system"""
    
    def calculate_ats_score(self, resume_text: str, job_description: str = "") -> Dict[str, Any]:
        """Calculate comprehensive ATS score"""
        
        # Calculate component scores
        keyword_score = self._score_keyword_match(resume_text, job_description)
        formatting_score = self._score_formatting(resume_text)
        structure_score = self._score_structure(resume_text)
        readability_score = self._score_readability(resume_text)
        completeness_score = self._score_completeness(resume_text)
        
        # Calculate overall score (weighted average)
        overall_score = (
            keyword_score * 0.3 +
            formatting_score * 0.2 +
            structure_score * 0.2 +
            readability_score * 0.15 +
            completeness_score * 0.15
        )
        
        # Determine grade
        grade = self._get_grade(overall_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            keyword_score, formatting_score, structure_score, 
            readability_score, completeness_score
        )
        
        return {
            'overall_score': round(overall_score, 1),
            'grade': grade,
            'component_scores': {
                'keyword_match': round(keyword_score, 1),
                'formatting': round(formatting_score, 1),
                'structure': round(structure_score, 1),
                'readability': round(readability_score, 1),
                'completeness': round(completeness_score, 1)
            },
            'recommendations': recommendations
        }
    
    def _score_keyword_match(self, resume_text: str, job_description: str) -> float:
        """Score keyword matching with job description"""
        if not job_description:
            return 75.0  # Default score when no job description
        
        resume_lower = resume_text.lower()
        job_lower = job_description.lower()
        
        # Extract keywords from job description
        job_keywords = set(re.findall(r'\b\w+\b', job_lower))
        job_keywords = {word for word in job_keywords if len(word) > 3}
        
        # Count matches
        matches = sum(1 for keyword in job_keywords if keyword in resume_lower)
        match_ratio = matches / len(job_keywords) if job_keywords else 0
        
        return min(100, match_ratio * 100)
    
    def _score_formatting(self, resume_text: str) -> float:
        """Score formatting quality"""
        score = 100.0
        
        # Check for common formatting issues
        if '\\bullet' in resume_text:
            score -= 15  # Literal bullet text
        if resume_text.count('\n\n') < 3:
            score -= 10  # Insufficient spacing
        if len(re.findall(r'[A-Z]{2,}', resume_text)) > 10:
            score -= 5   # Too much ALL CAPS
        
        return max(0, score)
    
    def _score_structure(self, resume_text: str) -> float:
        """Score resume structure"""
        score = 0.0
        sections = ['experience', 'education', 'skills', 'summary']
        
        for section in sections:
            if any(keyword in resume_text.lower() for keyword in [section, section.replace('e', 'a')]):
                score += 25
        
        return min(100, score)
    
    def _score_readability(self, resume_text: str) -> float:
        """Score readability"""
        lines = resume_text.split('\n')
        avg_line_length = sum(len(line) for line in lines) / len(lines) if lines else 0
        
        # Optimal line length is 60-80 characters
        if 60 <= avg_line_length <= 80:
            return 100.0
        elif 40 <= avg_line_length <= 100:
            return 80.0
        else:
            return 60.0
    
    def _score_completeness(self, resume_text: str) -> float:
        """Score resume completeness"""
        score = 0.0
        required_elements = [
            (r'@\w+\.\w+', 20),      # Email
            (r'\(\d{3}\)', 15),       # Phone
            (r'\b\d{4}\b', 15),       # Years/dates
            (r'•|·|\*', 25),          # Bullet points
            (r'[A-Z][a-z]+ [A-Z][a-z]+', 25)  # Name format
        ]
        
        for pattern, points in required_elements:
            if re.search(pattern, resume_text):
                score += points
        
        return min(100, score)
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 95:
            return 'A+'
        elif score >= 90:
            return 'A'
        elif score >= 85:
            return 'A-'
        elif score >= 80:
            return 'B+'
        elif score >= 75:
            return 'B'
        elif score >= 70:
            return 'B-'
        elif score >= 65:
            return 'C+'
        elif score >= 60:
            return 'C'
        else:
            return 'D'
    
    def _generate_recommendations(self, keyword_score: float, formatting_score: float, 
                                structure_score: float, readability_score: float, 
                                completeness_score: float) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        if keyword_score < 70:
            recommendations.append("Include more keywords from the job description")
        
        if formatting_score < 80:
            recommendations.append("Improve formatting consistency and remove special characters")
        
        if structure_score < 80:
            recommendations.append("Add clear section headers (Experience, Education, Skills)")
        
        if readability_score < 80:
            recommendations.append("Optimize line length and paragraph structure for better readability")
        
        if completeness_score < 80:
            recommendations.append("Ensure contact information and dates are clearly formatted")
        
        if not recommendations:
            recommendations.append("Great job! Your resume has excellent ATS compatibility")
        
        return recommendations
