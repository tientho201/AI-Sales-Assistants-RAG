"""
LangGraph Workflow orchestrator.
Builds the StateGraph representing the Multi-Agent Sales Copilot conversational flow.
"""
from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.requirement_agent import requirement_extraction_agent
from app.agents.memory_agent import memory_agent
from app.agents.clarification_agent import clarification_agent
from app.agents.hybrid_retriever_agent import hybrid_retriever_agent
from app.agents.recommendation_agent import recommendation_agent
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Node functions
def extract_requirements_node(state: AgentState) -> Dict[str, Any]:
    """
    Step 1: Extract requirements from user message.
    """
    logger.info("LangGraph Node: extract_requirements_node")
    newly_extracted = requirement_extraction_agent.run(state["user_message"])
    return {"newly_extracted": newly_extracted}

def memory_sync_node(state: AgentState) -> Dict[str, Any]:
    """
    Step 2: Sync and merge requirements with previous conversation history in DB.
    """
    logger.info("LangGraph Node: memory_sync_node")
    merged_requirements = memory_agent.run(
        session_id=state["session_id"],
        newly_extracted=state["newly_extracted"]
    )
    return {"current_requirements": merged_requirements}

def check_clarification_node(state: AgentState) -> Dict[str, Any]:
    """
    Step 3: Check if clarification is needed for missing critical info.
    """
    logger.info("LangGraph Node: check_clarification_node")
    needed, message = clarification_agent.run(
        current_requirements=state["current_requirements"],
        user_message=state["user_message"]
    )
    
    if needed:
        return {
            "clarification_needed": True,
            "clarification_message": message,
            "assistant_response": message,
            "recommendations": []
        }
        
    return {
        "clarification_needed": False,
        "clarification_message": None
    }

def retrieve_products_node(state: AgentState) -> Dict[str, Any]:
    """
    Step 4: Query Qdrant and Neo4j and combine results.
    """
    logger.info("LangGraph Node: retrieve_products_node")
    retrieved = hybrid_retriever_agent.run(state["current_requirements"])
    return {"retrieved_products": retrieved}

def recommend_products_node(state: AgentState) -> Dict[str, Any]:
    """
    Step 5: Write beautiful, contextual Vietnamese recommendation response.
    """
    logger.info("LangGraph Node: recommend_products_node")
    pitch = recommendation_agent.run(
        retrieved_products=state["retrieved_products"],
        current_requirements=state["current_requirements"]
    )
    return {
        "assistant_response": pitch,
        "recommendations": state["retrieved_products"]
    }

# Conditional edge routing
def route_after_clarification(state: AgentState) -> str:
    """
    Routes to Recommendation if info is sufficient, otherwise ends conversation with clarification question.
    """
    if state.get("clarification_needed", False):
        logger.info("LangGraph routing: CLARIFICATION_NEEDED -> END")
        return "end"
    else:
        logger.info("LangGraph routing: INFO_SUFFICIENT -> RETRIEVE_PRODUCTS")
        return "retrieve"

# Define the StateGraph structure
workflow = StateGraph(AgentState)

# Add Node definitions
workflow.add_node("extract_reqs", extract_requirements_node)
workflow.add_node("memory_sync", memory_sync_node)
workflow.add_node("check_clarification", check_clarification_node)
workflow.add_node("retrieve_products", retrieve_products_node)
workflow.add_node("recommend", recommend_products_node)

# Set Graph workflow edges
workflow.set_entry_point("extract_reqs")
workflow.add_edge("extract_reqs", "memory_sync")
workflow.add_edge("memory_sync", "check_clarification")

# Add conditional branch
workflow.add_conditional_edges(
    "check_clarification",
    route_after_clarification,
    {
        "end": END,
        "retrieve": "retrieve_products"
    }
)

workflow.add_edge("retrieve_products", "recommend")
workflow.add_edge("recommend", END)

# Compile into runnable application graph
sales_copilot_graph = workflow.compile()
