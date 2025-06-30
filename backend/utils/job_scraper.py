import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import time
from typing import Optional

class JobScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def scrape_job_description(self, url: str) -> Optional[str]:
        """
        Scrape job description from various job posting sites
        """
        try:
            domain = urlparse(url).netloc.lower()
            
            if 'linkedin.com' in domain:
                return self._scrape_linkedin(url)
            elif 'greenhouse.io' in domain or 'boards.greenhouse.io' in domain:
                return self._scrape_greenhouse(url)
            elif 'indeed.com' in domain:
                return self._scrape_indeed(url)
            else:
                # Generic scraper for other sites
                return self._scrape_generic(url)
                
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None
    
    def extract_job_title(self, url: str) -> Optional[str]:
        """
        Extract job title from job posting URL
        """
        try:
            response = requests.get(url, headers=self.headers)
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
            response = requests.get(url, headers=self.headers)
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
            response = requests.get(url, headers=self.headers)
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
            response = requests.get(url, headers=self.headers)
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
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
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