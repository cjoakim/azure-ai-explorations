import json
import os
from typing import Any
import m26

from fastmcp import FastMCP

# Note, this is based on the sample file from Anthropic found here:
# https://github.com/modelcontextprotocol/quickstart-resources/blob/main/weather-server-python/weather.py

# m26 is my pypi package for running/swimming/cycling calculations:
# https://pypi.org/project/m26/


# Initialize FastMCP server
mcp = FastMCP("m26")


@mcp.tool()
def calculate_pace_per_mile(miles: str, hhmmss: str) -> str:
    """
    Calculate the pace-per-mile (PPM) for the given distance in miles
    and elapsed time in the format '3:47:30' (hours:minutes:seconds).
    """
    ppm = "Unknown"
    try:
        print("calculate_pace_per_mile - miles: {} hhmmss: {}".format(miles, hhmmss))
        d = m26.Distance(float(miles))
        t = m26.ElapsedTime(hhmmss)
        s = m26.Speed(d, t)
        ppm = s.pace_per_mile()
    except Exception as e:
        return f"Error calculating pace: {e}"
    return f"""
Miles: {miles} miles
HHMMSS: {hhmmss}
Pace Per Mile: {ppm}
"""


@mcp.tool()
def miles_to_kilometers(miles: str) -> str:
    """
    Convert the given distance in miles to kilometers.
    """
    km = "Unknown"
    try:
        print("miles_to_kilometers - miles: {}".format(miles))
        d = m26.Distance(float(miles))
        km = d.as_kilometers()
    except Exception as e:
        return f"Error calculating pace: {e}"
    return f"""
Miles: {miles} miles
Kilometers: {km}
"""

# fastmcp dev m26-server.py
# fastmcp run m26-server.py
# FASTMCP_PORT
if __name__ == "__main__":
    print("starting {}".format(os.path.basename(__file__)))
    mcp.run(transport="stdio")  # stdio is the default
    #mcp.run(transport="http", host="127.0.0.1", port=8888, path="/m26")


# $ fastmcp dev m26-server.py
# Starting MCP inspector...
# ⚙️ Proxy server listening on 127.0.0.1:6277
# 🔑 Session token: 27404ae2005d29d178f7ce06c62752165714c72ef4f9a91d6adccb5facf3e8e7
# Use this token to authenticate requests or set DANGEROUSLY_OMIT_AUTH=true to disable auth

# 🔗 Open inspector with token pre-filled:
#    http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=27404ae2005d29d178f7ce06c62752165714c72ef4f9a91d6adccb5facf3e8e7
#    (Auto-open is disabled when authentication is enabled)

# 🔍 MCP Inspector is up and running at http://127.0.0.1:6274