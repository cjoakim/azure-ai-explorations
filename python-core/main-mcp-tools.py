"""
Usage:
  Generate and deploy config files for MCP desktop tools
  such as Claude Desktop.
  python main-mcp-tools.py generate_mcp_servers_config
  python main-mcp-tools.py generate_deploy_claude_config
  python main-mcp-tools.py generate_deploy_vsc_config
Options:
  -h --help     Show this screen.
  --version     Show version.
"""

import json
import sys
import os
import traceback

import duckdb

from docopt import docopt
from dotenv import load_dotenv

from src.io.fs import FS
from src.util.template import Template


def print_options(msg) -> None:
    print(msg)
    arguments = docopt(__doc__, version="1.0.0")
    print(arguments)

def mcp_servers_config_filename() -> str:
    return "config/mcp_servers.json"

def read_mcp_servers_config() -> list[dict]:
    return FS.read_json(mcp_servers_config_filename())

def claude_config_filename() -> str:
    dir = os.getenv("CLAUDE_DESKTOP_CONFIG_DIR", None)
    file = os.getenv("CLAUDE_DESKTOP_CONFIG_DIR", "claude_desktop_config.json")
    return "{}/{}".format(dir, file)

def generate_mcp_servers_config() -> None:
    """
    Create a MCP Server Definitions file which will be used in 
    the various config-generation methods in this script - 
    such as for Claude, VSC, and other tools.
    NOTE: The generated file should be git-ignored!
    """
    servers = list()
    # TODO - evolve these dict values as necessary
    cosmos_airports = dict()
    cosmos_airports["name"] = "Cosmos DB Airports"
    cosmos_airports["command"] = "node"
    cosmos_airports["command_args"] = "/Users/cjoakim/github/azure-ai-explorations/mcp/microsoft/azure-cosmos-mcp-server-samples/javascript/dist/index.js"
    cosmos_airports["active"] = True
    env = dict()
    env["cosmosdb-nosql-uri"] = os.getenv("AZURE_COSMOSDB_NOSQL_URI", None)
    env["cosmosdb-nosql-key"] = os.getenv("AZURE_COSMOSDB_NOSQL_KEY", None)
    cosmos_airports["env"] = env  # json.dumps(env, sort_keys=False, indent=2)
    servers.append(cosmos_airports)

    FS.write_json(servers, mcp_servers_config_filename())

def generate_deploy_claude_config() -> None:
    outfile = claude_config_filename()
    print("Claude config filename: {}".format(outfile))
    values = dict()
    values["mcp_servers"] = read_mcp_servers_config()
    t = Template.get_template(os.getcwd(), "claude-desktop-config.txt")
    jstr = Template.render(t, values)
    print(jstr)

def generate_deploy_vsc_config() -> None:
    print('TODO: implement for VSC similarly for Claude config')


if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            print_options("Error: no CLI args provided")
        else:
            func = sys.argv[1].lower()
            if func == "generate_mcp_servers_config":
                generate_mcp_servers_config()
            elif func == "generate_deploy_claude_config":
                generate_deploy_claude_config()
            elif func == "generate_deploy_vsc_config":
                generate_deploy_vsc_config()
            else:
                print_options("Error: invalid function: {}".format(func))
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
