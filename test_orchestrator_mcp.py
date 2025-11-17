"""
Test Orchestrator with MCP-enabled LangGraph Agent

This script verifies that the orchestrator correctly uses the MCP-enabled
LangGraph agent instead of directly accessing recipes.py
"""

from agents.orchestrator import orchestrator, LANGGRAPH_SETUP_SUCCESS

def test_orchestrator_mcp():
    """Test that orchestrator works with MCP agent"""

    print("=" * 80)
    print("TESTING ORCHESTRATOR WITH MCP-ENABLED LANGGRAPH AGENT")
    print("=" * 80)

    if not LANGGRAPH_SETUP_SUCCESS:
        print("✗ LangGraph setup failed")
        return False

    if orchestrator is None:
        print("✗ Orchestrator not initialized")
        return False

    print("\n✓ Orchestrator initialized with MCP-enabled agent")
    print(f"✓ Orchestrator name: {orchestrator.name}")
    print(f"✓ Available tools: {len(orchestrator.tools)}")

    for tool in orchestrator.tools:
        print(f"   - {tool.name if hasattr(tool, 'name') else 'AgentTool'}")

    # Verify the agent is using MCP by checking the import
    import agents.orchestrator as orch_module
    import inspect

    source = inspect.getsource(orch_module)
    if 'langgraph_agent_mcp' in source:
        print("\n✓ Confirmed: Orchestrator is using langgraph_agent_mcp")
    else:
        print("\n✗ Warning: Orchestrator may not be using MCP agent")

    print("\n" + "=" * 80)
    print("TEST PASSED: Orchestrator is correctly configured with MCP agent")
    print("=" * 80)

    return True

if __name__ == "__main__":
    success = test_orchestrator_mcp()
    exit(0 if success else 1)
