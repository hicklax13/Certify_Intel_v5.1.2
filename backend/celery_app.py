"""
Certify Intel - Celery Configuration
Async task queue for background processing.
"""
import os
from celery import Celery

# Get Redis URL from environment or use default
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "certify_intel",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["tasks"]
)

# Celery configuration
celery_app.conf.update(
    # Timezone
    timezone="UTC",
    enable_utc=True,
    
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    result_expires=3600,  # Results expire after 1 hour
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_concurrency=4,
    
    # Rate limiting
    task_annotations={
        "tasks.scrape_competitor": {"rate_limit": "10/m"},  # Max 10 scrapes per minute
        "tasks.run_discovery": {"rate_limit": "1/m"},       # Max 1 discovery per minute
    },
    
    # Beat schedule for periodic tasks
    beat_schedule={
        "weekly-full-refresh": {
            "task": "tasks.weekly_refresh",
            "schedule": 604800.0,  # 7 days in seconds
            "options": {"queue": "scheduled"}
        },
        "daily-high-priority-check": {
            "task": "tasks.check_high_priority",
            "schedule": 86400.0,  # 24 hours in seconds
            "options": {"queue": "scheduled"}
        },
        "daily-digest": {
            "task": "tasks.send_daily_digest",
            "schedule": 86400.0,
            "options": {"queue": "scheduled"}
        },
    }
)


# Task routing
celery_app.conf.task_routes = {
    "tasks.scrape_*": {"queue": "scraping"},
    "tasks.send_*": {"queue": "notifications"},
    "tasks.weekly_*": {"queue": "scheduled"},
    "tasks.run_*": {"queue": "discovery"},
}


if __name__ == "__main__":
    celery_app.start()
