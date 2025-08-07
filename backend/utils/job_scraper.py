import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import time
from typing import Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.timeout_config import TimeoutConfig

class JobScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        # Use configured timeout or fallback to 30 seconds
        try:
            self.timeout = TimeoutConfig.JOB_SCRAPING_TIMEOUT
        except:
            self.timeout = 30  # Fallback to 30 seconds if config not available
        
        # Phase 5: Enhanced scraping capabilities
        self.supported_domains = {
            'linkedin.com': self._scrape_linkedin,
            'indeed.com': self._scrape_indeed,
            'greenhouse.io': self._scrape_greenhouse,
            'boards.greenhouse.io': self._scrape_greenhouse,
            'lever.co': self._scrape_lever,
            'workday.com': self._scrape_workday,
            'bamboohr.com': self._scrape_bamboohr,
            'smartrecruiters.com': self._scrape_smartrecruiters
        }
    
    def scrape_job_description(self, url: str) -> Optional[str]:
        """
        Scrape job description from various job posting sites
        """
        try:
            print(f"🔍 DEBUG: Starting job scraper for URL: {url}")
            domain = urlparse(url).netloc.lower()
            print(f"🔍 DEBUG: Detected domain: {domain}")
            
            if 'linkedin.com' in domain:
                return self._scrape_linkedin(url)
            elif 'greenhouse.io' in domain or 'boards.greenhouse.io' in domain:
                return self._scrape_greenhouse(url)
            elif 'indeed.com' in domain:
                return self._scrape_indeed(url)
            else:
                # Generic scraper for other sites
                return self._scrape_generic(url)
                
        except requests.exceptions.Timeout:
            print(f"⏱️ Timeout scraping {url} after {self.timeout} seconds")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error scraping {url}: {str(e)}")
            return None
        except Exception as e:
            print(f"❌ Error scraping {url}: {str(e)}")
            return None
    
    def extract_job_title(self, url: str) -> Optional[str]:
        """
        Extract job title from job posting URL
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            domain = urlparse(url).netloc.lower()
            
            # Try different title selectors based on site
            title_selectors = []
            
            if 'linkedin.com' in domain:
                title_selectors = [
                    '.top-card-layout__title',
                    'h1[data-automation-id="job-title"]',
                    '.jobs-unified-top-card__job-title h1'
                ]
            elif 'greenhouse.io' in domain:
                title_selectors = [
                    'h1.app-title',
                    '.header h1',
                    '[data-automation="job-title"]'
                ]
            elif 'indeed.com' in domain:
                title_selectors = [
                    'h1[data-automation-id="jobTitle"]',
                    '.jobsearch-JobInfoHeader-title',
                    'h1.it2eXe'
                ]
            
            # Generic selectors that work for most sites
            title_selectors.extend([
                'h1',
                'title',
                '[class*="title"]',
                '[class*="job-title"]',
                '[data-testid*="title"]'
            ])
            
            for selector in title_selectors:
                element = soup.select_one(selector)
                if element:
                    title = element.get_text().strip()
                    # Clean up the title
                    title = re.sub(r'\s+', ' ', title)
                    title = re.sub(r'(- .+|\| .+)$', '', title)  # Remove company name suffixes
                    if len(title) > 3 and len(title) < 100:  # Reasonable title length
                        return title
            
            # Fallback: extract from page title
            page_title = soup.find('title')
            if page_title:
                title = page_title.get_text().strip()
                # Extract job title from page title (usually before company name or site name)
                title = re.split(r'[-|]', title)[0].strip()
                if len(title) > 3 and len(title) < 100:
                    return title
            
            return None
            
        except Exception as e:
            print(f"Error extracting job title from {url}: {str(e)}")
            return None
    
    def _scrape_linkedin(self, url: str) -> Optional[str]:
        """Scrape LinkedIn job posting"""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple selectors for job description
            selectors = [
                '.description__text',
                '.show-more-less-html__markup',
                '[data-automation-id="jobPostingDescription"]',
                '.jobs-description-content__text'
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    return self._clean_text(element.get_text())
            
            # Fallback: look for any div with job-related content
            job_content = soup.find('div', string=re.compile(r'(responsibilities|requirements|qualifications)', re.I))
            if job_content:
                return self._clean_text(job_content.get_text())
                
            return None
            
        except Exception as e:
            print(f"LinkedIn scraping error: {str(e)}")
            return None
    
    def _scrape_greenhouse(self, url: str) -> Optional[str]:
        """Scrape Greenhouse job posting"""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Greenhouse specific selectors
            selectors = [
                '#content',
                '.section-wrapper',
                '.job-post',
                '[data-automation="job-description"]'
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    return self._clean_text(element.get_text())
            
            return None
            
        except Exception as e:
            print(f"Greenhouse scraping error: {str(e)}")
            return None
    
    def _scrape_indeed(self, url: str) -> Optional[str]:
        """Scrape Indeed job posting"""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Indeed specific selectors
            selectors = [
                '#jobDescriptionText',
                '.jobsearch-jobDescriptionText',
                '[data-jk] .jobsearch-jobDescriptionText'
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    return self._clean_text(element.get_text())
            
            return None
            
        except Exception as e:
            print(f"Indeed scraping error: {str(e)}")
            return None
    
    def _scrape_generic(self, url: str) -> Optional[str]:
        """Generic scraper for other job sites"""
        try:
            print(f"🔍 DEBUG: Using generic scraper for {url}")
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            print(f"🔍 DEBUG: Got response, status: {response.status_code}")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            print(f"🔍 DEBUG: Parsed HTML, looking for job description patterns")
            
            # Look for common job description patterns
            job_keywords = ['description', 'responsibilities', 'requirements', 'qualifications', 'duties']
            
            for keyword in job_keywords:
                elements = soup.find_all(['div', 'section', 'article'], 
                                       class_=re.compile(keyword, re.I))
                if elements:
                    text = ' '.join([elem.get_text() for elem in elements])
                    if len(text) > 100:  # Ensure we have substantial content
                        return self._clean_text(text)
            
            # Fallback: get main content
            main_content = soup.find('main') or soup.find('body')
            if main_content:
                return self._clean_text(main_content.get_text())
            
            return None
            
        except Exception as e:
            print(f"Generic scraping error: {str(e)}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove common unwanted elements
        text = re.sub(r'(Show more|Show less|Read more|Read less)', '', text, flags=re.I)
        text = re.sub(r'Cookie Policy.*', '', text, flags=re.I)
        
        return text
    
    # ========================================
    # PHASE 5: Enhanced Job Source Compatibility
    # ========================================
    
    def _scrape_lever(self, url: str) -> Optional[str]:
        """Scrape Lever job posting"""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Lever specific selectors
            selectors = [
                '.section-wrapper .section',
                '.posting-requirements',
                '.posting-description',
                '[data-qa="job-description"]'
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    return self._clean_text(element.get_text())
            
            return None
            
        except Exception as e:
            print(f"Lever scraping error: {str(e)}")
            return None
    
    def _scrape_workday(self, url: str) -> Optional[str]:
        """Scrape Workday job posting"""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Workday specific selectors
            selectors = [
                '[data-automation-id="jobPostingDescription"]',
                '.jobPostingDescription',
                '[data-automation-id="jobPostingRequirements"]',
                '.wd-popup-content'
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    return self._clean_text(element.get_text())
            
            return None
            
        except Exception as e:
            print(f"Workday scraping error: {str(e)}")
            return None
    
    def _scrape_bamboohr(self, url: str) -> Optional[str]:
        """Scrape BambooHR job posting"""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # BambooHR specific selectors
            selectors = [
                '.BambooHR-ATS-Description',
                '.job-description',
                '[data-testid="job-description"]',
                '.posting-description'
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    return self._clean_text(element.get_text())
            
            return None
            
        except Exception as e:
            print(f"BambooHR scraping error: {str(e)}")
            return None
    
    def _scrape_smartrecruiters(self, url: str) -> Optional[str]:
        """Scrape SmartRecruiters job posting"""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # SmartRecruiters specific selectors
            selectors = [
                '.st-text-block',
                '[data-test-id="job-description"]',
                '.job-description-content',
                '.posting-description'
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    return self._clean_text(element.get_text())
            
            return None
            
        except Exception as e:
            print(f"SmartRecruiters scraping error: {str(e)}")
            return None
    
    def scrape_job_posting(self, url: str) -> dict:
        """Enhanced job posting scraper that returns structured data"""
        try:
            print(f"🔍 Enhanced scraping for URL: {url}")
            domain = urlparse(url).netloc.lower()
            
            # Get job description
            description = self.scrape_job_description(url)
            if not description:
                description = "Unable to extract job description"
            
            # Get job title
            title = self.extract_job_title(url)
            if not title:
                title = "Job Title Not Found"
            
            # Extract company name from domain or content
            company = self._extract_company_name(url, description)
            
            # Structure the job data
            job_data = {
                "title": title,
                "company": company,
                "description": description,
                "url": url,
                "source": domain,
                "requirements": self._extract_requirements(description),
                "skills": self._extract_skills(description)
            }
            
            print(f"✅ Successfully scraped: {title} at {company}")
            return job_data
            
        except Exception as e:
            print(f"❌ Error in enhanced job scraping: {str(e)}")
            return {
                "title": "Error extracting job",
                "company": "Unknown",
                "description": f"Error: {str(e)}",
                "url": url,
                "source": "error",
                "requirements": [],
                "skills": []
            }
    
    def _extract_company_name(self, url: str, description: str) -> str:
        """Extract company name from URL or description"""
        try:
            domain = urlparse(url).netloc.lower()
            
            # Extract from domain
            if 'linkedin.com' not in domain and 'indeed.com' not in domain:
                company_from_domain = domain.replace('www.', '').replace('.com', '').replace('.io', '')
                if len(company_from_domain) > 2:
                    return company_from_domain.title()
            
            # Extract from description using common patterns
            company_patterns = [
                r'(?:at|join|work for)\s+([A-Z][a-zA-Z\s&]+?)(?:\s+is|\s+we|\.|,)',
                r'([A-Z][a-zA-Z\s&]+?)\s+is\s+(?:looking|seeking|hiring)',
                r'Company:\s*([A-Z][a-zA-Z\s&]+?)(?:\n|\.|,)'
            ]
            
            for pattern in company_patterns:
                match = re.search(pattern, description)
                if match:
                    company = match.group(1).strip()
                    if len(company) > 2 and len(company) < 50:
                        return company
            
            return "Company Name Not Found"
            
        except Exception:
            return "Unknown Company"
    
    def _extract_requirements(self, description: str) -> list:
        """Extract job requirements from description"""
        try:
            requirements = []
            
            # Look for requirements sections
            req_patterns = [
                r'(?:requirements|qualifications|must have|required):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|$)',
                r'(?:you must have|you should have):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|$)'
            ]
            
            for pattern in req_patterns:
                matches = re.findall(pattern, description, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    # Split by bullet points or line breaks
                    items = re.split(r'[•\*\-]|\n', match)
                    for item in items:
                        item = item.strip()
                        if len(item) > 10 and len(item) < 200:
                            requirements.append(item)
            
            return requirements[:10]  # Limit to top 10
            
        except Exception:
            return []
    
    def _extract_skills(self, description: str) -> list:
        """Extract skills from job description"""
        try:
            # Common tech skills to look for
            common_skills = [
                'Python', 'JavaScript', 'Java', 'C++', 'React', 'Node.js', 'SQL', 'AWS', 'Docker',
                'Kubernetes', 'Git', 'HTML', 'CSS', 'TypeScript', 'Angular', 'Vue.js', 'MongoDB',
                'PostgreSQL', 'Redis', 'Elasticsearch', 'GraphQL', 'REST API', 'Microservices',
                'Machine Learning', 'Data Science', 'TensorFlow', 'PyTorch', 'Pandas', 'NumPy'
            ]
            
            found_skills = []
            description_lower = description.lower()
            
            for skill in common_skills:
                if skill.lower() in description_lower:
                    found_skills.append(skill)
            
            return found_skills
            
        except Exception:
            return []
    
    def process_manual_job_description(self, job_text: str, company_name: Optional[str] = None, job_title: Optional[str] = None) -> dict:
        """Process manually pasted job description"""
        try:
            print(f"📝 Processing manual job description")
            
            # Clean the text
            cleaned_description = self._clean_text(job_text)
            
            # Extract title if not provided
            if not job_title:
                title_patterns = [
                    r'^([A-Z][a-zA-Z\s-]+?)(?:\n|$)',
                    r'(?:position|role|job title):\s*([A-Z][a-zA-Z\s-]+?)(?:\n|$)',
                    r'we are hiring\s+(?:a|an)?\s*([A-Z][a-zA-Z\s-]+?)(?:\n|$)'
                ]
                
                for pattern in title_patterns:
                    match = re.search(pattern, cleaned_description, re.IGNORECASE)
                    if match:
                        job_title = match.group(1).strip()
                        break
                
                if not job_title:
                    job_title = "Manual Job Posting"
            
            # Extract company if not provided
            if not company_name:
                company_name = self._extract_company_name("", cleaned_description)
                if not company_name:
                    company_name = "Unknown Company"
            
            # Structure the job data
            job_data = {
                "title": job_title,
                "company": company_name,
                "description": cleaned_description,
                "url": "manual_input",
                "source": "manual",
                "requirements": self._extract_requirements(cleaned_description),
                "skills": self._extract_skills(cleaned_description)
            }
            
            print(f"✅ Successfully processed manual job: {job_title}")
            return job_data
            
        except Exception as e:
            print(f"❌ Error processing manual job description: {str(e)}")
            return {
                "title": job_title or "Manual Job Posting",
                "company": company_name or "Unknown Company",
                "description": job_text,
                "url": "manual_input",
                "source": "manual",
                "requirements": [],
                "skills": []
            } 