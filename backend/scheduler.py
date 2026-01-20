"""
Certify Intel - Automated Scheduler
Runs weekly scraping jobs and data refresh.
"""
import os
import asyncio
from datetime import datetime
from typing import List, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from scraper import CompetitorScraper, ScrapeResult
from extractor import GPTExtractor, ExtractedData
from database import SessionLocal, Competitor, ChangeLog

# Initialize scheduler
scheduler = AsyncIOScheduler()


class CompetitorRefreshJob:
    """Job that scrapes and updates competitor data."""
    
    def __init__(self):
        self.scraper = None
        self.extractor = GPTExtractor()
        
    async def run_full_refresh(self, competitor_ids: Optional[List[int]] = None):
        """Run a full data refresh for all or specified competitors."""
        print(f"[{datetime.now()}] Starting competitor refresh job...")
        
        db = SessionLocal()
        
        # Get competitors to refresh
        if competitor_ids:
            competitors = db.query(Competitor).filter(
                Competitor.id.in_(competitor_ids),
                Competitor.is_deleted == False
            ).all()
        else:
            competitors = db.query(Competitor).filter(
                Competitor.is_deleted == False
            ).all()
        
        print(f"Refreshing {len(competitors)} competitors...")
        
        results = []
        
        async with CompetitorScraper(headless=True) as scraper:
            for competitor in competitors:
                try:
                    # Scrape competitor website
                    scrape_result = await scraper.scrape_competitor(
                        name=competitor.name,
                        website=competitor.website,
                        pages_to_scrape=["homepage", "pricing", "about"]
                    )
                    
                    if scrape_result.success and scrape_result.pages:
                        # Extract data from scraped content
                        extractions = []
                        for page in scrape_result.pages:
                            extracted = self.extractor.extract_from_content(
                                competitor.name,
                                page.content,
                                page.page_type
                            )
                            extractions.append(extracted)
                        
                        # Merge extractions
                        merged = self.extractor.merge_extractions(extractions)
                        
                        # Update competitor with new data and detect changes
                        changes = self._update_competitor(db, competitor, merged)
                        
                        results.append({
                            "competitor": competitor.name,
                            "success": True,
                            "pages_scraped": len(scrape_result.pages),
                            "changes_detected": len(changes)
                        })
                    else:
                        results.append({
                            "competitor": competitor.name,
                            "success": False,
                            "error": scrape_result.error or "No pages scraped"
                        })
                        
                except Exception as e:
                    results.append({
                        "competitor": competitor.name,
                        "success": False,
                        "error": str(e)
                    })
        
        db.close()
        
        print(f"[{datetime.now()}] Refresh complete. Results: {len([r for r in results if r['success']])} success, {len([r for r in results if not r['success']])} failed")
        return results
    
    def _update_competitor(self, db, competitor: Competitor, extracted: ExtractedData) -> List[ChangeLog]:
        """Update competitor data and log changes."""
        changes = []
        
        # Fields to check for changes
        field_mappings = {
            "pricing_model": extracted.pricing_model,
            "base_price": extracted.base_price,
            "price_unit": extracted.price_unit,
            "product_categories": extracted.product_categories,
            "key_features": extracted.key_features,
            "integration_partners": extracted.integration_partners,
            "certifications": extracted.certifications,
            "target_segments": extracted.target_segments,
            "customer_size_focus": extracted.customer_size_focus,
            "geographic_focus": extracted.geographic_focus,
            "customer_count": extracted.customer_count,
            "key_customers": extracted.key_customers,
            "employee_count": extracted.employee_count,
            "year_founded": extracted.year_founded,
            "headquarters": extracted.headquarters,
            "funding_total": extracted.funding_total,
            "recent_launches": extracted.recent_launches,
        }
        
        for field, new_value in field_mappings.items():
            if new_value is not None:
                old_value = getattr(competitor, field)
                
                # Check if value changed
                if old_value != new_value and new_value != "Unknown":
                    # Determine severity based on field
                    severity = self._get_change_severity(field, old_value, new_value)
                    
                    # Log the change
                    change = ChangeLog(
                        competitor_id=competitor.id,
                        competitor_name=competitor.name,
                        change_type=field.replace("_", " ").title(),
                        previous_value=str(old_value) if old_value else None,
                        new_value=str(new_value),
                        source="Auto-scrape",
                        severity=severity
                    )
                    db.add(change)
                    changes.append(change)
                    
                    # Update the field
                    setattr(competitor, field, new_value)
        
        # Update last_updated timestamp
        competitor.last_updated = datetime.utcnow()
        
        # Update data quality score if available
        if extracted.confidence_score:
            competitor.data_quality_score = int(extracted.confidence_score)
        
        db.commit()
        
        return changes
    
    def _get_change_severity(self, field: str, old_value, new_value) -> str:
        """Determine the severity of a change."""
        high_priority_fields = ["pricing_model", "base_price", "funding_total", "customer_count"]
        medium_priority_fields = ["key_features", "integration_partners", "target_segments"]
        
        if field in high_priority_fields:
            return "High"
        elif field in medium_priority_fields:
            return "Medium"
        else:
            return "Low"


# Scheduler functions

def schedule_weekly_refresh():
    """Schedule weekly competitor refresh job."""
    job = CompetitorRefreshJob()
    
    # Run every Sunday at 2 AM
    scheduler.add_job(
        lambda: asyncio.create_task(job.run_full_refresh()),
        CronTrigger(day_of_week="sun", hour=2, minute=0),
        id="weekly_competitor_refresh",
        name="Weekly Competitor Refresh",
        replace_existing=True
    )
    
    print("Scheduled weekly refresh job for Sundays at 2 AM")


def schedule_daily_high_priority_check():
    """Schedule daily check for high-priority competitors."""
    job = CompetitorRefreshJob()
    
    # Get high-threat competitor IDs
    db = SessionLocal()
    high_threat_ids = [
        c.id for c in db.query(Competitor).filter(
            Competitor.threat_level == "High",
            Competitor.is_deleted == False
        ).all()
    ]
    db.close()
    
    if high_threat_ids:
        # Run daily at 6 AM for high-threat competitors only
        scheduler.add_job(
            lambda: asyncio.create_task(job.run_full_refresh(high_threat_ids)),
            CronTrigger(hour=6, minute=0),
            id="daily_high_priority_check",
            name="Daily High Priority Check",
            replace_existing=True
        )
        
        print(f"Scheduled daily check for {len(high_threat_ids)} high-priority competitors at 6 AM")


def start_scheduler():
    """Start the scheduler with all jobs."""
    schedule_weekly_refresh()
    schedule_daily_high_priority_check()
    scheduler.start()
    print("Scheduler started!")


def stop_scheduler():
    """Stop the scheduler."""
    scheduler.shutdown()
    print("Scheduler stopped.")


# Manual trigger functions

async def trigger_refresh_now(competitor_ids: Optional[List[int]] = None):
    """Manually trigger a refresh."""
    job = CompetitorRefreshJob()
    return await job.run_full_refresh(competitor_ids)


if __name__ == "__main__":
    # Test scheduler
    print("Testing scheduler...")
    start_scheduler()
    
    # Keep running
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        stop_scheduler()
