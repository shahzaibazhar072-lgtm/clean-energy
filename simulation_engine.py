import random
import math
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from enum import Enum


class TechType(Enum):
    BATTERY = "Advanced Battery Storage"
    SOLAR = "Next-Gen Solar Panels"
    HYDROGEN = "Green Hydrogen Production"
    CARBON_CAPTURE = "Carbon Capture Technology"


class FundingType(Enum):
    ANGEL = "Angel Investment"
    VC_A = "VC Series A"
    VC_B = "VC Series B"
    GRANT = "Government Grant"
    DEBT = "Debt Financing"


@dataclass
class CompanyMetrics:
    """Stores all company financial and operational metrics"""
    quarter: int = 0
    cash: float = 3_000_000
    revenue: float = 0
    cogs: float = 0
    gross_profit: float = 0
    operating_expenses: float = 0
    net_income: float = 0
    cumulative_production: int = 0
    units_sold: int = 0
    market_share: float = 0
    tech_level: float = 1.0
    unit_cost: float = 300
    valuation: float = 3_000_000
    total_funding_raised: float = 3_000_000
    equity_given: float = 0  # percentage


@dataclass
class Department:
    """Tracks headcount and quarterly costs for a department"""
    name: str
    headcount: int = 0
    salary_per_person: float = 30_000  # quarterly


@dataclass
class Competitor:
    """NPC competitor company"""
    name: str
    tech_level: float = 1.0
    market_share: float = 0.25
    price: float = 450
    is_active: bool = True


@dataclass
class RandomEvent:
    """Random event that affects the simulation"""
    title: str
    description: str
    effect_type: str  # 'positive', 'negative', 'neutral'
    impact: Dict[str, float]


class CleanEnergyStartup:
    """Main simulation engine for the clean energy startup game"""
    
    def __init__(self, tech_type: TechType):
        self.tech_type = tech_type
        self.metrics = CompanyMetrics()
        self.history: List[CompanyMetrics] = []
        
        # Initialize based on technology type
        self._set_tech_parameters()
        
        # Departments
        self.departments = {
            'Engineering': Department('Engineering', headcount=5, salary_per_person=35_000),
            'Sales': Department('Sales', headcount=3, salary_per_person=28_000),
            'Marketing': Department('Marketing', headcount=2, salary_per_person=25_000),
            'Operations': Department('Operations', headcount=4, salary_per_person=27_000)
        }
        
        # Competitors
        self.competitors = [
            Competitor("TechPower Inc", tech_level=1.0, market_share=0.30, price=420),
            Competitor("GreenFuture Corp", tech_level=0.95, market_share=0.25, price=440),
            Competitor("EcoInnovate", tech_level=0.9, market_share=0.20, price=460)
        ]
        
        # Market parameters
        self.base_market_size = self.initial_market_size
        self.market_growth_rate = 0.05  # 5% per quarter
        
        # R&D accumulation
        self.cumulative_rd_spend = 0
        
        # Decision inputs (set by player each quarter)
        self.price = 450
        self.planned_production = 1000
        self.marketing_spend = 50_000
        self.rd_spend = 100_000
        
        # Game state
        self.game_over = False
        self.game_over_reason = ""
        self.last_event: RandomEvent | None = None
        
    def _set_tech_parameters(self):
        """Set initial parameters based on technology choice"""
        tech_params = {
            TechType.BATTERY: {
                'unit_cost': 350,
                'market_size': 8000,
                'price_elasticity': -1.8,
                'rd_effectiveness': 1.2
            },
            TechType.SOLAR: {
                'unit_cost': 280,
                'market_size': 12000,
                'price_elasticity': -2.0,
                'rd_effectiveness': 1.0
            },
            TechType.HYDROGEN: {
                'unit_cost': 420,
                'market_size': 5000,
                'price_elasticity': -1.5,
                'rd_effectiveness': 1.3
            },
            TechType.CARBON_CAPTURE: {
                'unit_cost': 380,
                'market_size': 6000,
                'price_elasticity': -1.6,
                'rd_effectiveness': 1.1
            }
        }
        
        params = tech_params[self.tech_type]
        self.metrics.unit_cost = params['unit_cost']
        self.initial_market_size = params['market_size']
        self.price_elasticity = params['price_elasticity']
        self.rd_effectiveness = params['rd_effectiveness']
        
    def advance_quarter(self, decisions: Dict) -> Dict:
        """
        Advance the simulation by one quarter based on player decisions
        Returns: Dict with quarter results
        """
        # Store decisions
        self.price = decisions.get('price', self.price)
        self.planned_production = decisions.get('production', self.planned_production)
        self.marketing_spend = decisions.get('marketing', self.marketing_spend)
        self.rd_spend = decisions.get('rd', self.rd_spend)
        
        # Increment quarter
        self.metrics.quarter += 1
        
        # Update technology level from R&D
        self._update_technology()
        
        # Update unit cost (learning curve + tech improvement)
        self._update_unit_cost()
        
        # Calculate demand and sales
        demand = self._calculate_demand()
        production = min(self.planned_production, demand)
        self.metrics.units_sold = int(production)
        self.metrics.cumulative_production += self.metrics.units_sold
        
        # Calculate financials
        self.metrics.revenue = self.metrics.units_sold * self.price
        self.metrics.cogs = self.metrics.units_sold * self.metrics.unit_cost
        self.metrics.gross_profit = self.metrics.revenue - self.metrics.cogs
        
        # Operating expenses
        salary_costs = sum(dept.headcount * dept.salary_per_person 
                          for dept in self.departments.values())
        self.metrics.operating_expenses = (salary_costs + 
                                          self.marketing_spend + 
                                          self.rd_spend +
                                          50_000)  # Fixed overhead
        
        self.metrics.net_income = self.metrics.gross_profit - self.metrics.operating_expenses
        self.metrics.cash += self.metrics.net_income
        
        # Update market share
        self._update_market_share()
        
        # Update competitors
        self._update_competitors()
        
        # Calculate valuation
        self._calculate_valuation()
        
        # Random events (20% chance per quarter)
        event_result = None
        if random.random() < 0.20:
            event_result = self._trigger_random_event()
        
        # Check game over conditions
        if self.metrics.cash < -1_000_000:
            self.game_over = True
            self.game_over_reason = "Bankruptcy - Cash balance below -$1M"
        elif self.metrics.quarter >= 12:
            self.game_over = True
            self.game_over_reason = "Game Complete - 12 quarters finished"
        
        # Save history
        self.history.append(self._copy_metrics())
        
        # Prepare results
        results = {
            'quarter': self.metrics.quarter,
            'units_sold': self.metrics.units_sold,
            'revenue': self.metrics.revenue,
            'net_income': self.metrics.net_income,
            'cash': self.metrics.cash,
            'market_share': self.metrics.market_share,
            'tech_level': self.metrics.tech_level,
            'unit_cost': self.metrics.unit_cost,
            'event': event_result
        }
        
        return results
    
    def _update_technology(self):
        """Update technology level based on R&D spend and engineering headcount"""
        self.cumulative_rd_spend += self.rd_spend
        
        # Tech improvement from R&D (diminishing returns)
        rd_factor = math.log(1 + self.cumulative_rd_spend / 100_000) * 0.05 * self.rd_effectiveness
        
        # Tech improvement from engineers
        engineer_factor = self.departments['Engineering'].headcount * 0.01
        
        # Stochastic element
        random_factor = random.uniform(0.98, 1.02)
        
        self.metrics.tech_level = (1.0 + rd_factor + engineer_factor) * random_factor
        
    def _update_unit_cost(self):
        """Update unit cost based on learning curve and technology level"""
        # Learning curve: 20% reduction per doubling of cumulative production
        if self.metrics.cumulative_production > 0:
            learning_factor = math.pow(2, math.log2(self.metrics.cumulative_production / 1000 + 1) * -0.234)
        else:
            learning_factor = 1.0
        
        # Technology improvement reduces cost
        tech_factor = 1.0 / self.metrics.tech_level
        
        # Base cost depends on tech type
        if self.tech_type == TechType.BATTERY:
            base_cost = 350
        elif self.tech_type == TechType.SOLAR:
            base_cost = 280
        elif self.tech_type == TechType.HYDROGEN:
            base_cost = 420
        else:
            base_cost = 380
        
        self.metrics.unit_cost = base_cost * learning_factor * tech_factor
        
    def _calculate_demand(self) -> int:
        """Calculate market demand based on price, marketing, tech, and competition"""
        # Base market size grows each quarter
        current_market = self.base_market_size * math.pow(1 + self.market_growth_rate, 
                                                          self.metrics.quarter)
        
        # Price elasticity effect
        avg_competitor_price = sum(c.price for c in self.competitors if c.is_active) / len([c for c in self.competitors if c.is_active])
        price_ratio = self.price / avg_competitor_price
        price_effect = math.pow(price_ratio, self.price_elasticity)
        
        # Marketing effect (logarithmic)
        marketing_effect = 1.0 + math.log(1 + self.marketing_spend / 10_000) * 0.1
        
        # Technology advantage
        avg_competitor_tech = sum(c.tech_level for c in self.competitors if c.is_active) / len([c for c in self.competitors if c.is_active])
        tech_advantage = self.metrics.tech_level / avg_competitor_tech
        tech_effect = 1.0 + (tech_advantage - 1.0) * 0.5
        
        # Random variation
        random_factor = random.uniform(0.85, 1.15)
        
        # Calculate our share of demand
        total_competitors = len([c for c in self.competitors if c.is_active]) + 1
        our_share = (price_effect * marketing_effect * tech_effect) / total_competitors
        
        demand = int(current_market * our_share * random_factor)
        return max(0, demand)
    
    def _update_market_share(self):
        """Calculate market share relative to competitors"""
        our_sales = self.metrics.units_sold
        total_market_sales = our_sales
        
        # Estimate competitor sales (simplified)
        for comp in self.competitors:
            if comp.is_active:
                estimated_sales = self.base_market_size * comp.market_share * 0.9
                total_market_sales += estimated_sales
        
        if total_market_sales > 0:
            self.metrics.market_share = our_sales / total_market_sales
        else:
            self.metrics.market_share = 0
    
    def _update_competitors(self):
        """Update competitor metrics (simplified AI)"""
        for comp in self.competitors:
            if comp.is_active:
                # Competitors gradually improve tech
                comp.tech_level *= random.uniform(1.01, 1.03)
                
                # Competitors adjust prices slightly
                comp.price *= random.uniform(0.98, 1.02)
                
                # Market share fluctuates
                comp.market_share *= random.uniform(0.95, 1.05)
                comp.market_share = max(0.05, min(0.35, comp.market_share))
    
    def _calculate_valuation(self):
        """Calculate company valuation based on multiple factors"""
        # Revenue multiple method
        revenue_multiple = 3.0 if self.metrics.revenue > 0 else 1.0
        revenue_value = self.metrics.revenue * 4 * revenue_multiple  # Annual revenue * multiple
        
        # Technology premium
        tech_premium = self.metrics.tech_level * 500_000
        
        # Market share premium
        market_premium = self.metrics.market_share * 2_000_000
        
        # Cash on hand
        cash_value = max(0, self.metrics.cash)
        
        self.metrics.valuation = revenue_value + tech_premium + market_premium + cash_value
        self.metrics.valuation = max(self.metrics.total_funding_raised * 0.5, 
                                    self.metrics.valuation)
    
    def _trigger_random_event(self) -> RandomEvent:
        """Trigger a random event"""
        events = [
            RandomEvent(
                "Government Subsidy Approved!",
                "Your technology qualifies for a new government clean energy subsidy program.",
                "positive",
                {"cash": 500_000, "demand_boost": 1.2}
            ),
            RandomEvent(
                "Supply Chain Disruption",
                "Global chip shortage impacts your production capabilities.",
                "negative",
                {"unit_cost_mult": 1.15, "production_limit": 0.7}
            ),
            RandomEvent(
                "Breakthrough in R&D!",
                "Your engineering team achieves a major technological breakthrough.",
                "positive",
                {"tech_boost": 1.2}
            ),
            RandomEvent(
                "Key Engineer Departs",
                "Your lead engineer accepted a position at a competitor.",
                "negative",
                {"tech_level_mult": 0.95, "engineer_loss": 1}
            ),
            RandomEvent(
                "Major Customer Win",
                "Fortune 500 company signs large purchase agreement.",
                "positive",
                {"demand_boost": 1.5, "cash": 300_000}
            ),
            RandomEvent(
                "Regulatory Change",
                "New environmental regulations increase compliance costs.",
                "negative",
                {"operating_cost": 150_000}
            ),
            RandomEvent(
                "New Competitor Enters Market",
                "Well-funded startup announces competing product.",
                "negative",
                {"market_share_mult": 0.85}
            ),
            RandomEvent(
                "Industry Conference Success",
                "Your CEO's keynote generates significant buzz and sales leads.",
                "positive",
                {"marketing_efficiency": 1.3}
            ),
            RandomEvent(
                "Patent Granted",
                "Your core technology patent is approved, providing competitive protection.",
                "positive",
                {"tech_level": 1.15, "valuation_mult": 1.1}
            ),
            RandomEvent(
                "Economic Downturn",
                "Market recession reduces overall demand for clean energy products.",
                "negative",
                {"demand_boost": 0.75}
            ),
            RandomEvent(
                "Strategic Partnership",
                "Major energy company proposes distribution partnership.",
                "positive",
                {"cash": 400_000, "demand_boost": 1.3}
            ),
            RandomEvent(
                "Product Recall",
                "Quality issue requires costly product recall and repairs.",
                "negative",
                {"cash": -600_000, "market_share_mult": 0.8}
            )
        ]
        
        event = random.choice(events)
        self.last_event = event
        
        # Apply event effects
        if "cash" in event.impact:
            self.metrics.cash += event.impact["cash"]
        
        if "tech_boost" in event.impact:
            self.metrics.tech_level *= event.impact["tech_boost"]
        
        if "tech_level_mult" in event.impact:
            self.metrics.tech_level *= event.impact["tech_level_mult"]
        
        if "unit_cost_mult" in event.impact:
            self.metrics.unit_cost *= event.impact["unit_cost_mult"]
        
        if "engineer_loss" in event.impact:
            if self.departments['Engineering'].headcount > 0:
                self.departments['Engineering'].headcount -= 1
        
        if "operating_cost" in event.impact:
            self.metrics.operating_expenses += event.impact["operating_cost"]
        
        if "valuation_mult" in event.impact:
            self.metrics.valuation *= event.impact["valuation_mult"]
        
        return event
    
    def raise_funding(self, funding_type: FundingType) -> Dict:
        """Raise funding from various sources"""
        funding_params = {
            FundingType.ANGEL: {"amount": 500_000, "dilution": 0.08, "debt_cost": 0},
            FundingType.VC_A: {"amount": 3_000_000, "dilution": 0.20, "debt_cost": 0},
            FundingType.VC_B: {"amount": 8_000_000, "dilution": 0.25, "debt_cost": 0},
            FundingType.GRANT: {"amount": 750_000, "dilution": 0, "debt_cost": 0},
            FundingType.DEBT: {"amount": 2_000_000, "dilution": 0, "debt_cost": 0.02}  # 2% quarterly interest
        }
        
        params = funding_params[funding_type]
        
        # Check eligibility (simplified)
        if funding_type == FundingType.VC_B and self.metrics.total_funding_raised < 2_000_000:
            return {"success": False, "message": "Need to raise Series A first"}
        
        if funding_type == FundingType.GRANT and random.random() < 0.4:
            return {"success": False, "message": "Grant application not approved"}
        
        # Apply funding
        self.metrics.cash += params["amount"]
        self.metrics.total_funding_raised += params["amount"]
        self.metrics.equity_given += params["dilution"]
        
        return {
            "success": True,
            "amount": params["amount"],
            "dilution": params["dilution"],
            "message": f"Successfully raised ${params['amount']:,.0f}"
        }
    
    def hire_fire(self, department: str, delta: int) -> Dict:
        """Hire or fire employees in a department"""
        if department not in self.departments:
            return {"success": False, "message": "Invalid department"}
        
        dept = self.departments[department]
        new_headcount = dept.headcount + delta
        
        if new_headcount < 0:
            return {"success": False, "message": "Cannot have negative headcount"}
        
        dept.headcount = new_headcount
        
        action = "Hired" if delta > 0 else "Fired"
        return {
            "success": True,
            "message": f"{action} {abs(delta)} employee(s) in {department}",
            "new_headcount": new_headcount
        }
    
    def _copy_metrics(self) -> CompanyMetrics:
        """Create a copy of current metrics for history"""
        return CompanyMetrics(
            quarter=self.metrics.quarter,
            cash=self.metrics.cash,
            revenue=self.metrics.revenue,
            cogs=self.metrics.cogs,
            gross_profit=self.metrics.gross_profit,
            operating_expenses=self.metrics.operating_expenses,
            net_income=self.metrics.net_income,
            cumulative_production=self.metrics.cumulative_production,
            units_sold=self.metrics.units_sold,
            market_share=self.metrics.market_share,
            tech_level=self.metrics.tech_level,
            unit_cost=self.metrics.unit_cost,
            valuation=self.metrics.valuation,
            total_funding_raised=self.metrics.total_funding_raised,
            equity_given=self.metrics.equity_given
        )
    
    def get_current_state(self) -> Dict:
        """Get all current state information"""
        return {
            'metrics': self.metrics,
            'departments': self.departments,
            'competitors': self.competitors,
            'tech_type': self.tech_type,
            'history': self.history,
            'game_over': self.game_over,
            'game_over_reason': self.game_over_reason,
            'last_event': self.last_event
        }
    