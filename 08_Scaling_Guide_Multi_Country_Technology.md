# SCALING GUIDE: Multi-Country & Multi-Technology Support
## ROI System - From POC to Production

**Version:** 1.0  
**Date:** December 2025  
**Audience:** Engineering Team, Product Owner  

---

## Table of Contents

1. [Scaling Overview](#1-scaling-overview)
2. [Architecture Changes](#2-architecture-changes)
3. [Configuration Strategy](#3-configuration-strategy)
4. [Data Architecture](#4-data-architecture)
5. [Agent Parameterization](#5-agent-parameterization)
6. [Database Schema](#6-database-schema)
7. [Performance Optimization](#7-performance-optimization)
8. [Testing Strategy](#8-testing-strategy)
9. [Deployment Architecture](#9-deployment-architecture)
10. [Phased Rollout Plan](#10-phased-rollout-plan)

---

## 1. Scaling Overview

### 1.1 Current State (POC)

```
1 Country  × 1 Technology = 1 Configuration
    USA    ×  Solar PV     = Hardcoded

Limitations:
- Country hardcoded (USA only)
- Technology hardcoded (Solar PV only)
- Single LCOE calculation model
- Fixed data sources
- No parallelization
```

### 1.2 Target State (Production)

```
100+ Countries × 5 Technologies = 500+ Configurations
   Global      × Solar/Wind/Hydro/Geothermal/Storage

Capabilities:
- Dynamic country selection
- Dynamic technology selection
- Technology-specific calculation models
- Country-specific data sources
- Parallel processing (100+ concurrent)
- Multi-region deployment
```

### 1.3 Scaling Dimensions

| Dimension | POC | MVP | Production | Scaling Factor |
|-----------|-----|-----|------------|----------------|
| **Countries** | 1 (USA) | 25 | 100+ | 100x |
| **Technologies** | 1 (Solar) | 2 (Solar, Wind) | 5 (All) | 5x |
| **Test Sites** | 5 | 100 | 1000+ | 200x |
| **Concurrent Workflows** | 1 | 10 | 100+ | 100x |
| **Data Sources** | 2 | 10 | 50+ | 25x |
| **Analysts** | 0 | 10 | 200+ | ∞ |

**Total Complexity:** 1 → 500 → 50,000+ configurations

---

## 2. Architecture Changes

### 2.1 POC Architecture (Single Country/Tech)

```
┌─────────────────────────────────────┐
│         API (FastAPI)               │
│  POST /opportunities                │
└────────────┬────────────────────────┘
             │
             ↓
┌─────────────────────────────────────┐
│    Workflow Orchestrator            │
│  (Hardcoded: USA + Solar PV)        │
└────────────┬────────────────────────┘
             │
      ┌──────┴──────┐
      ↓             ↓
┌──────────┐  ┌──────────┐
│Research  │  │Analysis  │
│(USA only)│  │(Solar)   │
└──────────┘  └──────────┘
```

**Problems:**
- ❌ Can't add new countries without code changes
- ❌ Can't add new technologies without rewriting agents
- ❌ Single calculation engine
- ❌ No parallelization

### 2.2 Scaled Architecture (Multi-Country/Tech)

```
┌─────────────────────────────────────────────────────┐
│              API Gateway (FastAPI)                  │
│  POST /opportunities?country=X&technology=Y         │
└────────────────────┬────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────┐
│       Configuration Loader (Dynamic)                │
│  - Load country-specific config                     │
│  - Load technology-specific config                  │
│  - Validate compatibility                           │
└────────────────────┬────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────┐
│      Workflow Orchestrator (Parameterized)          │
│  - Country: {country}                               │
│  - Technology: {technology}                         │
│  - Dynamic agent selection                          │
└────────────────────┬────────────────────────────────┘
                     │
          ┌──────────┼──────────┐
          ↓          ↓          ↓
┌──────────────┐ ┌──────────┐ ┌──────────┐
│  Research    │ │ Analysis │ │Technology│
│  Agent       │ │ Agent    │ │ Engine   │
│              │ │          │ │ Factory  │
│ ├─ Policy   │ │ Dispatch │ │          │
│ │  (Country)│ │ to:      │ │ ├─Solar  │
│ └─ Resource │ │          │ │ ├─Wind   │
│   (Tech)    │ │ ├─Solar  │ │ ├─Hydro  │
└──────────────┘ │ ├─Wind   │ │ └─Etc.  │
                 │ └─Tech   │ └──────────┘
                 └──────────┘
```

**Benefits:**
- ✅ Add countries via config (no code change)
- ✅ Add technologies via plugin system
- ✅ Technology-specific calculation engines
- ✅ Parallel processing ready

---

## 3. Configuration Strategy

### 3.1 Configuration Hierarchy

```
config/
├── app_config.yaml              # Global settings
├── countries/
│   ├── _default.yaml           # Default country settings
│   ├── usa.yaml                # USA-specific
│   ├── germany.yaml            # Germany-specific
│   ├── china.yaml              # China-specific
│   └── ...                     # 100+ countries
├── technologies/
│   ├── _default.yaml           # Default tech settings
│   ├── solar_pv.yaml           # Solar PV specifics
│   ├── onshore_wind.yaml       # Wind specifics
│   ├── offshore_wind.yaml
│   ├── hydro.yaml
│   └── geothermal.yaml
└── combinations/
    ├── usa_solar_pv.yaml       # Country+Tech overrides
    └── germany_offshore_wind.yaml
```

### 3.2 Country Configuration Template

**File:** `config/countries/usa.yaml`

```yaml
country:
  code: "USA"
  name: "United States"
  currency: "USD"
  timezone: "America/New_York"
  
  # Policy Data Sources
  policy_sources:
    - name: "irs_itc"
      url: "https://www.irs.gov/credits-deductions/businesses/investment-tax-credit"
      enabled: true
      update_frequency: "monthly"
    
    - name: "state_renewable_portfolio"
      url: "https://www.dsireusa.org"
      enabled: true
      update_frequency: "quarterly"
  
  # Resource Data Sources
  resource_sources:
    - name: "nrel"
      api_url: "https://developer.nrel.gov/api/"
      api_key: "${NREL_API_KEY}"
      enabled: true
    
    - name: "nasa_power"
      api_url: "https://power.larc.nasa.gov/api/"
      enabled: true
  
  # Financial Parameters
  financial:
    discount_rate: 0.08
    corporate_tax_rate: 0.21
    depreciation_method: "MACRS"
    depreciation_years: 5
  
  # Grid Parameters
  grid:
    wholesale_price_usd_per_mwh: 35.0
    capacity_payment_usd_per_kw_year: 50.0
    interconnection_cost_usd_per_kw: 200.0
  
  # Regulatory
  regulatory:
    environmental_permitting_months: 6
    land_lease_usd_per_acre_year: 1000.0
    
  # Supported Technologies
  supported_technologies:
    - solar_pv
    - onshore_wind
    - offshore_wind
    - hydro
    - geothermal
```

**File:** `config/countries/germany.yaml`

```yaml
country:
  code: "DEU"
  name: "Germany"
  currency: "EUR"
  timezone: "Europe/Berlin"
  
  policy_sources:
    - name: "eeg_feed_in_tariff"
      url: "https://www.erneuerbare-energien.de"
      enabled: true
  
  resource_sources:
    - name: "dwd"  # German Weather Service
      api_url: "https://opendata.dwd.de"
      enabled: true
  
  financial:
    discount_rate: 0.06
    corporate_tax_rate: 0.30
    depreciation_method: "Straight-line"
    depreciation_years: 20
  
  grid:
    wholesale_price_eur_per_mwh: 45.0
    
  supported_technologies:
    - solar_pv
    - onshore_wind
    - offshore_wind  # Germany-specific: North Sea, Baltic Sea
```

### 3.3 Technology Configuration Template

**File:** `config/technologies/solar_pv.yaml`

```yaml
technology:
  code: "solar_pv"
  name: "Solar Photovoltaic"
  category: "solar"
  
  # Financial Model
  financial:
    capex_usd_per_kw: 1200.0
    opex_usd_per_kw_year: 15.0
    project_lifetime_years: 25
    capacity_factor_range: [0.10, 0.30]  # 10-30%
    degradation_rate_per_year: 0.005  # 0.5%/year
  
  # Technical Parameters
  technical:
    panel_efficiency: 0.20  # 20%
    inverter_efficiency: 0.98
    system_losses: 0.14  # 14%
    
  # Resource Requirements
  resource_requirements:
    - name: "GHI"
      unit: "kWh/m2/day"
      minimum: 3.0
      optimal: 5.5
      data_source: "nasa_power"
    
    - name: "temperature"
      unit: "celsius"
      optimal_range: [15, 25]
      data_source: "nasa_power"
  
  # LCOE Calculation
  lcoe_formula: "capex_annualized + opex_annual / annual_energy_production"
  
  # Validation Ranges
  validation:
    lcoe_usd_per_mwh: [20, 80]
    irr_percent: [5, 25]
    capacity_factor: [0.10, 0.30]
  
  # LLM Prompt Template
  prompt_template: "config/prompts/solar_pv_analysis.md"
```

**File:** `config/technologies/onshore_wind.yaml`

```yaml
technology:
  code: "onshore_wind"
  name: "Onshore Wind"
  category: "wind"
  
  financial:
    capex_usd_per_kw: 1500.0
    opex_usd_per_kw_year: 40.0
    project_lifetime_years: 25
    capacity_factor_range: [0.25, 0.45]
  
  technical:
    turbine_efficiency: 0.45
    availability: 0.95
    
  resource_requirements:
    - name: "wind_speed"
      unit: "m/s"
      minimum: 6.0
      optimal: 8.0
      data_source: "global_wind_atlas"
    
    - name: "wind_power_density"
      unit: "W/m2"
      minimum: 300
      data_source: "global_wind_atlas"
  
  validation:
    lcoe_usd_per_mwh: [30, 90]
    irr_percent: [5, 20]
    capacity_factor: [0.25, 0.45]
  
  prompt_template: "config/prompts/onshore_wind_analysis.md"
```

### 3.4 Dynamic Configuration Loading

```python
# src/utils/config_loader.py

import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigLoader:
    """
    Dynamic configuration loader for multi-country/tech support
    """
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self._cache = {}
    
    def load_country_config(self, country_code: str) -> Dict[str, Any]:
        """Load country-specific configuration"""
        
        # Check cache
        cache_key = f"country_{country_code}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Load default
        default_config = self._load_yaml("countries/_default.yaml")
        
        # Load country-specific
        country_file = f"countries/{country_code.lower()}.yaml"
        country_config = self._load_yaml(country_file, default={})
        
        # Merge (country overrides default)
        merged = self._deep_merge(default_config, country_config)
        
        # Cache and return
        self._cache[cache_key] = merged
        return merged
    
    def load_technology_config(self, tech_code: str) -> Dict[str, Any]:
        """Load technology-specific configuration"""
        
        cache_key = f"tech_{tech_code}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        default_config = self._load_yaml("technologies/_default.yaml")
        tech_file = f"technologies/{tech_code.lower()}.yaml"
        tech_config = self._load_yaml(tech_file, default={})
        
        merged = self._deep_merge(default_config, tech_config)
        self._cache[cache_key] = merged
        return merged
    
    def load_combination_config(
        self, 
        country_code: str, 
        tech_code: str
    ) -> Dict[str, Any]:
        """
        Load combined country+technology configuration
        with override support
        """
        
        # Load base configs
        country_config = self.load_country_config(country_code)
        tech_config = self.load_technology_config(tech_code)
        
        # Check for combination-specific overrides
        combo_file = f"combinations/{country_code.lower()}_{tech_code.lower()}.yaml"
        combo_config = self._load_yaml(combo_file, default={})
        
        # Merge: default → country → tech → combination
        merged = self._deep_merge(country_config, tech_config)
        merged = self._deep_merge(merged, combo_config)
        
        # Validate compatibility
        self._validate_compatibility(merged, country_code, tech_code)
        
        return merged
    
    def get_supported_countries(self) -> list:
        """Get list of all supported countries"""
        countries_dir = self.config_dir / "countries"
        return [
            f.stem for f in countries_dir.glob("*.yaml")
            if f.stem != "_default"
        ]
    
    def get_supported_technologies(self, country_code: Optional[str] = None) -> list:
        """Get list of supported technologies (optionally filtered by country)"""
        if country_code:
            country_config = self.load_country_config(country_code)
            return country_config.get("country", {}).get("supported_technologies", [])
        
        tech_dir = self.config_dir / "technologies"
        return [
            f.stem for f in tech_dir.glob("*.yaml")
            if f.stem != "_default"
        ]
    
    def _load_yaml(self, relative_path: str, default: Dict = None) -> Dict:
        """Load YAML file with error handling"""
        file_path = self.config_dir / relative_path
        
        if not file_path.exists():
            if default is not None:
                return default
            raise FileNotFoundError(f"Config file not found: {file_path}")
        
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _validate_compatibility(
        self, 
        config: Dict, 
        country_code: str, 
        tech_code: str
    ):
        """Validate that country supports this technology"""
        supported = config.get("country", {}).get("supported_technologies", [])
        
        if tech_code not in supported:
            raise ValueError(
                f"Technology '{tech_code}' not supported in country '{country_code}'. "
                f"Supported: {supported}"
            )


# Usage Example
config_loader = ConfigLoader()

# Load for USA + Solar PV
usa_solar_config = config_loader.load_combination_config("USA", "solar_pv")

# Load for Germany + Offshore Wind
germany_wind_config = config_loader.load_combination_config("DEU", "offshore_wind")

# Get all supported countries
countries = config_loader.get_supported_countries()
# ['usa', 'germany', 'china', 'india', ...]

# Get technologies supported in Germany
de_techs = config_loader.get_supported_technologies("DEU")
# ['solar_pv', 'onshore_wind', 'offshore_wind']
```

---

## 4. Data Architecture

### 4.1 Data Source Registry

**File:** `src/data_sources/source_registry.py`

```python
from typing import Dict, List, Type
from src.core.interfaces.data_source_interface import IDataSource

class DataSourceRegistry:
    """
    Registry for country/technology-specific data sources
    Implements Factory + Registry patterns
    """
    
    _sources: Dict[str, Dict[str, Type[IDataSource]]] = {
        # Country-specific sources
        "USA": {
            "policy": "IRSITCSource",
            "resource_solar": "NRELSource",
            "resource_wind": "NRELWindSource",
        },
        "DEU": {
            "policy": "EEGFeedInTariffSource",
            "resource_solar": "DWDSolarSource",
            "resource_wind": "DWDWindSource",
        },
        "CHN": {
            "policy": "NDRCPolicySource",
            "resource_solar": "CMASource",  # China Meteorological Admin
            "resource_wind": "CMAWindSource",
        },
        # ... 100+ countries
        
        # Global fallbacks
        "_global": {
            "resource_solar": "NASAPowerSource",
            "resource_wind": "GlobalWindAtlasSource",
            "policy": "WorldBankPolicySource",
        }
    }
    
    @classmethod
    def get_source(
        cls, 
        country_code: str, 
        source_type: str,
        technology: str
    ) -> IDataSource:
        """
        Get appropriate data source for country + technology
        """
        # Try country-specific first
        country_sources = cls._sources.get(country_code, {})
        source_key = f"{source_type}_{technology}"
        
        if source_key in country_sources:
            source_class = country_sources[source_key]
            return cls._instantiate(source_class)
        
        # Fall back to generic source_type
        if source_type in country_sources:
            source_class = country_sources[source_type]
            return cls._instantiate(source_class)
        
        # Fall back to global
        global_sources = cls._sources.get("_global", {})
        if source_key in global_sources:
            return cls._instantiate(global_sources[source_key])
        
        if source_type in global_sources:
            return cls._instantiate(global_sources[source_type])
        
        raise ValueError(
            f"No data source found for {country_code}/{source_type}/{technology}"
        )
    
    @classmethod
    def register_source(
        cls,
        country_code: str,
        source_type: str,
        source_class: Type[IDataSource]
    ):
        """Register a new data source"""
        if country_code not in cls._sources:
            cls._sources[country_code] = {}
        
        cls._sources[country_code][source_type] = source_class
    
    @classmethod
    def _instantiate(cls, source_class_name: str) -> IDataSource:
        """Dynamically instantiate data source class"""
        # Import and instantiate the class
        # Implementation depends on your module structure
        pass
```

### 4.2 Multi-Country Data Partitioning

**Database Partitioning Strategy:**

```sql
-- Partition opportunities table by country
CREATE TABLE opportunities (
    id UUID PRIMARY KEY,
    opportunity_id VARCHAR(255) UNIQUE,
    country VARCHAR(3) NOT NULL,  -- ISO 3166-1 alpha-3
    technology VARCHAR(50) NOT NULL,
    latitude DECIMAL(10, 6),
    longitude DECIMAL(11, 6),
    status VARCHAR(50),
    created_at TIMESTAMP,
    metadata JSONB
) PARTITION BY LIST (country);

-- Create partitions per country (or region)
CREATE TABLE opportunities_usa PARTITION OF opportunities
    FOR VALUES IN ('USA');

CREATE TABLE opportunities_eu PARTITION OF opportunities
    FOR VALUES IN ('DEU', 'FRA', 'ESP', 'ITA', 'GBR', ...);

CREATE TABLE opportunities_asia PARTITION OF opportunities
    FOR VALUES IN ('CHN', 'IND', 'JPN', 'KOR', ...);

-- Indexes on partitions
CREATE INDEX idx_opps_usa_tech ON opportunities_usa(technology);
CREATE INDEX idx_opps_usa_status ON opportunities_usa(status);
```

---

## 5. Agent Parameterization

### 5.1 Parameterized Research Agent

**Before (POC):**
```python
class ResearchAgent(BaseAgent):
    """Hardcoded for USA + Solar PV"""
    
    async def _execute_core(self, input_data):
        # Hardcoded USA policy scraper
        policy_data = await self.fetch_usa_itc()
        
        # Hardcoded solar resource data
        resource_data = await self.fetch_nrel_solar()
        
        return {"policy": policy_data, "resource": resource_data}
```

**After (Scaled):**
```python
class ResearchAgent(BaseAgent):
    """Parameterized for any country + technology"""
    
    def __init__(self, llm_provider, config, logger=None):
        super().__init__("ResearchAgent", llm_provider, config, logger)
        
        # Dynamic initialization
        self.country_code = config.get("country_code")
        self.technology = config.get("technology")
        self.config_loader = ConfigLoader()
        
        # Load country+tech specific config
        self.runtime_config = self.config_loader.load_combination_config(
            self.country_code,
            self.technology
        )
        
        # Initialize appropriate data sources
        self.policy_source = DataSourceRegistry.get_source(
            self.country_code,
            "policy",
            self.technology
        )
        
        self.resource_source = DataSourceRegistry.get_source(
            self.country_code,
            f"resource_{self.technology.split('_')[0]}",  # solar, wind, etc.
            self.technology
        )
    
    async def _execute_core(self, input_data):
        """Execute with parameterized sources"""
        
        # Fetch policy data (country-specific source)
        policy_params = {
            "country": self.country_code,
            "technology": self.technology,
            **input_data
        }
        policy_data = await self.policy_source.fetch(policy_params)
        
        # Fetch resource data (country+tech specific source)
        resource_params = {
            "latitude": input_data["latitude"],
            "longitude": input_data["longitude"],
            "technology": self.technology,
            **self.runtime_config.get("resource_requirements", {})
        }
        resource_data = await self.resource_source.fetch(resource_params)
        
        # Normalize using LLM (with country/tech context)
        normalized = await self._normalize_with_llm(
            policy_data,
            resource_data,
            self.runtime_config
        )
        
        return normalized
    
    async def _normalize_with_llm(self, policy_data, resource_data, config):
        """Normalize data using country/tech-aware prompt"""
        
        prompt = f"""
Normalize renewable energy data for:
Country: {config['country']['name']}
Technology: {config['technology']['name']}

Policy Data:
{json.dumps(policy_data, indent=2)}

Resource Data:
{json.dumps(resource_data, indent=2)}

Output JSON with keys: policy_data, resource_data, data_completeness
Follow schema for {self.technology} in {self.country_code}.
"""
        
        response = await self.llm_provider.generate(prompt)
        return json.loads(response)
```

### 5.2 Technology-Specific Calculation Engines

**File:** `src/services/calculation_engines.py`

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class ICalculationEngine(ABC):
    """Interface for technology-specific LCOE/IRR calculators"""
    
    @abstractmethod
    def calculate_lcoe(self, params: Dict[str, Any]) -> float:
        """Calculate Levelized Cost of Energy"""
        pass
    
    @abstractmethod
    def calculate_irr(self, params: Dict[str, Any]) -> float:
        """Calculate Internal Rate of Return"""
        pass
    
    @abstractmethod
    def calculate_capacity_factor(self, resource_data: Dict) -> float:
        """Calculate expected capacity factor"""
        pass


class SolarPVCalculator(ICalculationEngine):
    """Solar PV specific calculations"""
    
    def calculate_lcoe(self, params):
        capex = params['capex_usd_per_kw']
        opex = params['opex_usd_per_kw_year']
        capacity_factor = params['capacity_factor']
        lifetime = params['project_lifetime_years']
        discount_rate = params['discount_rate']
        
        # Annual energy (kWh/kW/year)
        annual_energy = 8760 * capacity_factor
        
        # Present value of costs
        pv_capex = capex
        pv_opex = opex * ((1 - (1 + discount_rate)**-lifetime) / discount_rate)
        
        # Present value of energy
        pv_energy = annual_energy * ((1 - (1 + discount_rate)**-lifetime) / discount_rate)
        
        # LCOE ($/MWh)
        lcoe = ((pv_capex + pv_opex) / pv_energy) * 1000
        
        return lcoe
    
    def calculate_capacity_factor(self, resource_data):
        """Solar-specific capacity factor calculation"""
        ghi = resource_data['avg_ghi_kwh_m2_day']
        temperature = resource_data.get('avg_temperature_c', 25)
        
        # Base capacity factor from GHI
        base_cf = (ghi * 365) / 8760
        
        # Temperature derating (panels less efficient in heat)
        temp_factor = 1 - 0.004 * max(0, temperature - 25)
        
        # System losses (soiling, inverter, wiring, etc.)
        system_losses = 0.14
        
        # Final capacity factor
        cf = base_cf * temp_factor * (1 - system_losses)
        
        return min(max(cf, 0.10), 0.30)  # Clamp to realistic range


class OnshoreWindCalculator(ICalculationEngine):
    """Onshore wind specific calculations"""
    
    def calculate_lcoe(self, params):
        # Wind-specific LCOE formula
        capex = params['capex_usd_per_kw']
        opex = params['opex_usd_per_kw_year']
        capacity_factor = params['capacity_factor']
        lifetime = params['project_lifetime_years']
        discount_rate = params['discount_rate']
        
        annual_energy = 8760 * capacity_factor
        
        pv_capex = capex
        pv_opex = opex * ((1 - (1 + discount_rate)**-lifetime) / discount_rate)
        pv_energy = annual_energy * ((1 - (1 + discount_rate)**-lifetime) / discount_rate)
        
        lcoe = ((pv_capex + pv_opex) / pv_energy) * 1000
        
        return lcoe
    
    def calculate_capacity_factor(self, resource_data):
        """Wind-specific capacity factor calculation using Weibull distribution"""
        avg_wind_speed = resource_data['avg_wind_speed_m_s']
        wind_power_density = resource_data.get('wind_power_density_w_m2', 400)
        
        # Simplified capacity factor from wind speed
        # (Real implementation would use Weibull distribution)
        if avg_wind_speed < 6:
            cf = 0.20
        elif avg_wind_speed < 7:
            cf = 0.30
        elif avg_wind_speed < 8:
            cf = 0.38
        else:
            cf = 0.45
        
        # Adjust for wind power density
        if wind_power_density < 300:
            cf *= 0.9
        elif wind_power_density > 500:
            cf *= 1.1
        
        return min(max(cf, 0.25), 0.50)


class CalculationEngineFactory:
    """Factory for creating technology-specific calculation engines"""
    
    _engines = {
        "solar_pv": SolarPVCalculator,
        "onshore_wind": OnshoreWindCalculator,
        "offshore_wind": "OffshoreWindCalculator",
        "hydro": "HydroCalculator",
        "geothermal": "GeothermalCalculator",
    }
    
    @classmethod
    def get_engine(cls, technology: str) -> ICalculationEngine:
        """Get calculation engine for technology"""
        engine_class = cls._engines.get(technology)
        
        if not engine_class:
            raise ValueError(f"No calculation engine for technology: {technology}")
        
        return engine_class()
```

### 5.3 Parameterized Analysis Agent

```python
class AnalysisAgent(BaseAgent):
    """Technology-agnostic analysis agent"""
    
    def __init__(self, llm_provider, config, logger=None):
        super().__init__("AnalysisAgent", llm_provider, config, logger)
        
        self.country_code = config.get("country_code")
        self.technology = config.get("technology")
        
        # Load config
        self.config_loader = ConfigLoader()
        self.runtime_config = self.config_loader.load_combination_config(
            self.country_code,
            self.technology
        )
        
        # Get appropriate calculation engine
        self.calc_engine = CalculationEngineFactory.get_engine(self.technology)
    
    async def _execute_core(self, input_data):
        research_data = input_data['research_data']
        
        # Extract resource data
        resource_data = research_data['resource_data']
        
        # Calculate capacity factor (technology-specific)
        capacity_factor = self.calc_engine.calculate_capacity_factor(resource_data)
        
        # Get financial parameters (country-specific)
        financial_params = {
            'capex_usd_per_kw': self.runtime_config['technology']['financial']['capex_usd_per_kw'],
            'opex_usd_per_kw_year': self.runtime_config['technology']['financial']['opex_usd_per_kw_year'],
            'project_lifetime_years': self.runtime_config['technology']['financial']['project_lifetime_years'],
            'discount_rate': self.runtime_config['country']['financial']['discount_rate'],
            'capacity_factor': capacity_factor,
        }
        
        # Calculate LCOE (technology-specific formula)
        lcoe = self.calc_engine.calculate_lcoe(financial_params)
        
        # Calculate IRR (technology-specific)
        irr = self.calc_engine.calculate_irr({
            **financial_params,
            'electricity_price': self.runtime_config['country']['grid']['wholesale_price_usd_per_mwh'],
            'capacity_payment': self.runtime_config['country']['grid'].get('capacity_payment_usd_per_kw_year', 0),
        })
        
        # Validate against technology-specific ranges
        self._validate_results(lcoe, irr)
        
        return {
            "lcoe_usd_per_mwh": lcoe,
            "irr_percent": irr,
            "capacity_factor": capacity_factor,
            "assumptions": financial_params,
            "confidence": "high"
        }
    
    def _validate_results(self, lcoe, irr):
        """Validate against technology-specific ranges"""
        lcoe_range = self.runtime_config['technology']['validation']['lcoe_usd_per_mwh']
        irr_range = self.runtime_config['technology']['validation']['irr_percent']
        
        if not (lcoe_range[0] <= lcoe <= lcoe_range[1]):
            self.logger.warning(
                f"LCOE {lcoe} outside expected range {lcoe_range} "
                f"for {self.technology} in {self.country_code}"
            )
        
        if not (irr_range[0] <= irr <= irr_range[1]):
            self.logger.warning(
                f"IRR {irr} outside expected range {irr_range}"
            )
```

---

## 6. Database Schema

### 6.1 Scaled Schema

```sql
-- Opportunities (partitioned by country)
CREATE TABLE opportunities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    opportunity_id VARCHAR(255) UNIQUE NOT NULL,
    
    -- Multi-country/tech support
    country VARCHAR(3) NOT NULL,  -- ISO 3166-1 alpha-3
    technology VARCHAR(50) NOT NULL,
    
    -- Location
    latitude DECIMAL(10, 6) NOT NULL,
    longitude DECIMAL(11, 6) NOT NULL,
    region VARCHAR(100),  -- State/province
    
    -- Status tracking
    status VARCHAR(50) NOT NULL DEFAULT 'INITIALIZED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Metrics
    duration_seconds DECIMAL(10, 2),
    cost_usd DECIMAL(10, 2),
    
    -- Flexible metadata
    metadata JSONB,
    
    -- Constraints
    CONSTRAINT valid_country CHECK (length(country) = 3),
    CONSTRAINT valid_technology CHECK (technology IN (
        'solar_pv', 'onshore_wind', 'offshore_wind', 'hydro', 'geothermal'
    ))
) PARTITION BY LIST (country);

-- Create partitions (example for major countries)
CREATE TABLE opportunities_usa PARTITION OF opportunities FOR VALUES IN ('USA');
CREATE TABLE opportunities_chn PARTITION OF opportunities FOR VALUES IN ('CHN');
CREATE TABLE opportunities_ind PARTITION OF opportunities FOR VALUES IN ('IND');
-- ... etc

-- Indexes on partitions
CREATE INDEX idx_opps_usa_tech_status ON opportunities_usa(technology, status);
CREATE INDEX idx_opps_usa_created ON opportunities_usa(created_at DESC);

-- Reports (partitioned by country+technology)
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    opportunity_id VARCHAR(255) REFERENCES opportunities(opportunity_id),
    
    country VARCHAR(3) NOT NULL,
    technology VARCHAR(50) NOT NULL,
    
    version VARCHAR(20) NOT NULL DEFAULT '1.0',
    report_type VARCHAR(50) NOT NULL,
    report_data JSONB NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) PARTITION BY LIST (country);

-- Configuration cache table
CREATE TABLE config_cache (
    cache_key VARCHAR(255) PRIMARY KEY,
    country VARCHAR(3),
    technology VARCHAR(50),
    config_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    
    INDEX idx_config_country_tech (country, technology)
);
```

### 6.2 Query Patterns

```sql
-- Get all opportunities for a country+technology
SELECT * FROM opportunities
WHERE country = 'USA' AND technology = 'solar_pv'
ORDER BY created_at DESC
LIMIT 100;

-- Aggregate statistics by country
SELECT 
    country,
    technology,
    COUNT(*) as total_opportunities,
    AVG(cost_usd) as avg_cost,
    AVG(duration_seconds) as avg_duration
FROM opportunities
WHERE status = 'COMPLETED'
GROUP BY country, technology
ORDER BY total_opportunities DESC;

-- Technology distribution per country
SELECT 
    country,
    technology,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY country), 2) as percentage
FROM opportunities
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY country, technology
ORDER BY country, count DESC;
```

---

## 7. Performance Optimization

### 7.1 Parallel Processing

```python
# src/orchestration/parallel_workflow.py

import asyncio
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor

class ParallelWorkflowOrchestrator:
    """Process multiple opportunities in parallel"""
    
    def __init__(self, max_concurrent: int = 100):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_batch(
        self,
        opportunities: List[Dict]
    ) -> List[Dict]:
        """Process a batch of opportunities in parallel"""
        
        # Create tasks
        tasks = [
            self._process_single_with_limit(opp)
            for opp in opportunities
        ]
        
        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        success = [r for r in results if not isinstance(r, Exception)]
        failures = [r for r in results if isinstance(r, Exception)]
        
        self.logger.info(
            f"Batch complete: {len(success)} success, {len(failures)} failures"
        )
        
        return results
    
    async def _process_single_with_limit(self, opportunity: Dict):
        """Process single opportunity with concurrency limit"""
        async with self.semaphore:
            return await self._process_single(opportunity)
    
    async def _process_single(self, opportunity: Dict):
        """Process single opportunity"""
        # Load appropriate config
        config = ConfigLoader().load_combination_config(
            opportunity['country'],
            opportunity['technology']
        )
        
        # Create agents with loaded config
        research_agent = AgentFactory.create_agent(
            "research",
            llm_provider,
            {**config, **opportunity}
        )
        
        # Execute workflow
        # ...
        
        return result


# Usage
orchestrator = ParallelWorkflowOrchestrator(max_concurrent=100)

# Process 500 opportunities across 50 countries × 5 technologies
opportunities = [
    {"country": "USA", "technology": "solar_pv", "latitude": 31.99, "longitude": -102.07},
    {"country": "DEU", "technology": "offshore_wind", "latitude": 54.0, "longitude": 7.0},
    # ... 498 more
]

results = await orchestrator.process_batch(opportunities)
```

### 7.2 Caching Strategy

```python
# src/utils/cache_manager.py

import redis
import json
from typing import Optional, Any
from datetime import timedelta

class MultiLevelCacheManager:
    """
    Multi-level caching for country/technology configurations and data
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def get_country_config(self, country_code: str) -> Optional[Dict]:
        """Get cached country config"""
        cache_key = f"config:country:{country_code}"
        cached = self.redis.get(cache_key)
        
        if cached:
            return json.loads(cached)
        
        return None
    
    def set_country_config(self, country_code: str, config: Dict, ttl: int = 86400):
        """Cache country config (24 hour TTL)"""
        cache_key = f"config:country:{country_code}"
        self.redis.setex(
            cache_key,
            ttl,
            json.dumps(config)
        )
    
    def get_resource_data(
        self,
        country: str,
        technology: str,
        lat: float,
        lon: float
    ) -> Optional[Dict]:
        """Get cached resource data"""
        # Cache key includes location rounded to 2 decimals
        cache_key = f"resource:{country}:{technology}:{lat:.2f}:{lon:.2f}"
        cached = self.redis.get(cache_key)
        
        if cached:
            return json.loads(cached)
        
        return None
    
    def set_resource_data(
        self,
        country: str,
        technology: str,
        lat: float,
        lon: float,
        data: Dict,
        ttl: int = 2592000  # 30 days
    ):
        """Cache resource data (long TTL for static resource data)"""
        cache_key = f"resource:{country}:{technology}:{lat:.2f}:{lon:.2f}"
        self.redis.setex(cache_key, ttl, json.dumps(data))
```

---

## 8. Testing Strategy

### 8.1 Parameterized Tests

```python
# tests/test_multi_country_tech.py

import pytest

# Test matrix: countries × technologies
TEST_MATRIX = [
    ("USA", "solar_pv"),
    ("USA", "onshore_wind"),
    ("DEU", "solar_pv"),
    ("DEU", "offshore_wind"),
    ("CHN", "solar_pv"),
    ("CHN", "hydro"),
    ("IND", "solar_pv"),
    ("IND", "onshore_wind"),
    # ... 500 combinations for full coverage
]

@pytest.mark.parametrize("country,technology", TEST_MATRIX)
async def test_end_to_end_workflow(country, technology):
    """Test workflow for each country+technology combination"""
    
    # Load config
    config = ConfigLoader().load_combination_config(country, technology)
    
    # Create test opportunity
    opportunity = {
        "country": country,
        "technology": technology,
        "latitude": config['test_site']['latitude'],
        "longitude": config['test_site']['longitude'],
    }
    
    # Execute workflow
    result = await orchestrator.execute_opportunity_analysis(opportunity)
    
    # Validate results
    assert result["status"] == "COMPLETED"
    
    # Check LCOE in expected range
    lcoe = result["analysis_data"]["lcoe_usd_per_mwh"]
    lcoe_range = config['technology']['validation']['lcoe_usd_per_mwh']
    assert lcoe_range[0] <= lcoe <= lcoe_range[1], \
        f"LCOE {lcoe} outside range {lcoe_range} for {country}/{technology}"


@pytest.mark.parametrize("country", ["USA", "DEU", "CHN", "IND"])
def test_config_loading(country):
    """Test config loading for each country"""
    config = ConfigLoader().load_country_config(country)
    
    assert "country" in config
    assert config["country"]["code"] == country
    assert "supported_technologies" in config["country"]


@pytest.mark.parametrize("technology", ["solar_pv", "onshore_wind", "offshore_wind"])
def test_calculation_engines(technology):
    """Test calculation engines for each technology"""
    engine = CalculationEngineFactory.get_engine(technology)
    
    # Test LCOE calculation
    test_params = {
        "capex_usd_per_kw": 1200,
        "opex_usd_per_kw_year": 15,
        "capacity_factor": 0.25,
        "project_lifetime_years": 25,
        "discount_rate": 0.08,
    }
    
    lcoe = engine.calculate_lcoe(test_params)
    assert 0 < lcoe < 500, f"LCOE {lcoe} unrealistic for {technology}"
```

---

## 9. Deployment Architecture

### 9.1 Multi-Region Deployment

```
┌────────────────────────────────────────────────────────────┐
│                   Global Load Balancer                      │
│              (CloudFlare / AWS Global Accelerator)          │
└────────┬──────────────────────┬────────────────────────────┘
         │                      │                      
         ↓                      ↓                      
┌─────────────────┐    ┌─────────────────┐    
│   US Region     │    │   EU Region     │    
│                 │    │                 │    
│ ┌─────────────┐ │    │ ┌─────────────┐ │    
│ │   API       │ │    │ │   API       │ │    
│ │  (FastAPI)  │ │    │ │  (FastAPI)  │ │    
│ └──────┬──────┘ │    │ └──────┬──────┘ │    
│        │        │    │        │        │    
│ ┌──────┴──────┐ │    │ ┌──────┴──────┐ │    
│ │ PostgreSQL  │ │    │ │ PostgreSQL  │ │    
│ │ (USA data)  │ │    │ │ (EU data)   │ │    
│ └─────────────┘ │    │ └─────────────┘ │    
│                 │    │                 │    
│ ┌─────────────┐ │    │ ┌─────────────┐ │    
│ │  ChromaDB   │ │    │ │  ChromaDB   │ │    
│ └─────────────┘ │    │ └─────────────┘ │    
└─────────────────┘    └─────────────────┘    

         ↓                      ↓
┌─────────────────────────────────────────────┐
│     Shared Configuration (S3 / GCS)         │
│  - Country configs                          │
│  - Technology configs                       │
│  - Synced across regions                    │
└─────────────────────────────────────────────┘
```

**Routing Logic:**
- US requests → US region
- EU requests → EU region
- Asia requests → Nearest region
- Data residency compliance

---

## 10. Phased Rollout Plan

### Phase 1: POC (Current) - 1 Country, 1 Tech
- ✅ USA + Solar PV
- ✅ 5 test sites
- ✅ Validate feasibility

### Phase 2: MVP (Q2 2026) - 25 Countries, 2 Technologies
**Countries (25):**
- North America: USA, Canada, Mexico
- Europe: Germany, France, Spain, Italy, UK, Netherlands, Poland, Greece
- Asia: China, India, Japan, South Korea, Vietnam, Thailand
- Middle East: UAE, Saudi Arabia, Israel
- Latin America: Brazil, Chile, Argentina
- Africa: South Africa, Egypt, Morocco
- Oceania: Australia

**Technologies (2):**
- Solar PV
- Onshore Wind

**Implementation:**
- Week 1-2: Refactor for parameterization
- Week 3-4: Add config files for 25 countries
- Week 5-6: Add onshore wind calculation engine
- Week 7-8: Testing (25 × 2 = 50 combinations)

### Phase 3: Scale (Q4 2026) - 75 Countries, 4 Technologies
**Additional Countries (50):**
- All G20 nations
- Top 50 by renewable potential

**Additional Technologies (2):**
- Offshore Wind
- Hydro (run-of-river, reservoir)

**Implementation:**
- Month 1: Add 50 country configs
- Month 2: Add offshore wind + hydro engines
- Month 3: Testing (75 × 4 = 300 combinations)

### Phase 4: Enterprise (Year 2) - 100+ Countries, 5 Technologies
**Full Global Coverage:**
- All UN member states (193)
- Focus on top 100 by renewable potential

**Complete Technology Portfolio:**
- Solar PV, Onshore Wind, Offshore Wind, Hydro, **Geothermal**
- Energy Storage (batteries, pumped hydro)

---

## 11. Migration Path

### 11.1 From POC to Scaled Architecture

**Step 1: Abstract Configuration (Week 1)**
```bash
# Move hardcoded values to config files
git checkout -b feature/config-abstraction

# Create config structure
mkdir -p config/countries config/technologies

# Extract USA config
# Extract Solar PV config

# Refactor agents to use ConfigLoader
```

**Step 2: Parameterize Agents (Week 2)**
```python
# Refactor agents to accept country/tech parameters
# Replace hardcoded data sources with registry
# Add dynamic calculation engine selection
```

**Step 3: Add Second Country (Week 3)**
```bash
# Add Germany config
# Test USA vs Germany comparison
# Fix country-specific issues
```

**Step 4: Add Second Technology (Week 4)**
```python
# Add onshore wind calculation engine
# Test solar vs wind comparison
# Fix technology-specific issues
```

**Step 5: Scale Testing (Week 5-6)**
```bash
# Add parameterized tests
# Test 25 countries × 2 technologies = 50 combinations
# Fix any compatibility issues
```

---

## 12. Key Takeaways

### ✅ **DO:**
1. **Externalize all configuration** - No hardcoding
2. **Use Factory pattern** for data sources and calculation engines
3. **Partition database** by country for performance
4. **Cache aggressively** - Configs and resource data rarely change
5. **Test the matrix** - All country × technology combinations
6. **Version configs** - Track changes over time
7. **Monitor per country/tech** - Separate metrics

### ❌ **DON'T:**
1. **Don't hardcode country logic** - Use config
2. **Don't use single calculation engine** - Use tech-specific engines
3. **Don't skip validation ranges** - Each tech has different ranges
4. **Don't forget data sovereignty** - Some countries require local storage
5. **Don't ignore performance** - 500+ configs need optimization
6. **Don't deploy globally day 1** - Phase rollout by region

---

## 13. Cost Implications

### Single Country/Tech (POC):
- **Development:** 3 weeks, $26K
- **Operational:** $5/opportunity

### 25 Countries × 2 Technologies (MVP):
- **Development:** +8 weeks, $160K
- **Operational:** $6/opportunity (more data sources)
- **Infrastructure:** +$500/month (multi-region DB)

### 100 Countries × 5 Technologies (Enterprise):
- **Development:** +6 months, $500K
- **Operational:** $4/opportunity (economies of scale)
- **Infrastructure:** +$5K/month (global deployment)

---

## 14. Success Metrics

Track these metrics **per country** and **per technology**:

```sql
-- Success metrics dashboard
SELECT 
    country,
    technology,
    COUNT(*) as total_analyses,
    AVG(duration_seconds) as avg_duration,
    AVG(cost_usd) as avg_cost,
    AVG((report_data->>'lcoe_usd_per_mwh')::float) as avg_lcoe,
    STDDEV((report_data->>'lcoe_usd_per_mwh')::float) as lcoe_stddev
FROM opportunities o
JOIN reports r ON o.opportunity_id = r.opportunity_id
WHERE o.status = 'COMPLETED'
GROUP BY country, technology
ORDER BY total_analyses DESC;
```

**Target KPIs (Per Country/Tech):**
- Completion rate: >95%
- Avg duration: <30 minutes
- Avg cost: <$5
- LCOE variance: <15% from industry benchmarks

---

**END OF SCALING GUIDE**

**Next Steps:**
1. Review this guide with engineering team
2. Prioritize countries for Phase 2 (MVP)
3. Create country config templates
4. Begin refactoring POC code for parameterization

**Questions? Contact:** Engineering Lead
