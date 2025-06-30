"""
Usage:
  python main-merge.py <func>
  python main-merge.py merge
"""

import datetime
import sys
import os
import traceback

from docopt import docopt
from dotenv import load_dotenv

from src.io.fs import FS


def print_options(msg):
    print(msg)
    arguments = docopt(__doc__, version="1.0.0")
    print(arguments)


def merge():
    gls_lines = FS.read_lines("tmp/gls.txt")
    ai_dict, core_dict = dict(), dict()

    # Collect file inventories
    for line in gls_lines:
        line = line.strip()
        if line.startswith("python-ai/"):
            filename = line[10:]
            ai_dict[filename] = read_file(line)
        if line.startswith("python-core/"):
            filename = line[12:]
            core_dict[filename] = read_file(line)

    FS.write_json(ai_dict, "tmp/gls-ai.json")
    FS.write_json(core_dict, "tmp/gls-core.json")

    # Check for diffs for merging python-ai into python-core
    for key in sorted(ai_dict.keys()):
        if key in core_dict.keys():
            ai_size = ai_dict[key]
            core_size = core_dict[key]
            if (ai_size == core_size):
                pass
                #print("Same size: {} {}".format(ai_size, key))
            else:
                if ("tests" in key):
                    pass
                else:
                    print("Diff size - ai: {} core: {} file: {}".format(
                        ai_size, core_size, key))
                    
                    ai_path = "/Users/cjoakim/github/azure-ai-explorations/python-ai/{}".format(key)
                    core_path = "/Users/cjoakim/github/azure-ai-explorations/python-core/{}".format(key)
                    ai_time = os.path.getmtime(ai_path) 
                    core_time = os.path.getmtime(core_path)
                    ai_ts = datetime.datetime.fromtimestamp(ai_time)
                    core_ts = datetime.datetime.fromtimestamp(core_time)

                    print("ai_time:   {} size: {}".format(ai_ts, ai_size))
                    print("core_time: {} size: {}".format(core_ts, core_size))
        else:
            pass
            #print("Not in core: {}".format(key))



def read_file(gls_filename):
    try:
        # gls_filename is a value like 'python-ai/src/util/counter.py'
        fq_filename = "/Users/cjoakim/github/azure-ai-explorations/{}".format(gls_filename)
        lines = FS.read_lines(fq_filename)
        return len(lines)
    except Exception as e:
        print("unable to read file: {}".format(fq_filename))
        return -1


if __name__ == "__main__":
    try:
        load_dotenv(override=True)
        if len(sys.argv) < 2:
            print_options("Error: no CLI args provided")
        else:
            func = sys.argv[1].lower()
            if func == "merge":
                merge()
            else:
                print_options("Error: invalid function: {}".format(func))
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
