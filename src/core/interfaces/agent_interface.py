"""
Agent Interface - Following SOLID Principles

This interface defines the contract that ALL agents must follow.
It enables:
1. Polymorphism - Any agent can be used interchangeably
2. Testability - Easy to create mock agents for testing
3. Extensibility - New agents just implement this interface
4. Type Safety - Clear contract for what an agent must do

Design Patterns Used:
- Interface Segregation Principle (ISP): Small, focused interface
- Dependency Inversion Principle (DIP): Depend on abstraction, not concrete classes
- Template Method Pattern: Base implementation provided in BaseAgent

Example:
    class MyCustomAgent(IAgent):
        async def execute(self, input_data):
            # Custom logic here
            return {"result": "success"}

        def validate_input(self, input_data):
            return "latitude" in input_data

        def get_name(self):
            return "MyCustomAgent"
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class IAgent(ABC):
    """
    Abstract base interface for all agents in the ROI system.

    All agents (Research, Analysis, Peer Review, etc.) must implement this interface.
    This ensures consistency and allows agents to be used interchangeably.

    Attributes:
        None (interface only defines methods, not attributes)

    Methods:
        execute: Main entry point - executes the agent's task
        validate_input: Validates that input data is correct
        get_name: Returns the agent's name for logging/tracking
    """

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's primary task.

        This is the main entry point for the agent. It should:
        1. Validate input
        2. Perform the agent's core task
        3. Return results in a consistent format

        Args:
            input_data: Dictionary containing input parameters
                       Common keys:
                       - country: Country code (e.g., "USA")
                       - technology: Technology code (e.g., "solar_pv")
                       - latitude: Location latitude
                       - longitude: Location longitude
                       - Additional agent-specific parameters

        Returns:
            Dictionary containing results
            Should always include:
            - status: "success" or "error"
            - data: The actual results
            - metadata: Additional information (execution time, cost, etc.)

        Raises:
            ValueError: If input validation fails
            Exception: If execution fails

        Example:
            >>> agent = ResearchAgent(llm, config, "USA", "solar_pv")
            >>> input_data = {
            ...     "latitude": 31.99,
            ...     "longitude": -102.07,
            ...     "capacity_mw": 100
            ... }
            >>> result = await agent.execute(input_data)
            >>> print(result["status"])
            'success'
            >>> print(result["data"]["policy_data"])
            {'federal_itc': 30.0, ...}
        """
        pass

    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate that input data meets requirements.

        Each agent has different input requirements. This method
        checks that all required fields are present and valid.

        Args:
            input_data: Dictionary to validate

        Returns:
            True if input is valid, False otherwise

        Example:
            >>> agent = ResearchAgent(llm, config, "USA", "solar_pv")
            >>> valid_input = {"latitude": 31.99, "longitude": -102.07}
            >>> agent.validate_input(valid_input)
            True
            >>>
            >>> invalid_input = {"latitude": 31.99}  # Missing longitude
            >>> agent.validate_input(invalid_input)
            False
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """
        Get the agent's name.

        Used for logging, tracking, and debugging. Should be unique
        and descriptive.

        Returns:
            String name of the agent

        Example:
            >>> agent = ResearchAgent(llm, config, "USA", "solar_pv")
            >>> agent.get_name()
            'ResearchAgent'
        """
        pass


# Optional: Define common result structure for consistency
class AgentResult:
    """
    Standard result structure for agent execution.

    While not enforced by the interface, using this structure
    makes results consistent across all agents.
    """

    def __init__(
            self,
            status: str,
            data: Dict[str, Any],
            metadata: Dict[str, Any] = None
    ):
        """
        Initialize agent result.

        Args:
            status: "success" or "error"
            data: The actual results
            metadata: Additional information (execution time, cost, etc.)
        """
        self.status = status
        self.data = data
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "status": self.status,
            "data": self.data,
            "metadata": self.metadata
        }

    @classmethod
    def success(cls, data: Dict[str, Any], metadata: Dict[str, Any] = None):
        """Create a success result."""
        return cls("success", data, metadata)

    @classmethod
    def error(cls, error_message: str, metadata: Dict[str, Any] = None):
        """Create an error result."""
        return cls("error", {"error": error_message}, metadata)


# Example implementation (for testing)
class MockAgent(IAgent):
    """
    Mock agent for testing purposes.

    This is a simple implementation that shows how to implement IAgent.
    """

    def __init__(self, name: str = "MockAgent"):
        self.name = name

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute mock task - just returns input."""
        if not self.validate_input(input_data):
            raise ValueError("Invalid input data")

        return {
            "status": "success",
            "data": {
                "message": "Mock execution completed",
                "input_received": input_data
            },
            "metadata": {
                "agent": self.name
            }
        }

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate that input is a non-empty dictionary."""
        return input_data is not None and isinstance(input_data, dict) and len(input_data) > 0

    def get_name(self) -> str:
        """Return agent name."""
        return self.name


# Demo and testing
if __name__ == "__main__":
    import asyncio

    print("=" * 70)
    print("Agent Interface Demo")
    print("=" * 70)

    # Create a mock agent
    agent = MockAgent("TestAgent")

    print(f"\n1. Agent name: {agent.get_name()}")

    # Test validation
    print("\n2. Testing input validation:")
    valid_input = {"latitude": 31.99, "longitude": -102.07}
    print(f"   Valid input: {agent.validate_input(valid_input)}")

    invalid_input = {}
    print(f"   Invalid input (empty): {agent.validate_input(invalid_input)}")

    invalid_input = None
    print(f"   Invalid input (None): {agent.validate_input(invalid_input)}")

    # Test execution
    print("\n3. Testing execution:")


    async def test_execution():
        result = await agent.execute(valid_input)
        print(f"   Status: {result['status']}")
        print(f"   Message: {result['data']['message']}")
        print(f"   Agent: {result['metadata']['agent']}")


    asyncio.run(test_execution())

    # Test error handling
    print("\n4. Testing error handling:")


    async def test_error():
        try:
            result = await agent.execute({})
        except ValueError as e:
            print(f"   Caught expected error: {e}")


    asyncio.run(test_error())

    # Test AgentResult helper
    print("\n5. Testing AgentResult helper:")
    success_result = AgentResult.success(
        data={"lcoe": 45.2, "irr": 12.5},
        metadata={"execution_time": 2.5}
    )
    print(f"   Success result: {success_result.to_dict()}")

    error_result = AgentResult.error(
        error_message="Data source unavailable",
        metadata={"retry_count": 3}
    )
    print(f"   Error result: {error_result.to_dict()}")

    print("\n" + "=" * 70)
    print("✅ Agent Interface working correctly!")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("- All agents must implement execute(), validate_input(), get_name()")
    print("- execute() is async to support I/O operations")
    print("- AgentResult provides consistent result structure")
    print("- MockAgent shows minimal implementation")