"""Simple conversational graph using MessagesState.

A minimal chatbot graph: START -> chatbot -> END.
Uses LangGraph's built-in MessagesState for conversation history.
"""

from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, StateGraph

model = ChatOpenAI()


def chatbot(state: MessagesState) -> dict[str, list[object]]:
    """Invoke the LLM with the current conversation history."""
    response = model.invoke(state.messages)
    return {"messages": [response]}


builder = StateGraph(MessagesState)
builder.add_node("chatbot", chatbot)

builder.set_entry_point("chatbot")
builder.set_finish_point("chatbot")

graph = builder.compile()
