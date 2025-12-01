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
