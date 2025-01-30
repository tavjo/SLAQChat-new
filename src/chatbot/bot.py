# src/chatbot/bot.py

from langgraph import ToolNode, StateGraph


class Chatbot:
    def __init__(self):
        self.llm = load_llm()
        self.tool_node = self.create_tool()
        self.workflow = self.create_workflow()
        
    def create_tool(self):
        return ToolNode(name="Weather Tool", func=fetch_weather)
        
    def create_workflow(self):
        graph = StateGraph()
        graph.add_node(self.call_model, "start")
        graph.add_edge("start", "tool", condition=self.router)
        graph.add_edge("tool", "end")
        return graph.compile()
    def call_model(self, state):
        return self.llm.query(state.message)