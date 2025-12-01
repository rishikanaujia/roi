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
