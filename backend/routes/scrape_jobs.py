from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
import asyncio
from utils.job_scraper import JobScraper

router = APIRouter()
job_scraper = JobScraper()

class JobURLs(BaseModel):
    urls: List[str]

class SingleJobURL(BaseModel):
    job_url: str

@router.post("/scrape")
async def scrape_single_job(request: SingleJobURL):
    """
    Scrape a single job description from provided URL
    """
    try:
        if not request.job_url.strip():
            raise HTTPException(
                status_code=400,
                detail="Job URL is required"
            )
        
        url = request.job_url.strip()
        
        # Scrape job description
        job_description = job_scraper.scrape_job_description(url)
        
        if not job_description:
            return JSONResponse({
                "success": False,
                "detail": "Could not extract job description from this URL"
            })
        
        # Extract job title if possible
        job_title = job_scraper.extract_job_title(url)
        
        return JSONResponse({
            "success": True,
            "job_description": job_description,
            "job_title": job_title or "Product Manager",
            "job_url": url,
            "preview": job_description[:200] + "..." if len(job_description) > 200 else job_description
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "detail": f"Error scraping job: {str(e)}"
        })

@router.post("/scrape-jobs")
async def scrape_job_descriptions(job_urls: JobURLs):
    """
    Scrape job descriptions from provided URLs
    """
    try:
        if len(job_urls.urls) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 job URLs allowed"
            )
        
        if not job_urls.urls:
            raise HTTPException(
                status_code=400,
                detail="At least one job URL is required"
            )
        
        scraped_jobs = []
        
        for i, url in enumerate(job_urls.urls):
            try:
                # Scrape job description
                job_description = job_scraper.scrape_job_description(url.strip())
                
                if job_description:
                    scraped_jobs.append({
                        "id": i + 1,
                        "url": url.strip(),
                        "job_description": job_description,
                        "status": "success",
                        "preview": job_description[:200] + "..." if len(job_description) > 200 else job_description
                    })
                else:
                    scraped_jobs.append({
                        "id": i + 1,
                        "url": url.strip(),
                        "job_description": None,
                        "status": "failed",
                        "error": "Could not extract job description"
                    })
                    
            except Exception as e:
                scraped_jobs.append({
                    "id": i + 1,
                    "url": url.strip(),
                    "job_description": None,
                    "status": "failed",
                    "error": str(e)
                })
        
        successful_jobs = [job for job in scraped_jobs if job["status"] == "success"]
        
        return JSONResponse({
            "message": f"Scraped {len(successful_jobs)} out of {len(job_urls.urls)} job descriptions",
            "total_jobs": len(job_urls.urls),
            "successful_scrapes": len(successful_jobs),
            "failed_scrapes": len(job_urls.urls) - len(successful_jobs),
            "jobs": scraped_jobs
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scraping job descriptions: {str(e)}")

@router.get("/test-scrape")
async def test_scrape(url: str):
    """
    Test endpoint to scrape a single job URL
    """
    try:
        job_description = job_scraper.scrape_job_description(url)
        
        if not job_description:
            return JSONResponse({
                "url": url,
                "status": "failed",
                "error": "Could not extract job description"
            })
        
        return JSONResponse({
            "url": url,
            "status": "success",
            "job_description": job_description,
            "preview": job_description[:300] + "..." if len(job_description) > 300 else job_description
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing scrape: {str(e)}") 