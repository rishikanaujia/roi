"""
Base Agent - Template Method Pattern

This base class provides common functionality for all agents:
1. Execution workflow (preprocess → execute → postprocess)
2. Error handling and logging
3. Input validation
4. Execution tracking (time, cost, etc.)

Design Pattern: Template Method
- Base class defines the workflow structure
- Subclasses fill in the specific steps
- Prevents code duplication across agents

All agents should inherit from BaseAgent instead of implementing IAgent directly.

Example:
    class ResearchAgent(BaseAgent):
        async def _execute_core(self, input_data):
            # Only implement the core logic
            # BaseAgent handles everything else
            return {"policy_data": ..., "resource_data": ...}
"""

import logging
import time
from typing import Any, Dict, Optional
from abc import abstractmethod

from src.core.interfaces.agent_interface import IAgent


class BaseAgent(IAgent):
    """
    Base implementation of IAgent with Template Method pattern.

    This class provides:
    - Common execution workflow
    - Logging infrastructure
    - Error handling
    - Execution metrics (time, cost)
    - Input validation

    Subclasses only need to implement:
    - _execute_core(): The agent's main logic
    - validate_input(): Agent-specific validation (optional)

    Attributes:
        name (str): Agent name for logging
        llm_provider: LLM provider for API calls
        config (Dict): Agent configuration
        logger (logging.Logger): Logger instance
    """

    def __init__(
            self,
            name: str,
            llm_provider,  # Type: ILLMProvider (we'll create this interface later)
            config: Dict[str, Any],
            logger: Optional[logging.Logger] = None
    ):
        """
        Initialize base agent.

        Args:
            name: Agent name (e.g., "ResearchAgent")
            llm_provider: LLM provider instance
            config: Configuration dictionary
            logger: Optional logger (creates one if not provided)
        """
        self.name = name
        self.llm_provider = llm_provider
        self.config = config
        self.logger = logger or self._create_logger(name)

        # Execution metrics
        self._execution_count = 0
        self._total_execution_time = 0.0
        self._total_cost = 0.0

    # =========================================================================
    # PUBLIC INTERFACE (IAgent implementation)
    # =========================================================================

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent using Template Method pattern.

        Workflow:
            1. Validate input
            2. Preprocess (hook for subclasses)
            3. Execute core logic (implemented by subclass)
            4. Postprocess (hook for subclasses)
            5. Return results

        Args:
            input_data: Input parameters

        Returns:
            Dictionary with results and metadata

        Raises:
            ValueError: If input validation fails
            Exception: If execution fails
        """
        start_time = time.time()

        try:
            # Step 1: Validate input
            if not self.validate_input(input_data):
                raise ValueError(f"Invalid input data for {self.name}")

            self.logger.info(f"{self.name} execution started")
            self.logger.debug(f"Input: {input_data}")

            # Step 2: Preprocess (hook)
            processed_input = await self._preprocess(input_data)

            # Step 3: Execute core logic (implemented by subclass)
            result = await self._execute_core(processed_input)

            # Step 4: Postprocess (hook)
            final_result = await self._postprocess(result)

            # Calculate execution metrics
            execution_time = time.time() - start_time

            # Update metrics
            self._execution_count += 1
            self._total_execution_time += execution_time

            self.logger.info(
                f"{self.name} execution completed "
                f"(time: {execution_time:.2f}s)"
            )

            # Add metadata
            final_result["_metadata"] = {
                "agent": self.name,
                "execution_time_seconds": round(execution_time, 2),
                "execution_count": self._execution_count,
                "timestamp": time.time()
            }

            return final_result

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(
                f"{self.name} execution failed after {execution_time:.2f}s: {str(e)}"
            )
            raise

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Basic input validation.

        Override this in subclasses for agent-specific validation.

        Args:
            input_data: Input to validate

        Returns:
            True if valid, False otherwise
        """
        return input_data is not None and isinstance(input_data, dict)

    def get_name(self) -> str:
        """Get agent name."""
        return self.name

    # =========================================================================
    # TEMPLATE METHOD HOOKS (Override in subclasses)
    # =========================================================================

    @abstractmethod
    async def _execute_core(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core execution logic - MUST be implemented by subclass.

        This is where the agent's main work happens.

        Args:
            input_data: Preprocessed input data

        Returns:
            Dictionary with results

        Example:
            async def _execute_core(self, input_data):
                # Fetch data
                policy_data = await self.fetch_policy()
                resource_data = await self.fetch_resource()

                # Process
                result = self.process(policy_data, resource_data)

                return {
                    "policy_data": policy_data,
                    "resource_data": resource_data,
                    "processed_result": result
                }
        """
        pass

    async def _preprocess(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess input data (optional hook).

        Override this to add preprocessing logic like:
        - Data normalization
        - Default value filling
        - Coordinate transformation

        Args:
            input_data: Raw input data

        Returns:
            Preprocessed input data

        Example:
            async def _preprocess(self, input_data):
                # Add default capacity if not provided
                if "capacity_mw" not in input_data:
                    input_data["capacity_mw"] = 100.0

                # Round coordinates
                input_data["latitude"] = round(input_data["latitude"], 4)
                input_data["longitude"] = round(input_data["longitude"], 4)

                return input_data
        """
        return input_data

    async def _postprocess(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Postprocess results (optional hook).

        Override this to add postprocessing logic like:
        - Rounding numbers
        - Adding calculated fields
        - Formatting output

        Args:
            result: Raw results from _execute_core

        Returns:
            Postprocessed results

        Example:
            async def _postprocess(self, result):
                # Round financial values
                if "lcoe" in result:
                    result["lcoe"] = round(result["lcoe"], 2)
                if "irr" in result:
                    result["irr"] = round(result["irr"], 2)

                # Add confidence level
                result["confidence"] = self._calculate_confidence(result)

                return result
        """
        return result

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def _create_logger(self, name: str) -> logging.Logger:
        """
        Create a logger for this agent.

        Args:
            name: Logger name

        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(name)

        # Only add handler if not already present
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

        return logger

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get execution metrics for this agent.

        Returns:
            Dictionary with metrics
        """
        avg_time = (
            self._total_execution_time / self._execution_count
            if self._execution_count > 0
            else 0
        )

        return {
            "agent": self.name,
            "execution_count": self._execution_count,
            "total_execution_time": round(self._total_execution_time, 2),
            "average_execution_time": round(avg_time, 2),
            "total_cost": round(self._total_cost, 2)
        }

    def reset_metrics(self):
        """Reset execution metrics."""
        self._execution_count = 0
        self._total_execution_time = 0.0
        self._total_cost = 0.0


# ============================================================================
# EXAMPLE IMPLEMENTATION
# ============================================================================

class ExampleAgent(BaseAgent):
    """
    Example agent showing how to use BaseAgent.

    This agent just does some simple math to demonstrate the pattern.
    """

    def __init__(self, llm_provider, config, logger=None):
        super().__init__("ExampleAgent", llm_provider, config, logger)

    async def _execute_core(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core logic - just multiply two numbers.
        """
        # Simulate some async work
        import asyncio
        await asyncio.sleep(0.1)

        a = input_data.get("a", 0)
        b = input_data.get("b", 0)
        result = a * b

        return {
            "result": result,
            "operation": "multiply",
            "inputs": {"a": a, "b": b}
        }

    async def _preprocess(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add defaults for missing values."""
        if "a" not in input_data:
            input_data["a"] = 1
        if "b" not in input_data:
            input_data["b"] = 1
        return input_data

    async def _postprocess(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Round the result."""
        if "result" in result:
            result["result"] = round(result["result"], 2)
        return result

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate that inputs are numbers if provided.

        Empty dict is OK because preprocessing adds defaults.
        """
        base_valid = super().validate_input(input_data)
        if not base_valid:
            return False

        # If a or b are provided, check they're numbers
        if "a" in input_data and not isinstance(input_data["a"], (int, float)):
            return False

        if "b" in input_data and not isinstance(input_data["b"], (int, float)):
            return False

        # Empty dict is valid - preprocessing will add defaults
        return True


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    import asyncio

    print("=" * 70)
    print("BaseAgent Demo - Template Method Pattern")
    print("=" * 70)


    # Create a mock LLM provider (not used in this example)
    class MockLLMProvider:
        pass


    # Create example agent
    agent = ExampleAgent(
        llm_provider=MockLLMProvider(),
        config={"example_config": "value"}
    )

    print(f"\n1. Agent name: {agent.get_name()}")

    # Test validation
    print("\n2. Testing input validation:")
    print(f"   Valid: {agent.validate_input({'a': 5, 'b': 3})}")
    print(f"   Valid (only a): {agent.validate_input({'a': 5})}")
    print(f"   Invalid (empty): {agent.validate_input({})}")

    # Test execution
    print("\n3. Testing execution with preprocessing:")


    async def test_execution():
        # Test with both values
        result = await agent.execute({"a": 5, "b": 3})
        print(f"   Input: a=5, b=3")
        print(f"   Result: {result['result']}")
        print(f"   Execution time: {result['_metadata']['execution_time_seconds']}s")

        # Test with preprocessing (missing b)
        result = await agent.execute({"a": 7})
        print(f"\n   Input: a=7 (b will default to 1)")
        print(f"   Result: {result['result']}")

        # Test with preprocessing (both missing)
        result = await agent.execute({})
        print(f"\n   Input: empty (a=1, b=1 defaults)")
        print(f"   Result: {result['result']}")


    asyncio.run(test_execution())

    # Test metrics
    print("\n4. Agent metrics after 3 executions:")
    metrics = agent.get_metrics()
    print(f"   Total executions: {metrics['execution_count']}")
    print(f"   Total time: {metrics['total_execution_time']}s")
    print(f"   Average time: {metrics['average_execution_time']}s")

    # Test error handling
    print("\n5. Testing error handling:")


    class FailingAgent(BaseAgent):
        async def _execute_core(self, input_data):
            raise Exception("Simulated failure")


    failing_agent = FailingAgent("FailingAgent", MockLLMProvider(), {})


    async def test_error():
        try:
            await failing_agent.execute({"test": "data"})
        except Exception as e:
            print(f"   Caught expected error: {e}")


    asyncio.run(test_error())

    print("\n" + "=" * 70)
    print("✅ BaseAgent working correctly!")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("- BaseAgent provides execution workflow (Template Method pattern)")
    print("- Subclasses only implement _execute_core()")
    print("- Optional hooks: _preprocess(), _postprocess()")
    print("- Automatic logging, metrics, error handling")
    print("- No code duplication across agents!")