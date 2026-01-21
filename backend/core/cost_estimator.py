import json
from pathlib import Path
from typing import List, Dict, Optional
import logging
from backend.config.settings import settings

logger = logging.getLogger(__name__)


class CostEstimator:
    """
    Estimates repair costs based on detected damages.
    Uses a database of parts costs and labor estimates.
    """
    
    # Default cost database (if file doesn't exist)
    DEFAULT_COSTS = {
        "dent": {
            "minor": {"parts": 0, "labor_hours": 1.5, "paint": 150},
            "moderate": {"parts": 100, "labor_hours": 3.0, "paint": 300},
            "severe": {"parts": 250, "labor_hours": 5.0, "paint": 500}
        },
        "scratch": {
            "minor": {"parts": 0, "labor_hours": 1.0, "paint": 100},
            "moderate": {"parts": 50, "labor_hours": 2.0, "paint": 250},
            "severe": {"parts": 150, "labor_hours": 4.0, "paint": 400}
        },
        "crack": {
            "minor": {"parts": 75, "labor_hours": 1.0, "paint": 0},
            "moderate": {"parts": 200, "labor_hours": 2.5, "paint": 100},
            "severe": {"parts": 400, "labor_hours": 4.0, "paint": 200}
        },
        "broken_light": {
            "minor": {"parts": 150, "labor_hours": 0.5, "paint": 0},
            "moderate": {"parts": 250, "labor_hours": 1.0, "paint": 0},
            "severe": {"parts": 400, "labor_hours": 1.5, "paint": 0}
        },
        "broken_windshield": {
            "minor": {"parts": 300, "labor_hours": 2.0, "paint": 0},
            "moderate": {"parts": 500, "labor_hours": 3.0, "paint": 0},
            "severe": {"parts": 800, "labor_hours": 4.0, "paint": 0}
        },
        "broken_mirror": {
            "minor": {"parts": 100, "labor_hours": 0.5, "paint": 0},
            "moderate": {"parts": 200, "labor_hours": 1.0, "paint": 50},
            "severe": {"parts": 350, "labor_hours": 1.5, "paint": 100}
        },
        "flat_tire": {
            "minor": {"parts": 150, "labor_hours": 0.5, "paint": 0},
            "moderate": {"parts": 200, "labor_hours": 0.75, "paint": 0},
            "severe": {"parts": 300, "labor_hours": 1.0, "paint": 0}
        },
        "bumper_damage": {
            "minor": {"parts": 100, "labor_hours": 2.0, "paint": 200},
            "moderate": {"parts": 300, "labor_hours": 4.0, "paint": 400},
            "severe": {"parts": 600, "labor_hours": 6.0, "paint": 600}
        }
    }
    
    def __init__(
        self,
        costs_db_path: Optional[str] = None,
        labor_rate: Optional[float] = None,
        markup_percentage: Optional[float] = None
    ):
        """
        Initialize cost estimator.
        
        Args:
            costs_db_path: Path to JSON file with cost database
            labor_rate: Labor rate per hour (USD)
            markup_percentage: Markup percentage for final cost
        """
        self.costs_db_path = costs_db_path or settings.DAMAGE_COSTS_PATH
        self.labor_rate = labor_rate or settings.LABOR_RATE_PER_HOUR
        self.markup_percentage = markup_percentage or settings.MARKUP_PERCENTAGE
        
        # Load costs database
        self.costs_db = self._load_costs_database()
    
    def _load_costs_database(self) -> Dict:
        """
        Load costs database from JSON file.
        Falls back to default costs if file doesn't exist.
        
        Returns:
            Costs database dictionary
        """
        costs_path = Path(self.costs_db_path)
        
        if costs_path.exists():
            try:
                with open(costs_path, 'r') as f:
                    costs_db = json.load(f)
                logger.info(f"Loaded costs database from {costs_path}")
                return costs_db
            except Exception as e:
                logger.error(f"Failed to load costs database: {e}")
        else:
            # Create default costs file
            try:
                costs_path.parent.mkdir(parents=True, exist_ok=True)
                with open(costs_path, 'w') as f:
                    json.dump(self.DEFAULT_COSTS, f, indent=2)
                logger.info(f"Created default costs database at {costs_path}")
            except Exception as e:
                logger.warning(f"Could not create costs file: {e}")
        
        return self.DEFAULT_COSTS
    
    def estimate_damage_cost(
        self,
        damage_type: str,
        severity: str,
        include_paint: bool = True
    ) -> Dict:
        """
        Estimate cost for a single damage.
        
        Args:
            damage_type: Type of damage
            severity: Severity level (minor, moderate, severe)
            include_paint: Whether to include painting costs
            
        Returns:
            Dictionary with cost breakdown
        """
        # Get cost data from database
        cost_data = self.costs_db.get(damage_type, {}).get(severity)
        
        if not cost_data:
            logger.warning(f"No cost data for {damage_type}/{severity}, using defaults")
            cost_data = {"parts": 100, "labor_hours": 2.0, "paint": 100}
        
        # Calculate costs
        parts_cost = cost_data.get("parts", 0)
        labor_hours = cost_data.get("labor_hours", 0)
        labor_cost = labor_hours * self.labor_rate
        paint_cost = cost_data.get("paint", 0) if include_paint else 0
        
        subtotal = parts_cost + labor_cost + paint_cost
        
        return {
            "damage_type": damage_type,
            "severity": severity,
            "parts_cost": parts_cost,
            "labor_hours": labor_hours,
            "labor_cost": labor_cost,
            "paint_cost": paint_cost,
            "subtotal": subtotal
        }
    
    def estimate_total_cost(
        self,
        damages: List[Dict],
        include_paint: bool = True,
        labor_rate_override: Optional[float] = None,
        markup_override: Optional[float] = None
    ) -> Dict:
        """
        Estimate total repair cost for all damages.
        
        Args:
            damages: List of damage dictionaries
            include_paint: Whether to include painting costs
            labor_rate_override: Override default labor rate
            markup_override: Override default markup percentage
            
        Returns:
            Complete cost estimation with breakdown
        """
        # Use overrides if provided
        original_labor_rate = self.labor_rate
        if labor_rate_override:
            self.labor_rate = labor_rate_override
        
        markup_pct = markup_override if markup_override is not None else self.markup_percentage
        
        # Calculate individual damage costs
        damage_items = []
        total_parts = 0
        total_labor = 0
        total_paint = 0
        total_hours = 0
        
        for damage in damages:
            damage_cost = self.estimate_damage_cost(
                damage["damage_type"],
                damage.get("severity", "moderate"),
                include_paint
            )
            
            damage_items.append(damage_cost)
            total_parts += damage_cost["parts_cost"]
            total_labor += damage_cost["labor_cost"]
            total_paint += damage_cost["paint_cost"]
            total_hours += damage_cost["labor_hours"]
        
        # Calculate subtotal and markup
        subtotal = total_parts + total_labor + total_paint
        markup_amount = subtotal * (markup_pct / 100)
        total_cost = subtotal + markup_amount
        
        # Restore original labor rate
        self.labor_rate = original_labor_rate
        
        return {
            "parts_cost": round(total_parts, 2),
            "labor_cost": round(total_labor, 2),
            "paint_cost": round(total_paint, 2),
            "markup": round(markup_amount, 2),
            "total_cost": round(total_cost, 2),
            "estimated_labor_hours": round(total_hours, 2),
            "labor_rate": labor_rate_override or original_labor_rate,
            "markup_percentage": markup_pct,
            "damage_items": damage_items,
            "total_damages": len(damages)
        }
    
    def get_severity_breakdown(self, damages: List[Dict]) -> Dict[str, int]:
        """
        Get count of damages by severity.
        
        Args:
            damages: List of damage dictionaries
            
        Returns:
            Dictionary with severity counts
        """
        breakdown = {"minor": 0, "moderate": 0, "severe": 0}
        
        for damage in damages:
            severity = damage.get("severity", "moderate")
            if severity in breakdown:
                breakdown[severity] += 1
        
        return breakdown
    
    def estimate_repair_time(self, total_hours: float) -> str:
        """
        Estimate repair time in human-readable format.
        
        Args:
            total_hours: Total labor hours
            
        Returns:
            Estimated time string (e.g., "2-3 days")
        """
        if total_hours <= 8:
            return "1 day"
        elif total_hours <= 16:
            return "2-3 days"
        elif total_hours <= 40:
            return "1 week"
        else:
            weeks = int(total_hours / 40) + 1
            return f"{weeks} weeks"