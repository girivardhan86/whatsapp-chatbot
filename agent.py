from langgraph.graph import StateGraph

workflow = StateGraph(dict)

def chatbot_node(state):

    query = state["query"]

    return {
        "response": "Hello from AI Agent"
    }

workflow.add_node("chatbot", chatbot_node)

workflow.set_entry_point("chatbot")

graph = workflow.compile()