"""
Timeout Configuration for Apply.AI Backend
Manages all timeout settings for different operations
"""

import os
from typing import Dict

class TimeoutConfig:
    """Centralized timeout configuration for all operations"""
    
    # Server-level timeouts
    SERVER_KEEP_ALIVE = int(os.getenv("SERVER_KEEP_ALIVE_TIMEOUT", "300"))  # 5 minutes default
    SERVER_GRACEFUL_SHUTDOWN = int(os.getenv("SERVER_GRACEFUL_SHUTDOWN", "60"))  # 60 seconds
    
    # Request timeouts
    DEFAULT_REQUEST_TIMEOUT = int(os.getenv("DEFAULT_REQUEST_TIMEOUT", "30"))  # 30 seconds
    BATCH_PROCESSING_TIMEOUT = int(os.getenv("BATCH_PROCESSING_TIMEOUT", "1800"))  # 30 minutes
    
    # Job processing timeouts
    JOB_SCRAPING_TIMEOUT = int(os.getenv("JOB_SCRAPING_TIMEOUT", "30"))  # 30 seconds per job
    SINGLE_JOB_PROCESSING_TIMEOUT = int(os.getenv("SINGLE_JOB_TIMEOUT", "120"))  # 2 minutes per job
    
    # Batch processing settings
    MAX_CONCURRENT_JOBS = int(os.getenv("MAX_CONCURRENT_JOBS", "5"))  # Process 5 jobs at once
    MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", "25"))  # Maximum 25 jobs per batch
    
    # Polling and retry settings
    STATUS_POLL_INTERVAL = int(os.getenv("STATUS_POLL_INTERVAL", "2"))  # 2 seconds
    MAX_POLL_ATTEMPTS = int(os.getenv("MAX_POLL_ATTEMPTS", "900"))  # 900 * 2s = 30 minutes
    
    @classmethod
    def get_timeout_for_batch_size(cls, batch_size: int) -> int:
        """Calculate appropriate timeout based on batch size"""
        # Base timeout + additional time per job
        base_timeout = 60  # 1 minute base
        per_job_timeout = cls.SINGLE_JOB_PROCESSING_TIMEOUT
        
        # Calculate total timeout with a maximum cap
        total_timeout = base_timeout + (batch_size * per_job_timeout)
        return min(total_timeout, cls.BATCH_PROCESSING_TIMEOUT)
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, int]:
        """Get all timeout configurations as a dictionary"""
        return {
            "server_keep_alive": cls.SERVER_KEEP_ALIVE,
            "server_graceful_shutdown": cls.SERVER_GRACEFUL_SHUTDOWN,
            "default_request_timeout": cls.DEFAULT_REQUEST_TIMEOUT,
            "batch_processing_timeout": cls.BATCH_PROCESSING_TIMEOUT,
            "job_scraping_timeout": cls.JOB_SCRAPING_TIMEOUT,
            "single_job_timeout": cls.SINGLE_JOB_PROCESSING_TIMEOUT,
            "max_concurrent_jobs": cls.MAX_CONCURRENT_JOBS,
            "max_batch_size": cls.MAX_BATCH_SIZE,
            "status_poll_interval": cls.STATUS_POLL_INTERVAL,
            "max_poll_attempts": cls.MAX_POLL_ATTEMPTS
        }