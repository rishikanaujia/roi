"""
Base Policy Handler - Foundation for All Policy Handlers

NOW WITH RESEARCH CONTEXT LOADING!

This base class provides:
- Research context loading from JSON
- Logging setup
- Common policy handling methods
- Country-specific research data integration
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class BasePolicyHandler(ABC):
    """
    Base policy handler with research context loading.

    All country-specific policy handlers inherit from this class.
    Automatically loads market research, recent policies, trends, etc.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize handler with research context loading.

        Args:
            config: Configuration dictionary with country info
        """
        self.config = config
        self.country_code = config.get('country', {}).get('code', '')
        self.country_name = config.get('country', {}).get('name', '')

        # Create logger
        self.logger = self._create_logger()

        # Load research context from JSON
        self.research_context = self._load_research_context()

        if self.research_context:
            last_updated = self.research_context.get('last_updated', 'unknown')
            self.logger.info(
                f"✅ Loaded research context for {self.country_name} "
                f"(last updated: {last_updated})"
            )
        else:
            self.logger.warning(
                f"⚠️  No research context available for {self.country_code}"
            )

    def _load_research_context(self) -> Optional[Dict[str, Any]]:
        """
        Load country research context from JSON file.

        Loads market overview, recent policies, trends, challenges,
        opportunities, and source URLs for the country.

        Returns:
            Complete research context dict or None if not available
        """
        try:
            # Construct path to research data file
            # From: src/agents/research/policy_handlers/base_policy_handler.py
            # To:   src/data/country_research.json
            current_file = Path(__file__)
            research_file = current_file.parent.parent.parent.parent / "data" / "country_research.json"

            self.logger.debug(f"Looking for research file at: {research_file}")

            if not research_file.exists():
                self.logger.debug(f"Research file not found: {research_file}")
                return None

            # Load JSON file
            with open(research_file, 'r', encoding='utf-8') as f:
                research_data = json.load(f)

            # Find matching country by code
            for country_data in research_data:
                if country_data.get('country_code') == self.country_code:
                    self.logger.debug(
                        f"Found research context for {self.country_code}: "
                        f"{len(country_data.get('research', {}))} sections"
                    )
                    return country_data

            self.logger.debug(f"No research data found for country: {self.country_code}")
            return None

        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in research file: {str(e)}")
            return None

        except Exception as e:
            self.logger.warning(f"Failed to load research context: {str(e)}")
            return None

    def get_policy_data(self) -> Dict[str, Any]:
        """
        Get policy data with research context.

        This method provides base policy data structure.
        Subclasses should override this and add country-specific details.

        Returns:
            Policy data dict with optional research context
        """
        policy_data = {
            "country": self.country_code,
            "country_name": self.country_name,
            "confidence": "medium"
        }

        # Add research context if available
        if self.research_context:
            policy_data['research_context'] = self.research_context.get('research', {})
            policy_data['research_last_updated'] = self.research_context.get('last_updated')

            self.logger.debug(
                f"Including research context: "
                f"{len(policy_data['research_context'])} data sections"
            )

        return policy_data

    @abstractmethod
    async def fetch_policy(self, technology: str, **kwargs) -> Dict[str, Any]:
        """
        Fetch policy data for specific technology.

        This method must be implemented by subclasses.

        Args:
            technology: Technology type (solar_pv, onshore_wind, etc.)
            **kwargs: Additional parameters

        Returns:
            Complete policy data including research context
        """
        pass

    def get_country_code(self) -> str:
        """Get country code."""
        return self.country_code

    def _create_logger(self) -> logging.Logger:
        """
        Create logger instance.

        Returns:
            Configured logger
        """
        logger = logging.getLogger(f"PolicyHandler-{self.country_code}")

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

        return logger

    def _format_currency(
            self,
            amount: float,
            currency: str = "USD",
            decimals: int = 2
    ) -> str:
        """
        Format currency amount.

        Args:
            amount: Amount to format
            currency: Currency code (USD, EUR, INR)
            decimals: Number of decimal places

        Returns:
            Formatted currency string
        """
        symbols = {
            "USD": "$",
            "EUR": "€",
            "INR": "₹",
            "GBP": "£"
        }

        symbol = symbols.get(currency, currency)
        return f"{symbol}{amount:,.{decimals}f}"

    def _calculate_effective_rate(
            self,
            base_rate: float,
            incentive: float,
            incentive_type: str = "absolute"
    ) -> float:
        """
        Calculate effective rate after incentives.

        Args:
            base_rate: Base rate or LCOE
            incentive: Incentive amount
            incentive_type: "absolute" or "percentage"

        Returns:
            Effective rate after incentives
        """
        if incentive_type == "absolute":
            return base_rate - incentive
        elif incentive_type == "percentage":
            return base_rate * (1 - incentive / 100)
        else:
            return base_rate