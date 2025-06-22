"""
Usage:
  python main.py <func>
  python main.py env
  python main.py simple_evals
  python main.py pydantic_evals
  python main.py evaluate_rules_from_json_files
Options:
  -h --help     Show this screen.
  --version     Show version.
"""

import json
import sys
import time
import traceback

from datetime import datetime
from datetime import timedelta

from docopt import docopt
from dotenv import load_dotenv

from pydantic import BaseModel

from src.os.env import Env
from src.io.fs import FS

# Inline Pydantic model and other classes for demonstration purposes

class Rule(BaseModel):
    name: str
    domain: str
    category: str
    description: str
    expression: str
    return_type: str

    def __repr__(self):
        return f"Rule(name={self.name}, description={self.description}, expression={self.expression})"


class RuleData(BaseModel):
    state: str
    county: str
    postal_code: int
    state_tax_rate: float
    county_tax_rate: float
    income: int


class Calculator:

    def today(self) -> str:
        """ Return today's date as a string in YYYY-MM-DD format. """
        return time.strftime("%Y-%m-%d")

    def next_week(self) -> str:
        """ Return the date one week from today as a string in YYYY-MM-DD format. """
        return (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")


def print_options(msg):
    print(msg)
    arguments = docopt(__doc__, version="1.0.0")
    print(arguments)


def check_env():
    load_dotenv(override=True)
    Env.log_standard_env_vars()
    print("check_env - username: {}".format(Env.username()))


def simple_evals():
    print("simple_evals")
    locals = {
        "state": "NC",
        "county": "Mecklenburg",
        "postal_code": "28036",
        "state_tax_rate": 0.07,
        "county_tax_rate": 0.005,
        "income": 100_000
    }
    expressions = [
        "(1 + 17) / 4.0",
        "income + 42",
        "income * state_tax_rate",
        "income * (state_tax_rate + county_tax_rate)",
        "int(income * (state_tax_rate + county_tax_rate))",
        "sum([1,2,3,income])",
        "max([12,0,13,9,0])",
        "hex(255)",
        "county[0:1].lower()",
        "'wealthy' if income > 1_000_000 else 'middle_class'",
        "'even' if income % 2 == 0 else 'odd'",
        "'even' if (income + 1) % 2 == 0 else 'odd'"
    ]
    print("locals:")
    print(json.dumps(locals, sort_keys=False, indent=2))

    for ex in expressions:
        try:
            #result = eval(ex, {"__builtins__": None}, data)
            result = eval(ex, {}, locals=locals)
            print(f"expression: {ex} => result: {result}")
        except Exception as excp:
            print(f"Error evaluating '{ex}': {excp}") 


def pydantic_evals():
    print("pydantic_evals")
    rule_data = RuleData(
        state="NC",
        county="Mecklenburg",
        postal_code=28036,
        state_tax_rate=0.07,
        county_tax_rate=0.005,
        income=100_000
    )
    c = Calculator()
    print("Calculator today:     {}".format(c.today()))
    print("Calculator next week: {}".format(c.next_week()))

    locals = {
        "data": rule_data,
        "calculator": c
    }
    expressions = [
        "float((1 + 17) / 4.0)",
        "int(data.income + 42)",
        "float(data.income * data.state_tax_rate)",
        "float(data.income * (data.state_tax_rate + data.county_tax_rate))",
        "int(data.income * (data.state_tax_rate + data.county_tax_rate))",
        "int(sum([1,2,3,data.income]))",
        "float([6.2,3.1,13.1,9.3,1.0])",
        "str(hex(255))",
        "str(data.county[0:1].lower())",
        "str('wealthy' if data.income > 1_000_000 else 'middle_class')",
        "str(calculator.today() if data.income > 1_000_000 else calculator.next_week())",
        "str('even' if data.income % 2 == 0 else 'odd')",
        "str('even' if (data.income + 1) % 2 == 0 else 'odd')"
    ]
    print("rule_data:")
    print(rule_data.model_dump_json(indent=2))

    for ex in expressions:
        try:
            result = eval(ex, {}, locals=locals)
            print(f"expression: {ex} => result: {result}")
        except Exception as excp:
            print(f"Error evaluating '{ex}': {excp}")

    create_rules_file(expressions) 
    FS.write_json(rule_data.model_dump(), "rules/rules_data.json", pretty=True, sort_keys=False, verbose=True)


def evaluate_rules_from_json_files():
    rules = FS.read_json("rules/rules.json")
    rule_data = FS.read_json("rules/rules_data.json")
    rule_data_obj = RuleData(**rule_data)

    c = Calculator()
    print("Calculator today:     {}".format(c.today()))
    print("Calculator next week: {}".format(c.next_week()))

    locals = {
        "data": rule_data_obj,
        "calculator": c
    }
    for rule_dict in rules:
        try:
            ex = rule_dict['expression']
            result = eval(ex, {}, locals=locals)
            print(f"expression: {ex} => result: {result}")
        except Exception as excp:
            print(f"Error evaluating '{ex}': {excp}")


def create_rules_file(expressions):
    rules = list()
    for idx, ex in enumerate(expressions):
        try:
            return_type = ex.split('(')[0].strip()
            rule = Rule(
                name="Rule_{}".format(idx + 1),
                domain="<some high-level domain>",
                category="<some lower-level name within the domain>",
                description=f"Evaluates the expression: {ex}",
                expression=ex,
                return_type=return_type
            )
            rules.append(rule.model_dump())
        except Exception as excp:
            print(f"Error creating rule for '{ex}': {excp}")
    FS.write_json(rules, "rules/rules.json", pretty=True, sort_keys=False, verbose=True)


if __name__ == "__main__":
    try:
        func = sys.argv[1].lower()
        if func == "env":
            check_env()
        elif func == "simple_evals":
            simple_evals()
        elif func == "pydantic_evals":
            pydantic_evals()
        elif func == "evaluate_rules_from_json_files":
            evaluate_rules_from_json_files()
        else:
            print_options("Error: invalid function: {}".format(func))
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
