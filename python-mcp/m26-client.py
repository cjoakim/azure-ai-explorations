import asyncio
import json
import os
from fastmcp import Client, FastMCP

# HTTP server
# HTTP Client program for 'm26-server.py' in this directory
# Started with: fastmcp run m26-server.py --transport http --port 9001
client = Client("http://127.0.0.1:9001/mcp/")

async def main():
    async with client:
        print("Pinging the server:")
        print(await client.ping())
        
        print("List available operations on the server - tools, resources, prompts")
        tools = await client.list_tools()  # a list of <class 'mcp.types.Tool'>
        resources = await client.list_resources()
        prompts = await client.list_prompts()
        print("tools:\n{}".format(tools))
        print("resources:\n{}".format(resources))
        print("prompts:\n{}".format(prompts))

        print("Invoking miles_to_kilometers tool:")
        result = await client.call_tool(
            "miles_to_kilometers",
            {"miles": "26.2"})
        print(str(type(result)))  # a list of <class 'mcp.types.TextContent'>
        print(result)

        print("Invoking calculate_pace_per_mile tool:")
        result = await client.call_tool(
            "calculate_pace_per_mile",
            {"miles": "26.2", "hhmmss": "3:47:30"})
        print(str(type(result)))  # a list of <class 'mcp.types.TextContent'>
        print(result)

        print("Invoking meta tool:")
        result = await client.call_tool(
            "meta", {})
        print(str(type(result)))  # a list of <class 'mcp.types.TextContent'>
        print(result)


if __name__ == "__main__":
    print("starting client {}".format(os.path.basename(__file__)))
    asyncio.run(main())
