"""
Usage:
    CLI app for Azure AI Search.
    -
    python main-swagger.py <func>
    python main-swagger.py parse <infile>
"""

import json
import os
import random
import sys
import traceback

from docopt import docopt
from dotenv import load_dotenv

from src.io.fs import FS


def print_options(msg):
    print(msg)
    arguments = docopt(__doc__, version="1.0.0")
    print(arguments)


def parse(infile="../data/swagger/swagger.json"):
    print("reading swagger file: {}".format(infile))
    data = FS.read_json(infile)
    md_lines = list()
    print("data keys: {}".format(sorted(data.keys())))
    # data keys: ['components', 'info', 'openapi', 'paths', 'security', 'servers']
    schemas = data["components"]["schemas"]
    schema_names = sorted(schemas.keys())

    md_lines.append("# Swagger Analysis")
    md_lines.append("")

    md_lines.append("## Schema List")
    md_lines.append("")
    for schema_idx, schema_name in enumerate(schema_names):
        md_lines.append("- {} {}".format(schema_idx + 1, schema_name))

    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")

    md_lines.append("## Schemas Of Interest")
    md_lines.append("")
    for schema_name in schema_names:
        if schema_is_of_interest(schema_name):
            md_lines.append("### {}".format(schema_name))
            md_lines.append("")
            schema = schemas[schema_name]
            md_lines.append("```")
            md_lines.append(json.dumps(schema, indent=2))
            md_lines.append("```")
            md_lines.append("")

    md_lines.append("")
    FS.write_lines(md_lines, "tmp/swaggger.md")


def schema_is_of_interest(schema_name) -> bool:
    if schema_name.startswith("Question"):
        return True
    if schema_name.startswith("Answer"):
        return True
    
    if schema_name == "BountyResponseModel":
        return True
    if schema_name == "CommunitySummaryResponseModel":
        return True
    if schema_name == "MentionedUserGroupResponseModel":
        return True
    if schema_name == "MentionedUserResponseModel":
        return True
    if schema_name == "SearchResultModel":
        return True
    if schema_name == "TagSummaryResponseModel":
        return True
    if schema_name == "UserSummaryResponseModel":
        return True
    return False


if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            print_options("Error: no CLI args provided")
        else:
            func = sys.argv[1].lower()
            print("=== CLI function: {}".format(func))

            if func == "parse":
                parse()
            else:
                print_options("Error: invalid function: {}".format(func))
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
