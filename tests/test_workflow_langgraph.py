from langgraph.graph.state import CompiledStateGraph

from app.workflow import ProofPathWorkflow


def test_workflow_uses_compiled_langgraph_state_graph() -> None:
    workflow = ProofPathWorkflow()

    assert isinstance(workflow.graph, CompiledStateGraph)
