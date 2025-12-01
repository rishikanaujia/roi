#!/bin/bash

################################################################################
# ROI POC Complete Project Generator - Hybrid Architecture
# 
# Creates a production-ready POC with multi-country/multi-technology support
# 
# Usage: bash create_scalable_roi_poc.sh [project-name]
# Example: bash create_scalable_roi_poc.sh my-roi-poc
################################################################################

set -euo pipefail

PROJECT_NAME="${1:-roi-poc}"
BLUE='\033[0;34m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${BLUE}🚀 Creating scalable ROI POC project: ${PROJECT_NAME}${NC}"

# Create root directory
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

################################################################################
# 1. CREATE DIRECTORY STRUCTURE
################################################################################

echo -e "${BLUE}📁 Creating directory structure...${NC}"

mkdir -p src/agents/research/{policy_handlers,resource_fetchers,normalizers}
mkdir -p src/agents/analysis/calculators
mkdir -p src/agents/peer_review
mkdir -p src/core/{interfaces,factories}
mkdir -p src/data_sources
mkdir -p src/repositories
mkdir -p src/services
mkdir -p src/orchestration
mkdir -p src/models
mkdir -p src/utils
mkdir -p config/{countries,technologies,combinations,agents,prompts}
mkdir -p data/{raw,processed,cache,chromadb}
mkdir -p outputs/{reports,logs}
mkdir -p tests/{unit,integration,fixtures}
mkdir -p docker
mkdir -p scripts
mkdir -p docs

################################################################################
# 2. CREATE __INIT__ FILES
################################################################################

echo -e "${BLUE}📝 Creating __init__ files...${NC}"

for dir in src src/agents src/agents/research src/agents/research/policy_handlers \
           src/agents/research/resource_fetchers src/agents/research/normalizers \
           src/agents/analysis src/agents/analysis/calculators src/agents/peer_review \
           src/core src/core/interfaces src/core/factories src/data_sources \
           src/repositories src/services src/orchestration src/models src/utils; do
    echo '"""Package initialization"""' > "$dir/__init__.py"
done

################################################################################
# 3. CORE INTERFACES
################################################################################

echo -e "${BLUE}🔧 Creating core interfaces...${NC}"

# Agent Interface
cat > src/core/interfaces/agent_interface.py << 'INTERFACE_EOF'
"""Agent Interface - Following SOLID principles"""
from abc import ABC, abstractmethod
from typing import Any, Dict

class IAgent(ABC):
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        pass
INTERFACE_EOF

# LLM Interface
cat > src/core/interfaces/llm_interface.py << 'INTERFACE_EOF'
"""LLM Provider Interface - Strategy Pattern"""
from abc import ABC, abstractmethod

class ILLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        pass
    
    @abstractmethod
    def estimate_cost(self, tokens: int) -> float:
        pass
INTERFACE_EOF

# Policy Handler Interface
cat > src/core/interfaces/policy_handler_interface.py << 'INTERFACE_EOF'
"""Policy Handler Interface - Country-specific implementations"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class IPolicyHandler(ABC):
    @abstractmethod
    async def fetch_policy(self, technology: str, **kwargs) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_country_code(self) -> str:
        pass
INTERFACE_EOF

# Resource Fetcher Interface
cat > src/core/interfaces/resource_fetcher_interface.py << 'INTERFACE_EOF'
"""Resource Fetcher Interface - Technology-specific implementations"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class IResourceFetcher(ABC):
    @abstractmethod
    async def fetch_resource(self, latitude: float, longitude: float, **kwargs) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_technology(self) -> str:
        pass
INTERFACE_EOF

# Calculation Engine Interface
cat > src/core/interfaces/calculation_engine_interface.py << 'INTERFACE_EOF'
"""Calculation Engine Interface - Technology-specific calculations"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class ICalculationEngine(ABC):
    @abstractmethod
    def calculate_lcoe(self, params: Dict[str, Any]) -> float:
        pass
    
    @abstractmethod
    def calculate_irr(self, params: Dict[str, Any]) -> float:
        pass
    
    @abstractmethod
    def calculate_capacity_factor(self, resource_data: Dict[str, Any]) -> float:
        pass
INTERFACE_EOF

################################################################################
# 4. BASE AGENT IMPLEMENTATION
################################################################################

cat > src/core/base_agent.py << 'BASEAGENT_EOF'
"""Base Agent - Template Method Pattern"""
import logging
from typing import Any, Dict, Optional
from abc import abstractmethod
from src.core.interfaces.agent_interface import IAgent
from src.core.interfaces.llm_interface import ILLMProvider

class BaseAgent(IAgent):
    def __init__(self, name: str, llm_provider: ILLMProvider, 
                 config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        self.name = name
        self.llm_provider = llm_provider
        self.config = config
        self.logger = logger or logging.getLogger(self.name)
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.validate_input(input_data):
                raise ValueError(f"Invalid input for {self.name}")
            
            self.logger.info(f"{self.name} execution started")
            processed = await self._preprocess(input_data)
            result = await self._execute_core(processed)
            final = await self._postprocess(result)
            self.logger.info(f"{self.name} execution completed")
            return final
        except Exception as e:
            self.logger.error(f"{self.name} failed: {str(e)}")
            raise
    
    @abstractmethod
    async def _execute_core(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    async def _preprocess(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return input_data
    
    async def _postprocess(self, result: Dict[str, Any]) -> Dict[str, Any]:
        return result
    
    def get_name(self) -> str:
        return self.name
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return input_data is not None and isinstance(input_data, dict)
BASEAGENT_EOF

################################################################################
# 5. CONFIG LOADER (Critical for scaling)
################################################################################

cat > src/utils/config_loader.py << 'CONFIGLOADER_EOF'
"""Dynamic Configuration Loader - Enables multi-country/tech scaling"""
import yaml
import os
import re
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigLoader:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self._cache = {}
    
    def load_country_config(self, country_code: str) -> Dict[str, Any]:
        cache_key = f"country_{country_code}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        default = self._load_yaml("countries/_default.yaml")
        country_file = f"countries/{country_code.lower()}.yaml"
        country_config = self._load_yaml(country_file, default={})
        
        merged = self._deep_merge(default, country_config)
        self._cache[cache_key] = merged
        return merged
    
    def load_technology_config(self, tech_code: str) -> Dict[str, Any]:
        cache_key = f"tech_{tech_code}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        default = self._load_yaml("technologies/_default.yaml")
        tech_file = f"technologies/{tech_code.lower()}.yaml"
        tech_config = self._load_yaml(tech_file, default={})
        
        merged = self._deep_merge(default, tech_config)
        self._cache[cache_key] = merged
        return merged
    
    def load_combination_config(self, country_code: str, tech_code: str) -> Dict[str, Any]:
        country_config = self.load_country_config(country_code)
        tech_config = self.load_technology_config(tech_code)
        
        combo_file = f"combinations/{country_code.lower()}_{tech_code.lower()}.yaml"
        combo_config = self._load_yaml(combo_file, default={})
        
        merged = self._deep_merge(country_config, tech_config)
        merged = self._deep_merge(merged, combo_config)
        
        self._validate_compatibility(merged, country_code, tech_code)
        return merged
    
    def get_supported_countries(self) -> list:
        countries_dir = self.config_dir / "countries"
        return [f.stem for f in countries_dir.glob("*.yaml") if f.stem != "_default"]
    
    def get_supported_technologies(self, country_code: Optional[str] = None) -> list:
        if country_code:
            config = self.load_country_config(country_code)
            return config.get("country", {}).get("supported_technologies", [])
        
        tech_dir = self.config_dir / "technologies"
        return [f.stem for f in tech_dir.glob("*.yaml") if f.stem != "_default"]
    
    def _load_yaml(self, relative_path: str, default: Dict = None) -> Dict:
        file_path = self.config_dir / relative_path
        if not file_path.exists():
            if default is not None:
                return default
            raise FileNotFoundError(f"Config not found: {file_path}")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        content = self._replace_env_vars(content)
        return yaml.safe_load(content)
    
    def _replace_env_vars(self, content: str) -> str:
        pattern = r'\$\{([^}:]+)(?::-(.*?))?\}'
        def replace(match):
            var_name = match.group(1)
            default_value = match.group(2) or ""
            return os.environ.get(var_name, default_value)
        return re.sub(pattern, replace, content)
    
    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def _validate_compatibility(self, config: Dict, country_code: str, tech_code: str):
        supported = config.get("country", {}).get("supported_technologies", [])
        if tech_code not in supported:
            raise ValueError(f"Technology '{tech_code}' not supported in '{country_code}'")
CONFIGLOADER_EOF

################################################################################
# 6. POLICY HANDLERS (Country-specific)
################################################################################

# Base Policy Handler
cat > src/agents/research/policy_handlers/base_policy_handler.py << 'HANDLER_EOF'
"""Base Policy Handler"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from src.core.interfaces.policy_handler_interface import IPolicyHandler

class BasePolicyHandler(IPolicyHandler):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    @abstractmethod
    async def fetch_policy(self, technology: str, **kwargs) -> Dict[str, Any]:
        pass
    
    def get_country_code(self) -> str:
        return self.config.get("country", {}).get("code", "UNKNOWN")
HANDLER_EOF

# USA Policy Handler
cat > src/agents/research/policy_handlers/usa_policy_handler.py << 'HANDLER_EOF'
"""USA-specific Policy Handler"""
from typing import Dict, Any
from src.agents.research.policy_handlers.base_policy_handler import BasePolicyHandler

class USAPolicyHandler(BasePolicyHandler):
    async def fetch_policy(self, technology: str, **kwargs) -> Dict[str, Any]:
        # USA-specific: Federal ITC, state incentives, MACRS
        return {
            "country": "USA",
            "federal_itc_percentage": 30.0,
            "state_incentives": ["Texas RPS: 50% by 2030"],
            "depreciation_method": "MACRS",
            "depreciation_years": 5,
            "tax_rate": 0.21,
            "source": "IRS + DSIRE"
        }
HANDLER_EOF

# Germany Policy Handler
cat > src/agents/research/policy_handlers/germany_policy_handler.py << 'HANDLER_EOF'
"""Germany-specific Policy Handler"""
from typing import Dict, Any
from src.agents.research.policy_handlers.base_policy_handler import BasePolicyHandler

class GermanyPolicyHandler(BasePolicyHandler):
    async def fetch_policy(self, technology: str, **kwargs) -> Dict[str, Any]:
        # Germany-specific: EEG feed-in tariff
        offshore_bonus = 0
        if technology == "offshore_wind":
            offshore_bonus = 5.0
        
        return {
            "country": "DEU",
            "feed_in_tariff_eur_per_mwh": 45.0,
            "offshore_wind_bonus": offshore_bonus,
            "depreciation_method": "Straight-line",
            "depreciation_years": 20,
            "tax_rate": 0.30,
            "source": "EEG"
        }
HANDLER_EOF

# Policy Handler Factory
cat > src/agents/research/policy_handlers/factory.py << 'FACTORY_EOF'
"""Policy Handler Factory - Add countries here"""
from typing import Dict, Any
from src.agents.research.policy_handlers.base_policy_handler import BasePolicyHandler
from src.agents.research.policy_handlers.usa_policy_handler import USAPolicyHandler
from src.agents.research.policy_handlers.germany_policy_handler import GermanyPolicyHandler

class PolicyHandlerFactory:
    _handlers = {
        "USA": USAPolicyHandler,
        "DEU": GermanyPolicyHandler,
        # Add more countries here as you scale
    }
    
    @classmethod
    def create(cls, country_code: str, config: Dict[str, Any]) -> BasePolicyHandler:
        handler_class = cls._handlers.get(country_code)
        if not handler_class:
            raise ValueError(f"No policy handler for country: {country_code}")
        return handler_class(config)
    
    @classmethod
    def register(cls, country_code: str, handler_class: type):
        cls._handlers[country_code] = handler_class
FACTORY_EOF

################################################################################
# 7. RESOURCE FETCHERS (Technology-specific)
################################################################################

# Base Resource Fetcher
cat > src/agents/research/resource_fetchers/base_resource_fetcher.py << 'FETCHER_EOF'
"""Base Resource Fetcher"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from src.core.interfaces.resource_fetcher_interface import IResourceFetcher

class BaseResourceFetcher(IResourceFetcher):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    @abstractmethod
    async def fetch_resource(self, latitude: float, longitude: float, **kwargs) -> Dict[str, Any]:
        pass
    
    def get_technology(self) -> str:
        return self.config.get("technology", {}).get("code", "UNKNOWN")
FETCHER_EOF

# Solar Resource Fetcher
cat > src/agents/research/resource_fetchers/solar_fetcher.py << 'FETCHER_EOF'
"""Solar-specific Resource Fetcher"""
from typing import Dict, Any
from src.agents.research.resource_fetchers.base_resource_fetcher import BaseResourceFetcher

class SolarResourceFetcher(BaseResourceFetcher):
    async def fetch_resource(self, latitude: float, longitude: float, **kwargs) -> Dict[str, Any]:
        # Solar-specific: GHI, temperature
        # In real implementation, call NASA POWER API or NREL API
        avg_ghi = 5.5  # Mock data
        avg_temp = 25.0
        
        return {
            "technology": "solar_pv",
            "avg_ghi_kwh_m2_day": avg_ghi,
            "avg_temperature_c": avg_temp,
            "confidence": "high",
            "source": "NASA POWER (mock)"
        }
FETCHER_EOF

# Wind Resource Fetcher
cat > src/agents/research/resource_fetchers/wind_fetcher.py << 'FETCHER_EOF'
"""Wind-specific Resource Fetcher"""
from typing import Dict, Any
from src.agents.research.resource_fetchers.base_resource_fetcher import BaseResourceFetcher

class WindResourceFetcher(BaseResourceFetcher):
    async def fetch_resource(self, latitude: float, longitude: float, **kwargs) -> Dict[str, Any]:
        # Wind-specific: Wind speed, power density
        avg_wind_speed = 7.5  # Mock data
        wind_power_density = 400
        
        return {
            "technology": "onshore_wind",
            "avg_wind_speed_m_s": avg_wind_speed,
            "wind_power_density_w_m2": wind_power_density,
            "hub_height_m": kwargs.get("hub_height", 100),
            "confidence": "high",
            "source": "Global Wind Atlas (mock)"
        }
FETCHER_EOF

# Resource Fetcher Factory
cat > src/agents/research/resource_fetchers/factory.py << 'FACTORY_EOF'
"""Resource Fetcher Factory - Add technologies here"""
from typing import Dict, Any
from src.agents.research.resource_fetchers.base_resource_fetcher import BaseResourceFetcher
from src.agents.research.resource_fetchers.solar_fetcher import SolarResourceFetcher
from src.agents.research.resource_fetchers.wind_fetcher import WindResourceFetcher

class ResourceFetcherFactory:
    _fetchers = {
        "solar_pv": SolarResourceFetcher,
        "onshore_wind": WindResourceFetcher,
        # Add more technologies here as you scale
    }
    
    @classmethod
    def create(cls, technology: str, config: Dict[str, Any]) -> BaseResourceFetcher:
        fetcher_class = cls._fetchers.get(technology)
        if not fetcher_class:
            raise ValueError(f"No resource fetcher for technology: {technology}")
        return fetcher_class(config)
    
    @classmethod
    def register(cls, technology: str, fetcher_class: type):
        cls._fetchers[technology] = fetcher_class
FACTORY_EOF

################################################################################
# 8. RESEARCH AGENT (Hybrid - uses pluggable components)
################################################################################

cat > src/agents/research/research_agent.py << 'AGENT_EOF'
"""Research Agent - Hybrid Architecture with Pluggable Components"""
import json
from typing import Dict, Any
from src.core.base_agent import BaseAgent
from src.utils.config_loader import ConfigLoader
from src.agents.research.policy_handlers.factory import PolicyHandlerFactory
from src.agents.research.resource_fetchers.factory import ResourceFetcherFactory

class ResearchAgent(BaseAgent):
    """Generic research agent that works for any country + technology"""
    
    def __init__(self, llm_provider, config, country_code: str, technology: str, logger=None):
        super().__init__("ResearchAgent", llm_provider, config, logger)
        
        self.country_code = country_code
        self.technology = technology
        
        # Load dynamic configuration
        config_loader = ConfigLoader()
        self.runtime_config = config_loader.load_combination_config(country_code, technology)
        
        # Plug in country-specific policy handler
        self.policy_handler = PolicyHandlerFactory.create(country_code, self.runtime_config)
        
        # Plug in technology-specific resource fetcher
        self.resource_fetcher = ResourceFetcherFactory.create(technology, self.runtime_config)
    
    async def _execute_core(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Fetch policy (country-specific implementation)
        policy_data = await self.policy_handler.fetch_policy(
            technology=self.technology,
            **input_data
        )
        
        # Fetch resource (technology-specific implementation)
        resource_data = await self.resource_fetcher.fetch_resource(
            latitude=input_data["latitude"],
            longitude=input_data["longitude"],
            **input_data
        )
        
        # Normalize using LLM
        normalized = await self._normalize_with_llm(policy_data, resource_data)
        
        return normalized
    
    async def _normalize_with_llm(self, policy_data, resource_data):
        prompt = f"""
Normalize renewable energy data for:
Country: {self.runtime_config['country']['name']}
Technology: {self.runtime_config['technology']['name']}

Policy Data: {json.dumps(policy_data, indent=2)}
Resource Data: {json.dumps(resource_data, indent=2)}

Output valid JSON with keys: policy_data, resource_data, data_completeness
"""
        response = await self.llm_provider.generate(prompt)
        return json.loads(response)
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        required = ["latitude", "longitude"]
        return all(k in input_data for k in required)
AGENT_EOF

################################################################################
# 9. CALCULATION ENGINES (Technology-specific)
################################################################################

# Base Calculation Engine
cat > src/agents/analysis/calculators/base_calculator.py << 'CALC_EOF'
"""Base Calculation Engine"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from src.core.interfaces.calculation_engine_interface import ICalculationEngine

class BaseCalculator(ICalculationEngine):
    @abstractmethod
    def calculate_lcoe(self, params: Dict[str, Any]) -> float:
        pass
    
    @abstractmethod
    def calculate_irr(self, params: Dict[str, Any]) -> float:
        pass
    
    @abstractmethod
    def calculate_capacity_factor(self, resource_data: Dict[str, Any]) -> float:
        pass
CALC_EOF

# Solar Calculator
cat > src/agents/analysis/calculators/solar_calculator.py << 'CALC_EOF'
"""Solar PV Calculation Engine"""
from typing import Dict, Any
from src.agents.analysis.calculators.base_calculator import BaseCalculator

class SolarPVCalculator(BaseCalculator):
    def calculate_lcoe(self, params: Dict[str, Any]) -> float:
        capex = params['capex_usd_per_kw']
        opex = params['opex_usd_per_kw_year']
        cf = params['capacity_factor']
        lifetime = params['project_lifetime_years']
        dr = params['discount_rate']
        
        annual_energy = 8760 * cf
        pv_capex = capex
        pv_opex = opex * ((1 - (1 + dr)**-lifetime) / dr)
        pv_energy = annual_energy * ((1 - (1 + dr)**-lifetime) / dr)
        
        lcoe = ((pv_capex + pv_opex) / pv_energy) * 1000
        return round(lcoe, 2)
    
    def calculate_irr(self, params: Dict[str, Any]) -> float:
        # Simplified IRR calculation
        lcoe = self.calculate_lcoe(params)
        electricity_price = params.get('electricity_price', 40.0)
        
        if lcoe < electricity_price:
            irr = 8 + (electricity_price - lcoe) * 0.5
        else:
            irr = 8 - (lcoe - electricity_price) * 0.3
        
        return round(max(5, min(25, irr)), 2)
    
    def calculate_capacity_factor(self, resource_data: Dict[str, Any]) -> float:
        ghi = resource_data['avg_ghi_kwh_m2_day']
        temp = resource_data.get('avg_temperature_c', 25)
        
        base_cf = (ghi * 365) / 8760
        temp_factor = 1 - 0.004 * max(0, temp - 25)
        system_losses = 0.14
        
        cf = base_cf * temp_factor * (1 - system_losses)
        return round(min(max(cf, 0.10), 0.30), 4)
CALC_EOF

# Wind Calculator
cat > src/agents/analysis/calculators/wind_calculator.py << 'CALC_EOF'
"""Onshore Wind Calculation Engine"""
from typing import Dict, Any
from src.agents.analysis/calculators.base_calculator import BaseCalculator

class OnshoreWindCalculator(BaseCalculator):
    def calculate_lcoe(self, params: Dict[str, Any]) -> float:
        capex = params['capex_usd_per_kw']
        opex = params['opex_usd_per_kw_year']
        cf = params['capacity_factor']
        lifetime = params['project_lifetime_years']
        dr = params['discount_rate']
        
        annual_energy = 8760 * cf
        pv_capex = capex
        pv_opex = opex * ((1 - (1 + dr)**-lifetime) / dr)
        pv_energy = annual_energy * ((1 - (1 + dr)**-lifetime) / dr)
        
        lcoe = ((pv_capex + pv_opex) / pv_energy) * 1000
        return round(lcoe, 2)
    
    def calculate_irr(self, params: Dict[str, Any]) -> float:
        lcoe = self.calculate_lcoe(params)
        electricity_price = params.get('electricity_price', 40.0)
        
        if lcoe < electricity_price:
            irr = 8 + (electricity_price - lcoe) * 0.4
        else:
            irr = 8 - (lcoe - electricity_price) * 0.25
        
        return round(max(5, min(25, irr)), 2)
    
    def calculate_capacity_factor(self, resource_data: Dict[str, Any]) -> float:
        wind_speed = resource_data['avg_wind_speed_m_s']
        
        if wind_speed < 6:
            cf = 0.20
        elif wind_speed < 7:
            cf = 0.30
        elif wind_speed < 8:
            cf = 0.38
        else:
            cf = 0.45
        
        return round(min(max(cf, 0.25), 0.50), 4)
CALC_EOF

# Calculator Factory
cat > src/agents/analysis/calculators/factory.py << 'FACTORY_EOF'
"""Calculation Engine Factory"""
from typing import Dict, Any
from src.agents.analysis.calculators.base_calculator import BaseCalculator
from src.agents.analysis.calculators.solar_calculator import SolarPVCalculator
from src.agents.analysis.calculators.wind_calculator import OnshoreWindCalculator

class CalculationEngineFactory:
    _engines = {
        "solar_pv": SolarPVCalculator,
        "onshore_wind": OnshoreWindCalculator,
        # Add more technologies here
    }
    
    @classmethod
    def get_engine(cls, technology: str) -> BaseCalculator:
        engine_class = cls._engines.get(technology)
        if not engine_class:
            raise ValueError(f"No calculation engine for: {technology}")
        return engine_class()
FACTORY_EOF

################################################################################
# 10. ANALYSIS AGENT (Hybrid)
################################################################################

cat > src/agents/analysis/analysis_agent.py << 'AGENT_EOF'
"""Analysis Agent - Hybrid Architecture"""
from typing import Dict, Any
from src.core.base_agent import BaseAgent
from src.utils.config_loader import ConfigLoader
from src.agents.analysis.calculators.factory import CalculationEngineFactory

class AnalysisAgent(BaseAgent):
    """Generic analysis agent with technology-specific calculations"""
    
    def __init__(self, llm_provider, config, country_code: str, technology: str, logger=None):
        super().__init__("AnalysisAgent", llm_provider, config, logger)
        
        self.country_code = country_code
        self.technology = technology
        
        config_loader = ConfigLoader()
        self.runtime_config = config_loader.load_combination_config(country_code, technology)
        
        # Get technology-specific calculation engine
        self.calc_engine = CalculationEngineFactory.get_engine(technology)
    
    async def _execute_core(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        research_data = input_data['research_data']
        resource_data = research_data['resource_data']
        
        # Calculate capacity factor (technology-specific)
        cf = self.calc_engine.calculate_capacity_factor(resource_data)
        
        # Build financial parameters (country-specific)
        params = {
            'capex_usd_per_kw': self.runtime_config['technology']['financial']['capex_usd_per_kw'],
            'opex_usd_per_kw_year': self.runtime_config['technology']['financial']['opex_usd_per_kw_year'],
            'project_lifetime_years': self.runtime_config['technology']['financial']['project_lifetime_years'],
            'discount_rate': self.runtime_config['country']['financial']['discount_rate'],
            'capacity_factor': cf,
            'electricity_price': self.runtime_config['country']['grid'].get('wholesale_price_usd_per_mwh', 40.0),
        }
        
        # Calculate LCOE and IRR (technology-specific)
        lcoe = self.calc_engine.calculate_lcoe(params)
        irr = self.calc_engine.calculate_irr(params)
        
        return {
            "lcoe_usd_per_mwh": lcoe,
            "irr_percent": irr,
            "capacity_factor": cf,
            "assumptions": params,
            "confidence": "high"
        }
AGENT_EOF

################################################################################
# 11. CONFIGURATION FILES
################################################################################

echo -e "${BLUE}⚙️  Creating configuration files...${NC}"

# Default Country Config
cat > config/countries/_default.yaml << 'CONFIG_EOF'
country:
  code: "DEFAULT"
  name: "Default Country"
  
financial:
  discount_rate: 0.08
  corporate_tax_rate: 0.21

grid:
  wholesale_price_usd_per_mwh: 40.0

supported_technologies:
  - solar_pv
  - onshore_wind
CONFIG_EOF

# USA Config
cat > config/countries/usa.yaml << 'CONFIG_EOF'
country:
  code: "USA"
  name: "United States"
  currency: "USD"
  
financial:
  discount_rate: 0.08
  corporate_tax_rate: 0.21

grid:
  wholesale_price_usd_per_mwh: 35.0

supported_technologies:
  - solar_pv
  - onshore_wind
CONFIG_EOF

# Germany Config
cat > config/countries/germany.yaml << 'CONFIG_EOF'
country:
  code: "DEU"
  name: "Germany"
  currency: "EUR"
  
financial:
  discount_rate: 0.06
  corporate_tax_rate: 0.30

grid:
  wholesale_price_usd_per_mwh: 45.0

supported_technologies:
  - solar_pv
  - onshore_wind
  - offshore_wind
CONFIG_EOF

# Default Technology Config
cat > config/technologies/_default.yaml << 'CONFIG_EOF'
technology:
  code: "default"
  name: "Default Technology"
  
financial:
  capex_usd_per_kw: 1000.0
  opex_usd_per_kw_year: 10.0
  project_lifetime_years: 25
CONFIG_EOF

# Solar PV Config
cat > config/technologies/solar_pv.yaml << 'CONFIG_EOF'
technology:
  code: "solar_pv"
  name: "Solar Photovoltaic"
  category: "solar"
  
financial:
  capex_usd_per_kw: 1200.0
  opex_usd_per_kw_year: 15.0
  project_lifetime_years: 25
  capacity_factor_range: [0.10, 0.30]

validation:
  lcoe_usd_per_mwh: [20, 80]
  irr_percent: [5, 25]
CONFIG_EOF

# Onshore Wind Config
cat > config/technologies/onshore_wind.yaml << 'CONFIG_EOF'
technology:
  code: "onshore_wind"
  name: "Onshore Wind"
  category: "wind"
  
financial:
  capex_usd_per_kw: 1500.0
  opex_usd_per_kw_year: 40.0
  project_lifetime_years: 25
  capacity_factor_range: [0.25, 0.45]

validation:
  lcoe_usd_per_mwh: [30, 90]
  irr_percent: [5, 20]
CONFIG_EOF

# Main App Config
cat > config/app_config.yaml << 'CONFIG_EOF'
app:
  name: "ROI POC"
  version: "1.0.0"
  environment: "development"

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "outputs/logs/app.log"

llm:
  primary:
    provider: "anthropic"
    model: "claude-sonnet-4-20250514"
    api_key: "${ANTHROPIC_API_KEY}"
    temperature: 0.3
CONFIG_EOF

################################################################################
# 12. DOCKER FILES
################################################################################

echo -e "${BLUE}🐳 Creating Docker files...${NC}"

cat > docker-compose.yml << 'DOCKER_EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: roi_poc
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8000:8000"
    volumes:
      - chromadb_data:/chroma/chroma

volumes:
  postgres_data:
  redis_data:
  chromadb_data:
DOCKER_EOF

cat > Dockerfile << 'DOCKERFILE_EOF'
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
DOCKERFILE_EOF

################################################################################
# 13. REQUIREMENTS.TXT
################################################################################

cat > requirements.txt << 'REQUIREMENTS_EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
anthropic==0.7.7
openai==1.3.7
chromadb==0.4.18
asyncpg==0.29.0
redis==5.0.1
aiohttp==3.9.1
pyyaml==6.0.1
python-dotenv==1.0.0
pytest==7.4.3
pytest-asyncio==0.21.1
REQUIREMENTS_EOF

################################################################################
# 14. MAIN API
################################################################################

cat > src/main.py << 'MAIN_EOF'
"""FastAPI Main Application"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

app = FastAPI(title="ROI POC API", version="1.0.0")

class OpportunityRequest(BaseModel):
    country: str
    technology: str
    latitude: float
    longitude: float

@app.get("/")
async def root():
    return {"message": "ROI POC API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/v1/opportunities")
async def create_opportunity(request: OpportunityRequest):
    # TODO: Implement workflow orchestration
    return {
        "opportunity_id": f"OPP-{request.country}-{request.technology}",
        "status": "INITIALIZED",
        "message": "Implement orchestration to connect all components"
    }
MAIN_EOF

################################################################################
# 15. ENVIRONMENT FILE
################################################################################

cat > .env.example << 'ENV_EOF'
DB_HOST=localhost
DB_PORT=5432
REDIS_HOST=localhost
REDIS_PORT=6379
CHROMA_HOST=localhost
CHROMA_PORT=8000
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
ENV_EOF

################################################################################
# 16. README
################################################################################

cat > README.md << 'README_EOF'
# ROI POC - Scalable Multi-Country/Multi-Technology Architecture

## Architecture: Hybrid Pattern

This project uses a **hybrid architecture** that scales efficiently:

```
Generic Agent + Pluggable Components = Easy Scaling
```

### Adding New Country (3 steps):

1. Create policy handler:
```python
# src/agents/research/policy_handlers/india_policy_handler.py
class IndiaPolicyHandler(BasePolicyHandler):
    async def fetch_policy(self, technology: str, **kwargs):
        # India-specific logic
        pass
```

2. Register in factory:
```python
# src/agents/research/policy_handlers/factory.py
PolicyHandlerFactory.register("IND", IndiaPolicyHandler)
```

3. Create config:
```yaml
# config/countries/india.yaml
country:
  code: "IND"
  name: "India"
  # ... country-specific settings
```

### Adding New Technology (3 steps):

1. Create resource fetcher:
```python
# src/agents/research/resource_fetchers/hydro_fetcher.py
class HydroResourceFetcher(BaseResourceFetcher):
    async def fetch_resource(self, **kwargs):
        # Hydro-specific logic
        pass
```

2. Create calculator:
```python
# src/agents/analysis/calculators/hydro_calculator.py
class HydroCalculator(BaseCalculator):
    def calculate_lcoe(self, params):
        # Hydro-specific calculations
        pass
```

3. Create config:
```yaml
# config/technologies/hydro.yaml
technology:
  code: "hydro"
  # ... technology-specific settings
```

## Quick Start

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Start services
docker-compose up -d

# Run API
python -m uvicorn src.main:app --reload
```

## Current Support

- **Countries:** USA, Germany (easily add more)
- **Technologies:** Solar PV, Onshore Wind (easily add more)

## Scaling Summary

| Action | Files to Create | Lines of Code |
|--------|----------------|---------------|
| Add country | 1 handler + 1 config | ~150 lines |
| Add technology | 1 fetcher + 1 calculator + 1 config | ~350 lines |

**No code duplication. No breaking existing functionality.**

## Testing

```bash
pytest tests/
```

## Project Structure

```
src/
├── agents/
│   ├── research/
│   │   ├── research_agent.py          # Generic framework
│   │   ├── policy_handlers/           # Country-specific
│   │   │   ├── usa_policy_handler.py
│   │   │   └── germany_policy_handler.py
│   │   └── resource_fetchers/         # Technology-specific
│   │       ├── solar_fetcher.py
│   │       └── wind_fetcher.py
│   └── analysis/
│       ├── analysis_agent.py          # Generic framework
│       └── calculators/               # Technology-specific
│           ├── solar_calculator.py
│           └── wind_calculator.py
├── core/
│   └── interfaces/                    # Contracts
└── utils/
    └── config_loader.py               # Dynamic configuration

config/
├── countries/                         # Add countries here
│   ├── usa.yaml
│   └── germany.yaml
└── technologies/                      # Add technologies here
    ├── solar_pv.yaml
    └── onshore_wind.yaml
```

## License

Proprietary
README_EOF

################################################################################
# 17. GITIGNORE
################################################################################

cat > .gitignore << 'GITIGNORE_EOF'
__pycache__/
*.pyc
.Python
env/
venv/
.env
*.log
data/chromadb/
outputs/logs/
.DS_Store
GITIGNORE_EOF

################################################################################
# 18. SAMPLE TEST
################################################################################

cat > tests/test_scaling.py << 'TEST_EOF'
"""Test that scaling works - add countries and technologies easily"""
import pytest
from src.utils.config_loader import ConfigLoader

def test_config_loader_supports_multiple_countries():
    loader = ConfigLoader()
    
    # Should support USA
    usa_config = loader.load_country_config("USA")
    assert usa_config["country"]["code"] == "USA"
    
    # Should support Germany
    germany_config = loader.load_country_config("DEU")
    assert germany_config["country"]["code"] == "DEU"

def test_config_loader_supports_multiple_technologies():
    loader = ConfigLoader()
    
    # Should support Solar PV
    solar_config = loader.load_technology_config("solar_pv")
    assert solar_config["technology"]["code"] == "solar_pv"
    
    # Should support Wind
    wind_config = loader.load_technology_config("onshore_wind")
    assert wind_config["technology"]["code"] == "onshore_wind"

def test_combination_configs_work():
    loader = ConfigLoader()
    
    # USA + Solar should work
    usa_solar = loader.load_combination_config("USA", "solar_pv")
    assert usa_solar["country"]["code"] == "USA"
    assert usa_solar["technology"]["code"] == "solar_pv"
    
    # Germany + Wind should work
    germany_wind = loader.load_combination_config("DEU", "onshore_wind")
    assert germany_wind["country"]["code"] == "DEU"
    assert germany_wind["technology"]["code"] == "onshore_wind"
TEST_EOF

################################################################################
# 19. FINAL TOUCHES
################################################################################

# Create empty .gitkeep files
touch outputs/logs/.gitkeep
touch outputs/reports/.gitkeep
touch data/chromadb/.gitkeep

################################################################################
# SUCCESS MESSAGE
################################################################################

echo -e "${GREEN}✅ Project created successfully!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🚀 ROI POC - SCALABLE ARCHITECTURE READY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📁 Project: $PROJECT_NAME"
echo ""
echo "🏗️  Architecture: HYBRID (Generic Agents + Pluggable Components)"
echo ""
echo "✅ Currently supports:"
echo "   - Countries: USA, Germany"
echo "   - Technologies: Solar PV, Onshore Wind"
echo ""
echo "📈 Easy to scale:"
echo "   - Add country: Create 1 handler + 1 config (~150 lines)"
echo "   - Add technology: Create 1 fetcher + 1 calculator + 1 config (~350 lines)"
echo ""
echo "🎯 Next steps:"
echo "   1. cd $PROJECT_NAME"
echo "   2. cp .env.example .env"
echo "   3. Edit .env with your API keys"
echo "   4. python3 -m venv venv"
echo "   5. source venv/bin/activate"
echo "   6. pip install -r requirements.txt"
echo "   7. docker-compose up -d"
echo "   8. python -m uvicorn src.main:app --reload"
echo ""
echo "📖 Documentation: README.md"
echo "🧪 Test scaling: pytest tests/test_scaling.py"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
