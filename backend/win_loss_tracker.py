"""
Certify Intel - Win/Loss Tracker
Tracks competitive deals and outcomes.
"""
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship


@dataclass
class WinLossStats:
    """Win/Loss statistics."""
    total_deals: int
    wins: int
    losses: int
    win_rate: float
    total_value_won: float
    total_value_lost: float
    by_competitor: Dict[str, Dict[str, Any]]
    loss_reasons: Dict[str, int]
    monthly_trend: List[Dict[str, Any]]


class WinLossTracker:
    """Tracks competitive deal outcomes."""
    
    def __init__(self, db_session=None):
        self.db = db_session
        self._deals = []  # In-memory storage fallback
    
    def log_deal(self, 
                 competitor_id: int,
                 competitor_name: str,
                 deal_name: str,
                 deal_value: Optional[float],
                 outcome: str,
                 loss_reason: Optional[str] = None,
                 notes: Optional[str] = None) -> Dict[str, Any]:
        """
        Log a competitive deal outcome.
        
        Args:
            competitor_id: ID of the competitor
            competitor_name: Name of the competitor
            deal_name: Name of the deal/opportunity
            deal_value: Value in dollars
            outcome: "Won" or "Lost"
            loss_reason: Reason for loss (if applicable)
            notes: Additional notes
            
        Returns:
            Dict with logged deal info
        """
        deal = {
            "id": len(self._deals) + 1,
            "competitor_id": competitor_id,
            "competitor_name": competitor_name,
            "deal_name": deal_name,
            "deal_value": deal_value or 0,
            "outcome": outcome,
            "loss_reason": loss_reason,
            "notes": notes,
            "logged_at": datetime.utcnow().isoformat()
        }
        
        self._deals.append(deal)
        
        # If we have a database, persist
        if self.db:
            try:
                from main import ChangeLog
                
                change = ChangeLog(
                    competitor_id=competitor_id,
                    competitor_name=competitor_name,
                    change_type=f"Deal {outcome}",
                    new_value=f"{deal_name} (${deal_value:,.0f})" if deal_value else deal_name,
                    previous_value=loss_reason if outcome == "Lost" else None,
                    source="Win/Loss Tracker",
                    severity="High" if outcome == "Lost" and deal_value and deal_value > 100000 else "Medium"
                )
                self.db.add(change)
                self.db.commit()
            except Exception as e:
                print(f"Error persisting deal: {e}")
        
        return deal
    
    def get_stats(self, days: int = 365) -> WinLossStats:
        """
        Get win/loss statistics.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            WinLossStats with comprehensive analysis
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        # Filter deals by date
        recent_deals = [
            d for d in self._deals 
            if datetime.fromisoformat(d["logged_at"]) >= cutoff
        ]
        
        wins = [d for d in recent_deals if d["outcome"] == "Won"]
        losses = [d for d in recent_deals if d["outcome"] == "Lost"]
        
        total_deals = len(recent_deals)
        win_rate = (len(wins) / total_deals * 100) if total_deals > 0 else 0
        
        # Calculate values
        total_won = sum(d.get("deal_value", 0) for d in wins)
        total_lost = sum(d.get("deal_value", 0) for d in losses)
        
        # By competitor breakdown
        by_competitor = {}
        for deal in recent_deals:
            comp_name = deal["competitor_name"]
            if comp_name not in by_competitor:
                by_competitor[comp_name] = {"wins": 0, "losses": 0, "value_won": 0, "value_lost": 0}
            
            if deal["outcome"] == "Won":
                by_competitor[comp_name]["wins"] += 1
                by_competitor[comp_name]["value_won"] += deal.get("deal_value", 0)
            else:
                by_competitor[comp_name]["losses"] += 1
                by_competitor[comp_name]["value_lost"] += deal.get("deal_value", 0)
        
        # Loss reasons
        loss_reasons = {}
        for deal in losses:
            reason = deal.get("loss_reason") or "Unknown"
            loss_reasons[reason] = loss_reasons.get(reason, 0) + 1
        
        # Monthly trend (last 6 months)
        monthly_trend = self._calculate_monthly_trend(recent_deals)
        
        return WinLossStats(
            total_deals=total_deals,
            wins=len(wins),
            losses=len(losses),
            win_rate=round(win_rate, 1),
            total_value_won=total_won,
            total_value_lost=total_lost,
            by_competitor=by_competitor,
            loss_reasons=loss_reasons,
            monthly_trend=monthly_trend
        )
    
    def _calculate_monthly_trend(self, deals: List[Dict]) -> List[Dict[str, Any]]:
        """Calculate monthly win/loss trend."""
        months = {}
        
        for deal in deals:
            date = datetime.fromisoformat(deal["logged_at"])
            month_key = date.strftime("%Y-%m")
            
            if month_key not in months:
                months[month_key] = {"month": month_key, "wins": 0, "losses": 0}
            
            if deal["outcome"] == "Won":
                months[month_key]["wins"] += 1
            else:
                months[month_key]["losses"] += 1
        
        # Sort by month
        return sorted(months.values(), key=lambda x: x["month"])[-6:]
    
    def get_competitor_performance(self, competitor_id: int) -> Dict[str, Any]:
        """
        Get win/loss performance against a specific competitor.
        
        Args:
            competitor_id: Competitor ID
            
        Returns:
            Dict with performance data
        """
        deals = [d for d in self._deals if d["competitor_id"] == competitor_id]
        
        if not deals:
            return {"message": "No deals recorded against this competitor"}
        
        wins = [d for d in deals if d["outcome"] == "Won"]
        losses = [d for d in deals if d["outcome"] == "Lost"]
        
        return {
            "competitor_id": competitor_id,
            "competitor_name": deals[0]["competitor_name"] if deals else "",
            "total_deals": len(deals),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": round(len(wins) / len(deals) * 100, 1) if deals else 0,
            "value_won": sum(d.get("deal_value", 0) for d in wins),
            "value_lost": sum(d.get("deal_value", 0) for d in losses),
            "loss_reasons": self._get_loss_reasons(losses),
            "recent_deals": sorted(deals, key=lambda x: x["logged_at"], reverse=True)[:5]
        }
    
    def _get_loss_reasons(self, losses: List[Dict]) -> Dict[str, int]:
        """Count loss reasons."""
        reasons = {}
        for deal in losses:
            reason = deal.get("loss_reason") or "Unknown"
            reasons[reason] = reasons.get(reason, 0) + 1
        return reasons
    
    def get_most_competitive(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get competitors we face most often.
        
        Args:
            limit: Number of competitors to return
            
        Returns:
            List of competitors sorted by deal count
        """
        competitor_counts = {}
        
        for deal in self._deals:
            comp_name = deal["competitor_name"]
            if comp_name not in competitor_counts:
                competitor_counts[comp_name] = {
                    "name": comp_name,
                    "competitor_id": deal["competitor_id"],
                    "deals": 0,
                    "wins": 0,
                    "losses": 0
                }
            
            competitor_counts[comp_name]["deals"] += 1
            if deal["outcome"] == "Won":
                competitor_counts[comp_name]["wins"] += 1
            else:
                competitor_counts[comp_name]["losses"] += 1
        
        # Sort by total deals
        sorted_comps = sorted(competitor_counts.values(), key=lambda x: x["deals"], reverse=True)
        
        # Calculate win rates
        for comp in sorted_comps:
            comp["win_rate"] = round(comp["wins"] / comp["deals"] * 100, 1) if comp["deals"] > 0 else 0
        
        return sorted_comps[:limit]


# Singleton instance for in-memory storage
_tracker_instance = None

def get_tracker(db_session=None) -> WinLossTracker:
    """Get the win/loss tracker instance."""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = WinLossTracker(db_session)
    elif db_session:
        _tracker_instance.db = db_session
    return _tracker_instance


# API convenience functions
def log_competitive_deal(competitor_id: int, competitor_name: str, deal_name: str,
                        deal_value: float, outcome: str, loss_reason: str = None,
                        notes: str = None) -> Dict[str, Any]:
    """Log a competitive deal."""
    tracker = get_tracker()
    return tracker.log_deal(
        competitor_id=competitor_id,
        competitor_name=competitor_name,
        deal_name=deal_name,
        deal_value=deal_value,
        outcome=outcome,
        loss_reason=loss_reason,
        notes=notes
    )


def get_win_loss_stats(days: int = 365) -> Dict[str, Any]:
    """Get win/loss statistics."""
    tracker = get_tracker()
    stats = tracker.get_stats(days)
    return asdict(stats)


if __name__ == "__main__":
    # Test the tracker
    tracker = WinLossTracker()
    
    # Log some test deals
    tracker.log_deal(1, "Phreesia", "Mercy Health System", 250000, "Won")
    tracker.log_deal(1, "Phreesia", "Cleveland Clinic", 500000, "Lost", "Price")
    tracker.log_deal(2, "Clearwave", "Baptist Health", 150000, "Won")
    tracker.log_deal(3, "athenahealth", "Penn Medicine", 750000, "Lost", "Features")
    tracker.log_deal(1, "Phreesia", "Duke Health", 300000, "Won")
    
    # Get stats
    stats = tracker.get_stats()
    print(f"Total Deals: {stats.total_deals}")
    print(f"Win Rate: {stats.win_rate}%")
    print(f"Value Won: ${stats.total_value_won:,.0f}")
    print(f"Value Lost: ${stats.total_value_lost:,.0f}")
    print(f"\nBy Competitor: {stats.by_competitor}")
    print(f"\nLoss Reasons: {stats.loss_reasons}")
