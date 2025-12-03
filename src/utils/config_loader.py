"""
Dynamic Configuration Loader - The Key to Multi-Country/Multi-Technology Scaling

This file enables:
1. Add new country → Just create YAML file (no code change)
2. Add new technology → Just create YAML file (no code change)
3. Combine country + technology → Automatic merging with overrides
4. Environment variable substitution → ${VAR_NAME:-default}
5. Validation → Ensures country supports technology

Example Usage:
    loader = ConfigLoader()

    # Load USA config
    usa = loader.load_country_config("USA")

    # Load Solar PV config
    solar = loader.load_technology_config("solar_pv")

    # Load combined USA + Solar PV config (with validation)
    usa_solar = loader.load_combination_config("USA", "solar_pv")
"""

import yaml
import os
import re
from pathlib import Path
from typing import Dict, Any, Optional, List


class ConfigLoader:
    """
    Dynamic configuration loader for multi-country/multi-technology support.

    Configuration Hierarchy:
        1. _default.yaml (base defaults)
        2. {country}.yaml (country-specific overrides)
        3. {technology}.yaml (technology-specific overrides)
        4. {country}_{technology}.yaml (combination-specific overrides)

    The later configs override earlier ones using deep merge.

    Attributes:
        config_dir (Path): Root directory for all config files
        _cache (Dict): In-memory cache to avoid re-reading files
    """

    def __init__(self, config_dir: str = "config"):
        """
        Initialize ConfigLoader.

        Args:
            config_dir: Path to configuration directory (default: "config")
        """
        self.config_dir = Path(config_dir)
        self._cache: Dict[str, Dict[str, Any]] = {}

        # Validate that config directory exists
        if not self.config_dir.exists():
            raise ValueError(f"Config directory not found: {self.config_dir}")

    def load_country_config(self, country_code: str) -> Dict[str, Any]:
        """
        Load country-specific configuration.

        Merges _default.yaml with {country}.yaml

        Args:
            country_code: ISO 3166-1 alpha-3 country code (e.g., "USA", "DEU", "IND")

        Returns:
            Dict containing merged country configuration

        Example:
            >>> loader = ConfigLoader()
            >>> usa_config = loader.load_country_config("USA")
            >>> print(usa_config["country"]["name"])
            'United States'
            >>> print(usa_config["country"]["financial"]["discount_rate"])
            0.08
        """
        # Check cache first
        cache_key = f"country_{country_code}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Load default country configuration
        default_config = self._load_yaml("countries/_default.yaml")

        # Load country-specific configuration
        country_file = f"countries/{country_code.lower()}.yaml"
        country_config = self._load_yaml(country_file, default={})

        # Deep merge: country-specific overrides default
        merged = self._deep_merge(default_config, country_config)

        # Cache the result
        self._cache[cache_key] = merged
        return merged

    def load_technology_config(self, tech_code: str) -> Dict[str, Any]:
        """
        Load technology-specific configuration.

        Merges _default.yaml with {technology}.yaml

        Args:
            tech_code: Technology identifier (e.g., "solar_pv", "onshore_wind")

        Returns:
            Dict containing merged technology configuration

        Example:
            >>> loader = ConfigLoader()
            >>> solar_config = loader.load_technology_config("solar_pv")
            >>> print(solar_config["technology"]["name"])
            'Solar Photovoltaic'
            >>> print(solar_config["technology"]["financial"]["capex_usd_per_kw"])
            1200.0
        """
        # Check cache
        cache_key = f"tech_{tech_code}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Load default technology configuration
        default_config = self._load_yaml("technologies/_default.yaml")

        # Load technology-specific configuration
        tech_file = f"technologies/{tech_code.lower()}.yaml"
        tech_config = self._load_yaml(tech_file, default={})

        # Deep merge
        merged = self._deep_merge(default_config, tech_config)

        # Cache the result
        self._cache[cache_key] = merged
        return merged

    def load_combination_config(
            self,
            country_code: str,
            tech_code: str
    ) -> Dict[str, Any]:
        """
        Load combined country + technology configuration with validation.

        Configuration precedence (later overrides earlier):
            1. countries/_default.yaml
            2. countries/{country}.yaml
            3. technologies/_default.yaml
            4. technologies/{technology}.yaml
            5. combinations/{country}_{technology}.yaml (optional)

        Args:
            country_code: ISO 3166-1 alpha-3 country code
            tech_code: Technology identifier

        Returns:
            Dict containing fully merged configuration

        Raises:
            ValueError: If technology is not supported in the country

        Example:
            >>> loader = ConfigLoader()
            >>> # Get USA + Solar PV configuration
            >>> config = loader.load_combination_config("USA", "solar_pv")
            >>>
            >>> # Access country-specific data
            >>> print(config["country"]["name"])
            'United States'
            >>>
            >>> # Access technology-specific data
            >>> print(config["technology"]["name"])
            'Solar Photovoltaic'
            >>>
            >>> # Access financial parameters (merged from both)
            >>> print(config["country"]["financial"]["discount_rate"])  # From country
            0.08
            >>> print(config["technology"]["financial"]["capex_usd_per_kw"])  # From tech
            1200.0
        """
        # Load base configurations
        country_config = self.load_country_config(country_code)
        tech_config = self.load_technology_config(tech_code)

        # Check for combination-specific override file
        combo_file = f"combinations/{country_code.lower()}_{tech_code.lower()}.yaml"
        combo_config = self._load_yaml(combo_file, default={})

        # Merge in order: country → technology → combination
        merged = self._deep_merge(country_config, tech_config)
        merged = self._deep_merge(merged, combo_config)

        # Validate that country supports this technology
        self._validate_compatibility(merged, country_code, tech_code)

        return merged

    def get_supported_countries(self) -> List[str]:
        """
        Get list of all supported countries.

        Returns:
            List of country codes (e.g., ['USA', 'DEU', 'IND'])

        Example:
            >>> loader = ConfigLoader()
            >>> countries = loader.get_supported_countries()
            >>> print(countries)
            ['usa', 'germany', 'china', 'india']
        """
        countries_dir = self.config_dir / "countries"

        if not countries_dir.exists():
            return []

        return [
            f.stem  # Get filename without extension
            for f in countries_dir.glob("*.yaml")
            if f.stem != "_default"  # Exclude default template
        ]

    def get_supported_technologies(
            self,
            country_code: Optional[str] = None
    ) -> List[str]:
        """
        Get list of supported technologies.

        Args:
            country_code: If provided, returns only technologies supported in that country.
                         If None, returns all technologies.

        Returns:
            List of technology codes

        Example:
            >>> loader = ConfigLoader()
            >>>
            >>> # Get all technologies
            >>> all_techs = loader.get_supported_technologies()
            >>> print(all_techs)
            ['solar_pv', 'onshore_wind', 'offshore_wind', 'hydro']
            >>>
            >>> # Get technologies supported in USA
            >>> usa_techs = loader.get_supported_technologies("USA")
            >>> print(usa_techs)
            ['solar_pv', 'onshore_wind']
        """
        if country_code:
            # Return only technologies supported in this country
            config = self.load_country_config(country_code)
            return config.get("country", {}).get("supported_technologies", [])

        # Return all available technologies
        tech_dir = self.config_dir / "technologies"

        if not tech_dir.exists():
            return []

        return [
            f.stem
            for f in tech_dir.glob("*.yaml")
            if f.stem != "_default"
        ]

    def clear_cache(self):
        """
        Clear the configuration cache.

        Useful when configuration files are updated at runtime.
        """
        self._cache.clear()

    # -------------------------------------------------------------------------
    # PRIVATE METHODS
    # -------------------------------------------------------------------------

    def _load_yaml(self, relative_path: str, default: Optional[Dict] = None) -> Dict:
        """
        Load YAML file with environment variable substitution.

        Supports syntax: ${VAR_NAME:-default_value}

        Args:
            relative_path: Path relative to config_dir
            default: Default value to return if file doesn't exist

        Returns:
            Parsed YAML as dictionary

        Raises:
            FileNotFoundError: If file doesn't exist and no default provided
        """
        file_path = self.config_dir / relative_path

        if not file_path.exists():
            if default is not None:
                return default
            raise FileNotFoundError(f"Config file not found: {file_path}")

        # Read file content
        with open(file_path, 'r') as f:
            content = f.read()

        # Substitute environment variables
        content = self._replace_env_vars(content)

        # Parse YAML
        return yaml.safe_load(content) or {}

    def _replace_env_vars(self, content: str) -> str:
        """
        Replace environment variables in config content.

        Syntax: ${VAR_NAME:-default_value}

        Examples:
            ${ANTHROPIC_API_KEY} → Value from environment or empty
            ${DB_HOST:-localhost} → Value from environment or "localhost"
            ${DB_PORT:-5432} → Value from environment or "5432"

        Args:
            content: YAML content as string

        Returns:
            Content with environment variables substituted
        """
        # Pattern: ${VAR_NAME} or ${VAR_NAME:-default}
        pattern = r'\$\{([^}:]+)(?::-(.*?))?\}'

        def replace(match):
            var_name = match.group(1)
            default_value = match.group(2) or ""
            return os.environ.get(var_name, default_value)

        return re.sub(pattern, replace, content)

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """
        Deep merge two dictionaries.

        Override values take precedence. Nested dicts are merged recursively.

        Args:
            base: Base dictionary
            override: Override dictionary (takes precedence)

        Returns:
            Merged dictionary

        Example:
            >>> base = {"a": 1, "b": {"c": 2, "d": 3}}
            >>> override = {"b": {"c": 20}, "e": 4}
            >>> result = _deep_merge(base, override)
            >>> print(result)
            {"a": 1, "b": {"c": 20, "d": 3}, "e": 4}
        """
        result = base.copy()

        for key, value in override.items():
            if (
                    key in result
                    and isinstance(result[key], dict)
                    and isinstance(value, dict)
            ):
                # Recursively merge nested dictionaries
                result[key] = self._deep_merge(result[key], value)
            else:
                # Override value
                result[key] = value

        return result

    def _validate_compatibility(
            self,
            config: Dict,
            country_code: str,
            tech_code: str
    ):
        """
        Validate that country supports the specified technology.

        Args:
            config: Merged configuration
            country_code: Country code
            tech_code: Technology code

        Raises:
            ValueError: If technology is not supported in the country
        """
        supported_techs = config.get("country", {}).get("supported_technologies", [])

        if tech_code not in supported_techs:
            raise ValueError(
                f"Technology '{tech_code}' is not supported in country '{country_code}'. "
                f"Supported technologies: {supported_techs}"
            )


# Example usage and testing
if __name__ == "__main__":
    # Create a ConfigLoader instance
    loader = ConfigLoader()

    print("=" * 60)
    print("ConfigLoader Demo")
    print("=" * 60)

    # 1. Load country configuration
    print("\n1. Load USA configuration:")
    usa_config = loader.load_country_config("USA")
    print(f"   Country: {usa_config['country']['name']}")
    print(f"   Discount Rate: {usa_config['country']['financial']['discount_rate']}")
    print(f"   Tax Rate: {usa_config['country']['financial']['corporate_tax_rate']}")

    # 2. Load technology configuration
    print("\n2. Load Solar PV configuration:")
    solar_config = loader.load_technology_config("solar_pv")
    print(f"   Technology: {solar_config['technology']['name']}")
    print(f"   CapEx: ${solar_config['technology']['financial']['capex_usd_per_kw']}/kW")
    print(f"   OpEx: ${solar_config['technology']['financial']['opex_usd_per_kw_year']}/kW/year")

    # 3. Load combined configuration
    print("\n3. Load USA + Solar PV combined configuration:")
    combined = loader.load_combination_config("USA", "solar_pv")
    print(f"   Country: {combined['country']['name']}")
    print(f"   Technology: {combined['technology']['name']}")
    print(f"   Discount Rate (from country): {combined['country']['financial']['discount_rate']}")
    print(f"   CapEx (from technology): ${combined['technology']['financial']['capex_usd_per_kw']}/kW")

    # 4. Get supported countries
    print("\n4. Supported countries:")
    countries = loader.get_supported_countries()
    print(f"   {', '.join(countries)}")

    # 5. Get supported technologies
    print("\n5. Supported technologies:")
    all_techs = loader.get_supported_technologies()
    print(f"   All: {', '.join(all_techs)}")

    usa_techs = loader.get_supported_technologies("USA")
    print(f"   USA: {', '.join(usa_techs)}")

    print("\n" + "=" * 60)
    print("✅ ConfigLoader working correctly!")
    print("=" * 60)