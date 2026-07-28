import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from mcp_server.tools.flight_calculator import calculate_flight_time
from mcp_server.tools.roi_calculator import calculate_roi
from mcp_server.tools.compliance_checker import check_compliance
from mcp_server.tools.drone_recommender import recommend_drone

class MCPServer:
    """
    Model Context Protocol (MCP) Server exposing drone calculation & decision tools.
    """
    def __init__(self, name: str = "drone-intelligence-mcp"):
        self.name = name
        self.tools = {
            "flight_time_calculator": calculate_flight_time,
            "roi_calculator": calculate_roi,
            "compliance_checker": check_compliance,
            "drone_recommender": recommend_drone,
        }

    def list_tools(self):
        return [
            {
                "name": name,
                "description": func.__doc__.strip() if func.__doc__ else name,
            }
            for name, func in self.tools.items()
        ]

    def call_tool(self, tool_name: str, **kwargs):
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found on MCP server '{self.name}'.")
        return self.tools[tool_name](**kwargs)

if __name__ == "__main__":
    server = MCPServer()
    print(f"MCP Server '{server.name}' active with tools:")
    for t in server.list_tools():
        print(f"  - {t['name']}: {t['description']}")
