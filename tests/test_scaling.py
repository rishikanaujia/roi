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
