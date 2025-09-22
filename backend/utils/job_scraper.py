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
            elif 'oraclecloud.com' in domain:
                return self._scrape_oracle_cloud(url)
            elif 'workday.com' in domain:
                return self._scrape_workday(url)
            else:
                # Enhanced generic scraper for ANY job posting URL
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
            
            # Try robust meta tags first (works even when content is gated/login)
            meta_title_selectors = [
                'meta[property="og:title"]',
                'meta[name="og:title"]',
                'meta[name="twitter:title"]',
                'meta[property="twitter:title"]'
            ]
            for selector in meta_title_selectors:
                element = soup.select_one(selector)
                if element and element.get('content'):
                    title = element.get('content').strip()
                    title = re.sub(r'\s+', ' ', title)
                    title = re.sub(r'(- .+|\| .+)$', '', title)
                    title = re.sub(r'\s*at\s+.*$', '', title, flags=re.IGNORECASE)
                    if 3 < len(title) < 100:
                        return title
            
            # Try different title selectors based on site
            title_selectors = []
            
            if 'linkedin.com' in domain:
                title_selectors = [
                    '.top-card-layout__title',
                    'h1.top-card-layout__title',
                    'h1[data-automation-id="job-title"]',
                    '.jobs-unified-top-card__job-title h1',
                    '.jobs-unified-top-card__job-title',
                    '[data-test-id="job-title"]'
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
            elif 'oraclecloud.com' in domain:
                # Oracle Cloud (used by JPMorgan Chase and other companies)
                title_selectors = [
                    'h1[data-automation-id="jobTitle"]',
                    '.jobTitle',
                    '.job-title',
                    'h1.job-posting-title',
                    '[data-testid="job-title"]',
                    '.posting-title'
                ]
            elif 'workday.com' in domain:
                title_selectors = [
                    'h1[data-automation-id="jobTitle"]',
                    '.jobTitle',
                    '[data-automation-id="job-title"]'
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
                
                # Handle different title formats
                if 'oraclecloud.com' in domain:
                    # Oracle Cloud format: "Job Title | Company Name | Oracle"
                    # Split by | and take the first part
                    parts = title.split('|')
                    if len(parts) > 0:
                        title = parts[0].strip()
                elif 'workday.com' in domain:
                    # Workday format: "Job Title - Company Name"
                    parts = title.split(' - ')
                    if len(parts) > 0:
                        title = parts[0].strip()
                elif 'linkedin.com' in domain:
                    # LinkedIn often formats as "<Job Title> | LinkedIn"
                    parts = title.split('|')
                    if parts:
                        title = parts[0].strip()
                else:
                    # Generic format: split by common separators
                    title = re.split(r'[-|–]', title)[0].strip()
                
                # Clean up common suffixes
                title = re.sub(r'\s*\(.*\)\s*$', '', title)  # Remove parentheses
                title = re.sub(r'\s*at\s+.*$', '', title, flags=re.IGNORECASE)  # Remove "at Company"
                title = re.sub(r'\s*\|.*$', '', title)  # Remove remaining | parts
                
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
            
            # Fallback to meta description if gated
            meta_desc = soup.select_one('meta[property="og:description"]') or soup.select_one('meta[name="description"]')
            if meta_desc and meta_desc.get('content'):
                content = meta_desc.get('content')
                if content and len(content) > 100:
                    return self._clean_text(content)
            
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
        """Enhanced generic scraper that can handle ANY job posting URL"""
        try:
            print(f"🔍 DEBUG: Using generic scraper for {url}")
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            print(f"🔍 DEBUG: Got response, status: {response.status_code}")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            print(f"🔍 DEBUG: Parsed HTML, looking for job description patterns")
            
            # Remove unwanted elements that clutter the content
            for element in soup(['nav', 'header', 'footer', 'aside', 'script', 'style', 'noscript']):
                element.decompose()
            
            # Strategy 1: Look for job-specific class/id patterns
            job_selectors = [
                # Common job description containers
                '[class*="job-description"]', '[id*="job-description"]',
                '[class*="job-details"]', '[id*="job-details"]',
                '[class*="description"]', '[id*="description"]',
                '[class*="content"]', '[id*="content"]',
                '[class*="posting"]', '[id*="posting"]',
                '[class*="requirements"]', '[id*="requirements"]',
                '[class*="responsibilities"]', '[id*="responsibilities"]',
                # Greenhouse/ATS patterns
                '.section-wrapper', '.content-intro', '.app-title',
                # Generic content containers
                'main', 'article', '.main-content', '#main-content'
            ]
            
            for selector in job_selectors:
                elements = soup.select(selector)
                print(f"🔍 DEBUG: Selector '{selector}' found {len(elements)} elements")
                for element in elements:
                    text = element.get_text(strip=True)
                    print(f"🔍 DEBUG: Element text length: {len(text)} chars")
                    if len(text) > 50:  # Only show preview for substantial content
                        print(f"🔍 DEBUG: Element preview: {text[:200]}...")
                    if self._is_job_content(text):
                        print(f"🔍 DEBUG: Found job content using selector: {selector}")
                        return self._clean_text(text)
            
            # Strategy 2: Look for text blocks with job-related keywords
            all_divs = soup.find_all(['div', 'section', 'article', 'p'])
            job_content_blocks = []
            
            for div in all_divs:
                text = div.get_text(strip=True)
                if self._is_job_content(text):
                    job_content_blocks.append((len(text), text))
            
            # Sort by length and take the longest meaningful content
            if job_content_blocks:
                job_content_blocks.sort(reverse=True)
                longest_content = job_content_blocks[0][1]
                print(f"🔍 DEBUG: Found job content by keyword analysis ({len(longest_content)} chars)")
                return self._clean_text(longest_content)
            
            # Strategy 3: Handle JavaScript-rendered content
            # For pages that load content dynamically, try to extract any meaningful text
            all_text = soup.get_text(strip=True)
            if len(all_text) > 500:  # Has substantial content
                # Look for job-related patterns in the full text
                job_patterns = [
                    r'(?i)(responsibilities?|duties|role|position|requirements?|qualifications?|experience|skills?)[:.]([^.]{100,1000})',
                    r'(?i)(what you.{0,20}do|about the role|job description)[:.]([^.]{100,1000})',
                    r'(?i)(we are looking|join our team|candidate will)([^.]{100,1000})'
                ]
                
                extracted_content = []
                for pattern in job_patterns:
                    matches = re.findall(pattern, all_text)
                    for match in matches:
                        if isinstance(match, tuple):
                            content = ' '.join(match).strip()
                        else:
                            content = match.strip()
                        if len(content) > 50:
                            extracted_content.append(content)
                
                if extracted_content:
                    combined_content = '\n'.join(extracted_content)
                    print(f"🔍 DEBUG: Extracted job patterns ({len(combined_content)} chars)")
                    return self._clean_text(combined_content)
            
            # Strategy 4: Fallback - get body but filter out navigation/footer content
            body = soup.find('body')
            if body:
                text = body.get_text(strip=True)
                # Filter out obvious non-job content
                filtered_text = self._filter_non_job_content(text)
                if len(filtered_text) > 200:
                    print(f"🔍 DEBUG: Using filtered body content ({len(filtered_text)} chars)")
                    return self._clean_text(filtered_text)
            
            print(f"🔍 DEBUG: All extraction strategies failed - likely JavaScript-rendered content")
            print(f"🔍 DEBUG: Consider using manual job description input for this URL")
            return None
            
        except Exception as e:
            print(f"Generic scraping error: {str(e)}")
            return None
    
    def _is_job_content(self, text: str) -> bool:
        """Determine if text block contains job description content"""
        if len(text) < 100:  # Too short to be meaningful job content
            return False
        
        # Look for job-related keywords
        job_indicators = [
            'responsibilities', 'requirements', 'qualifications', 'experience',
            'skills', 'duties', 'role', 'position', 'candidate', 'apply',
            'years of experience', 'bachelor', 'degree', 'preferred',
            'required', 'must have', 'should have', 'we are looking',
            'join our team', 'about the role', 'what you\'ll do',
            'minimum qualifications', 'preferred qualifications'
        ]
        
        text_lower = text.lower()
        job_keyword_count = sum(1 for keyword in job_indicators if keyword in text_lower)
        
        # Must have at least 3 job-related keywords to be considered job content
        return job_keyword_count >= 3
    
    def _filter_non_job_content(self, text: str) -> str:
        """Filter out navigation, footer, and other non-job content"""
        lines = text.split('\n')
        filtered_lines = []
        
        # Skip lines that look like navigation/footer content
        skip_patterns = [
            r'(home|about|contact|careers|privacy|terms|cookie)',
            r'(facebook|twitter|linkedin|instagram|youtube)',
            r'(©|copyright|all rights reserved)',
            r'(sign in|log in|register|subscribe)',
            r'(menu|navigation|footer|header)',
            r'^(\s*[A-Z][A-Z\s]{2,20}\s*)$',  # All caps navigation items
        ]
        
        for line in lines:
            line = line.strip()
            if len(line) < 10:  # Skip very short lines
                continue
                
            # Check if line matches skip patterns
            should_skip = False
            for pattern in skip_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    should_skip = True
                    break
            
            if not should_skip:
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
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
    
    def _scrape_oracle_cloud(self, url: str) -> Optional[str]:
        """Scrape Oracle Cloud job posting (used by JPMorgan Chase and other companies)"""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Oracle Cloud specific selectors
            selectors = [
                '[data-automation-id="jobPostingDescription"]',
                '.jobDescription',
                '.job-description',
                '.posting-description',
                '[class*="description"]',
                '.content',
                'main',
                '[role="main"]'
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text(strip=True)
                    if self._is_job_content(text):
                        print(f"✅ Oracle Cloud scraping successful using selector: {selector}")
                        return self._clean_text(text)
            
            # Fallback to generic scraping
            return self._scrape_generic(url)
            
        except Exception as e:
            print(f"❌ Oracle Cloud scraping failed for {url}: {str(e)}")
            return None
    
 