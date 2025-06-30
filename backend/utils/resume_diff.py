import difflib
import re
from typing import Dict, List, Tuple, Any
from Levenshtein import distance
from datetime import datetime
import json

class ResumeDiffAnalyzer:
    def __init__(self):
        self.diff_types = {
            'added': '✅ ADDED',
            'removed': '❌ REMOVED', 
            'modified': '🔄 MODIFIED',
            'reordered': '↕️ REORDERED',
            'enhanced': '⬆️ ENHANCED'
        }
    
    def analyze_resume_diff(self, original_text: str, tailored_text: str, job_title: str = "") -> Dict[str, Any]:
        """Comprehensive diff analysis between original and tailored resumes"""
        
        # Parse resumes into structured sections
        original_sections = self._parse_resume_sections(original_text)
        tailored_sections = self._parse_resume_sections(tailored_text)
        
        # Analyze different types of changes
        diff_analysis = {
            "job_title": job_title,
            "analysis_timestamp": datetime.now().isoformat(),
            "summary": self._create_diff_summary(original_sections, tailored_sections),
            "section_changes": self._analyze_section_changes(original_sections, tailored_sections),
            "content_changes": self._analyze_content_changes(original_text, tailored_text),
            "enhancement_score": self._calculate_enhancement_score(original_text, tailored_text),
            "detailed_diff": self._create_detailed_diff(original_text, tailored_text)
        }
        
        return diff_analysis
    
    def _parse_resume_sections(self, text: str) -> Dict[str, str]:
        """Parse resume into logical sections"""
        sections = {}
        current_section = "header"
        current_content = []
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect section headers
            if self._is_section_header(line):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                
                # Start new section
                current_section = self._normalize_section_name(line)
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _is_section_header(self, line: str) -> bool:
        """Determine if line is a section header"""
        common_headers = [
            'professional summary', 'summary', 'objective', 'profile',
            'experience', 'work experience', 'professional experience', 'employment',
            'education', 'academic background',
            'skills', 'technical skills', 'core competencies', 'expertise',
            'projects', 'key projects', 'notable projects',
            'certifications', 'licenses', 'achievements', 'awards',
            'languages', 'interests', 'volunteer', 'activities'
        ]
        
        line_lower = line.lower().strip()
        
        # Check exact matches
        if line_lower in common_headers:
            return True
        
        # Check partial matches
        for header in common_headers:
            if header in line_lower and len(line_lower) < 50:
                return True
        
        # Check if all caps and short (likely header)
        if line.isupper() and len(line) < 40 and len(line.split()) <= 4:
            return True
        
        return False
    
    def _normalize_section_name(self, header: str) -> str:
        """Normalize section names for comparison"""
        header_lower = header.lower().strip()
        
        if 'summary' in header_lower or 'objective' in header_lower or 'profile' in header_lower:
            return 'summary'
        elif 'experience' in header_lower or 'employment' in header_lower:
            return 'experience'
        elif 'education' in header_lower:
            return 'education'
        elif 'skill' in header_lower or 'competenc' in header_lower or 'expertise' in header_lower:
            return 'skills'
        elif 'project' in header_lower:
            return 'projects'
        elif 'certification' in header_lower or 'license' in header_lower:
            return 'certifications'
        else:
            return header_lower.replace(' ', '_')
    
    def _create_diff_summary(self, original_sections: Dict, tailored_sections: Dict) -> Dict[str, Any]:
        """Create high-level summary of changes"""
        
        original_keys = set(original_sections.keys())
        tailored_keys = set(tailored_sections.keys())
        
        added_sections = tailored_keys - original_keys
        removed_sections = original_keys - tailored_keys
        common_sections = original_keys & tailored_keys
        
        modified_sections = []
        for section in common_sections:
            if original_sections[section] != tailored_sections[section]:
                modified_sections.append(section)
        
        return {
            "total_sections_original": len(original_sections),
            "total_sections_tailored": len(tailored_sections),
            "sections_added": list(added_sections),
            "sections_removed": list(removed_sections),
            "sections_modified": modified_sections,
            "modification_percentage": round((len(modified_sections) / max(len(common_sections), 1)) * 100, 1)
        }
    
    def _analyze_section_changes(self, original_sections: Dict, tailored_sections: Dict) -> Dict[str, Any]:
        """Detailed analysis of changes in each section"""
        
        section_analysis = {}
        all_sections = set(original_sections.keys()) | set(tailored_sections.keys())
        
        for section in all_sections:
            original_content = original_sections.get(section, "")
            tailored_content = tailored_sections.get(section, "")
            
            if not original_content and tailored_content:
                # Section was added
                section_analysis[section] = {
                    "change_type": "added",
                    "description": f"New {section} section added",
                    "content_preview": tailored_content[:200] + "..." if len(tailored_content) > 200 else tailored_content
                }
            elif original_content and not tailored_content:
                # Section was removed
                section_analysis[section] = {
                    "change_type": "removed",
                    "description": f"{section.title()} section removed",
                    "original_preview": original_content[:200] + "..." if len(original_content) > 200 else original_content
                }
            elif original_content and tailored_content:
                # Section was potentially modified
                similarity = self._calculate_similarity(original_content, tailored_content)
                
                if similarity < 0.8:  # Significant changes
                    changes = self._identify_specific_changes(original_content, tailored_content)
                    section_analysis[section] = {
                        "change_type": "modified",
                        "similarity_score": round(similarity, 3),
                        "description": f"{section.title()} section significantly modified",
                        "specific_changes": changes,
                        "original_length": len(original_content),
                        "tailored_length": len(tailored_content)
                    }
                elif similarity < 0.95:  # Minor enhancements
                    section_analysis[section] = {
                        "change_type": "enhanced",
                        "similarity_score": round(similarity, 3),
                        "description": f"{section.title()} section enhanced with better language",
                        "original_length": len(original_content),
                        "tailored_length": len(tailored_content)
                    }
        
        return section_analysis
    
    def _identify_specific_changes(self, original: str, tailored: str) -> List[Dict[str, str]]:
        """Identify specific changes between two text blocks"""
        changes = []
        
        # Use difflib to find differences
        matcher = difflib.SequenceMatcher(None, original.split(), tailored.split())
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                changes.append({
                    "type": "replaced",
                    "original": " ".join(original.split()[i1:i2]),
                    "tailored": " ".join(tailored.split()[j1:j2])
                })
            elif tag == 'delete':
                changes.append({
                    "type": "removed",
                    "original": " ".join(original.split()[i1:i2]),
                    "tailored": ""
                })
            elif tag == 'insert':
                changes.append({
                    "type": "added",
                    "original": "",
                    "tailored": " ".join(tailored.split()[j1:j2])
                })
        
        return changes[:10]  # Limit to top 10 changes for readability
    
    def _analyze_content_changes(self, original: str, tailored: str) -> Dict[str, Any]:
        """Analyze overall content changes"""
        
        # Word-level analysis
        original_words = set(original.lower().split())
        tailored_words = set(tailored.lower().split())
        
        added_words = tailored_words - original_words
        removed_words = original_words - tailored_words
        common_words = original_words & tailored_words
        
        # Sentence analysis
        original_sentences = len(re.split(r'[.!?]+', original))
        tailored_sentences = len(re.split(r'[.!?]+', tailored))
        
        # Keyword analysis (look for action verbs and industry terms)
        action_verbs = {
            'led', 'managed', 'developed', 'implemented', 'created', 'designed', 
            'improved', 'increased', 'reduced', 'optimized', 'launched', 'built',
            'spearheaded', 'drove', 'delivered', 'achieved', 'collaborated'
        }
        
        original_action_verbs = action_verbs & original_words
        tailored_action_verbs = action_verbs & tailored_words
        
        return {
            "word_count_change": len(tailored.split()) - len(original.split()),
            "sentence_count_change": tailored_sentences - original_sentences,
            "words_added": len(added_words),
            "words_removed": len(removed_words),
            "vocabulary_expansion": len(added_words) / max(len(original_words), 1),
            "action_verbs_original": len(original_action_verbs),
            "action_verbs_tailored": len(tailored_action_verbs),
            "action_verb_improvement": len(tailored_action_verbs) - len(original_action_verbs),
            "new_keywords": list(added_words)[:20]  # Top 20 new keywords
        }
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        # Use Levenshtein distance for character-level similarity
        max_len = max(len(text1), len(text2))
        if max_len == 0:
            return 1.0
        
        edit_distance = distance(text1, text2)
        similarity = 1 - (edit_distance / max_len)
        
        return max(0.0, similarity)
    
    def _calculate_enhancement_score(self, original: str, tailored: str) -> Dict[str, Any]:
        """Calculate overall enhancement score"""
        
        # Factors for enhancement scoring
        length_factor = len(tailored) / max(len(original), 1)
        
        # Count professional keywords
        professional_keywords = {
            'strategic', 'leadership', 'management', 'optimization', 'efficiency',
            'innovation', 'collaboration', 'cross-functional', 'stakeholder',
            'revenue', 'growth', 'performance', 'results', 'impact', 'value'
        }
        
        original_pro_words = len([w for w in original.lower().split() if w in professional_keywords])
        tailored_pro_words = len([w for w in tailored.lower().split() if w in professional_keywords])
        
        professional_enhancement = tailored_pro_words / max(original_pro_words, 1)
        
        # Calculate overall score
        enhancement_score = min(100, (
            (length_factor * 30) +
            (professional_enhancement * 40) +
            (30 if length_factor > 0.9 else 20)  # Bonus for maintaining content
        ))
        
        return {
            "overall_score": round(enhancement_score, 1),
            "length_factor": round(length_factor, 2),
            "professional_enhancement": round(professional_enhancement, 2),
            "professional_keywords_added": tailored_pro_words - original_pro_words,
            "assessment": self._get_enhancement_assessment(enhancement_score)
        }
    
    def _get_enhancement_assessment(self, score: float) -> str:
        """Get qualitative assessment of enhancement"""
        if score >= 85:
            return "Excellent enhancement with significant improvements"
        elif score >= 70:
            return "Good enhancement with notable improvements"
        elif score >= 55:
            return "Moderate enhancement with some improvements"
        else:
            return "Minimal enhancement - consider further optimization"
    
    def _create_detailed_diff(self, original: str, tailored: str) -> List[Dict[str, str]]:
        """Create detailed line-by-line diff"""
        
        diff_lines = []
        differ = difflib.unified_diff(
            original.splitlines(),
            tailored.splitlines(),
            fromfile='Original Resume',
            tofile='Tailored Resume',
            lineterm=''
        )
        
        for line in differ:
            if line.startswith('+++') or line.startswith('---') or line.startswith('@@'):
                continue
            elif line.startswith('+'):
                diff_lines.append({
                    "type": "added",
                    "content": line[1:],
                    "marker": "✅"
                })
            elif line.startswith('-'):
                diff_lines.append({
                    "type": "removed", 
                    "content": line[1:],
                    "marker": "❌"
                })
            else:
                diff_lines.append({
                    "type": "unchanged",
                    "content": line,
                    "marker": "="
                })
        
        return diff_lines[:50]  # Limit for performance
    
    def create_diff_report(self, diff_analysis: Dict[str, Any]) -> str:
        """Create human-readable diff report"""
        
        report = f"""
# 📊 RESUME TAILORING ANALYSIS REPORT

**Job Title:** {diff_analysis.get('job_title', 'N/A')}
**Analysis Date:** {diff_analysis.get('analysis_timestamp', 'N/A')}

## 🎯 ENHANCEMENT SCORE: {diff_analysis['enhancement_score']['overall_score']}/100
**Assessment:** {diff_analysis['enhancement_score']['assessment']}

## 📋 SUMMARY OF CHANGES:
- **Sections Modified:** {len(diff_analysis['summary']['sections_modified'])}
- **Sections Added:** {len(diff_analysis['summary']['sections_added'])}
- **Sections Removed:** {len(diff_analysis['summary']['sections_removed'])}
- **Modification Rate:** {diff_analysis['summary']['modification_percentage']}%

## 📈 CONTENT IMPROVEMENTS:
- **Words Added:** {diff_analysis['content_changes']['words_added']}
- **Action Verbs Enhanced:** {diff_analysis['content_changes']['action_verb_improvement']}
- **Professional Keywords Added:** {diff_analysis['enhancement_score']['professional_keywords_added']}

## 🔍 KEY CHANGES BY SECTION:
"""
        
        for section, changes in diff_analysis['section_changes'].items():
            report += f"\n**{section.upper()}:** {changes['description']}"
            if 'similarity_score' in changes:
                report += f" (Similarity: {changes['similarity_score']})"
        
        return report 