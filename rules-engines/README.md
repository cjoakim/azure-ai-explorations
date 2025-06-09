# rules-explorations

Exploratory repo for various rules engines.

## Directory Structure of this repo

```
├── dotnet
│   └── rules_engine    Implementation with C# and the microsoft/RulesEngine NuGet package
└── python
    └── eval_engine     Implementation with the built-in Python "eval()" statement
```

---

## Microsoft C# RulesEngine

- NuGet library https://www.nuget.org/packages/RulesEngine 
- GitHub repo: https://github.com/microsoft/RulesEngine 
  - Supported by several developers
  - Used in several small projects
  - But is it actually used in any Microsoft products?
- The Rules can be expressed in code or in JSON
- The Rules can be collected into a Workflow of several rules
- Each rule invocation returns simply a boolean result
- Rule syntax is quirky, such as:

```
This was the expected syntax per blogs:
  input1.temperature >= 220

But this was the actual syntax I had to use.
  Convert.ToInt32(input1.temperature) >= 220
```

### Simple Dotnet Console App 

```
$ cd dotnet/rules_engine

$ dotnet --version
9.0.300

$ dotnet compile

$ dotnet run rule_examples1   (enter values for Temperature and US State when prompted)

run function: rule_examples1
Temperature:
233
US State Abbreviation:
NC

Input1:
{
  "temperature": "233",
  "state": "NC"
}

Rule - TemperatureIsBoiling, IsSuccess - True, Ex:
ActionResult.Output -
Rule - StateIsNC, IsSuccess - True, Ex:
ActionResult.Output - NC
{
  "TemperatureIsBoiling": true,
  "StateIsNC": true
}
```

---

## Python eval()

- The **eval()** method is a built-in function
  - See https://docs.python.org/3/library/functions.html#eval
  - Therefore it has no dependencies and is very portable 
    - To python web apps, console apps, MCP servers, Jupyter notebooks, etc
- The eval() function more easily gives you the expressive power of Python
- eval() return types are not limited to booleans like the above C# RulesEngine package
  - strings, ints, floats, arrays, etc may be returned; not just booleans
- eval() allows you to invoke built-in Python functions
- eval() also allows you to invoke methds on passed-in input objects & data
- I've used this eval() approach before in a US Government app, though with Ruby and Rails
- The eval statements can be wrappered into JSON structures/objects
  - Persist/query/filter them in databases such as Cosmos DB
  - Vector search is possible based on rule descriptions, names, domains, categories, etc
  - Leverage their descriptions and other attributes in SK agentic plugins
- Pydantic can be leveraged for sane typing
- The eval expressions can optionally be wrappered in a method like str() or int()
  - This provides more clarity on exactly what datatype is returned 

### Simple Python Console App

```
$ cd dotnet/eval__engine

$ ./venv.sh                   # create and populate the python virtual environment

$ source venv/bin/activate    # activate the venv

$ python --version
Python 3.13.3

$ python main.py --help
Usage:
  python main.py <func>
  python main.py env
  python main.py simple_evals
  python main.py pydantic_evals
  python main.py evaluate_rules_from_json_files

$ python main.py evaluate_rules_from_json_files 
```

### The data

The data passed into the eval expressions is this:

```
locals = {
    "data": rule_data,
    "calculator": c
}

Where "c" is an instance of class Calculator, with methods 'today()' and 'next_week()'.
These can be invoked in the eval expressions.

Where "rule_data" is a dict like this:

{
  "state": "NC",
  "county": "Mecklenburg",
  "postal_code": 28036,
  "state_tax_rate": 0.07,
  "county_tax_rate": 0.005,
  "income": 100000
}
```

### The Rules

Example alpha-version of the Rules look like the following.

More pertinent attribute values can be created, 
but the current **expression** values are working and can
be passed into a Python **eval()** statement to return a result.

```
[
  {
    "name": "Rule_1",
    "domain": "<some high-level domain>",
    "category": "<some lower-level name within the domain>",
    "description": "Evaluates the expression: float((1 + 17) / 4.0)",
    "expression": "float((1 + 17) / 4.0)",
    "return_type": "float"
  },
  {
    "name": "Rule_2",
    "domain": "<some high-level domain>",
    "category": "<some lower-level name within the domain>",
    "description": "Evaluates the expression: int(data.income + 42)",
    "expression": "int(data.income + 42)",
    "return_type": "int"
  },
  {
    "name": "Rule_3",
    "domain": "<some high-level domain>",
    "category": "<some lower-level name within the domain>",
    "description": "Evaluates the expression: float(data.income * data.state_tax_rate)",
    "expression": "float(data.income * data.state_tax_rate)",
    "return_type": "float"
  },
  {
    "name": "Rule_4",
    "domain": "<some high-level domain>",
    "category": "<some lower-level name within the domain>",
    "description": "Evaluates the expression: float(data.income * (data.state_tax_rate + data.county_tax_rate))",
    "expression": "float(data.income * (data.state_tax_rate + data.county_tax_rate))",
    "return_type": "float"
  },
  {
    "name": "Rule_5",
    "domain": "<some high-level domain>",
    "category": "<some lower-level name within the domain>",
    "description": "Evaluates the expression: int(data.income * (data.state_tax_rate + data.county_tax_rate))",
    "expression": "int(data.income * (data.state_tax_rate + data.county_tax_rate))",
    "return_type": "int"
  },
  {
    "name": "Rule_6",
    "domain": "<some high-level domain>",
    "category": "<some lower-level name within the domain>",
    "description": "Evaluates the expression: int(sum([1,2,3,data.income]))",
    "expression": "int(sum([1,2,3,data.income]))",
    "return_type": "int"
  },
  {
    "name": "Rule_7",
    "domain": "<some high-level domain>",
    "category": "<some lower-level name within the domain>",
    "description": "Evaluates the expression: float([6.2,3.1,13.1,9.3,1.0])",
    "expression": "float([6.2,3.1,13.1,9.3,1.0])",
    "return_type": "float"
  },
  {
    "name": "Rule_8",
    "domain": "<some high-level domain>",
    "category": "<some lower-level name within the domain>",
    "description": "Evaluates the expression: str(hex(255))",
    "expression": "str(hex(255))",
    "return_type": "str"
  },
  {
    "name": "Rule_9",
    "domain": "<some high-level domain>",
    "category": "<some lower-level name within the domain>",
    "description": "Evaluates the expression: str(data.county[0:1].lower())",
    "expression": "str(data.county[0:1].lower())",
    "return_type": "str"
  },
  {
    "name": "Rule_10",
    "domain": "<some high-level domain>",
    "category": "<some lower-level name within the domain>",
    "description": "Evaluates the expression: str('wealthy' if data.income > 1_000_000 else 'middle_class')",
    "expression": "str('wealthy' if data.income > 1_000_000 else 'middle_class')",
    "return_type": "str"
  },
  {
    "name": "Rule_11",
    "domain": "<some high-level domain>",
    "category": "<some lower-level name within the domain>",
    "description": "Evaluates the expression: str(calculator.today() if data.income > 1_000_000 else calculator.next_week())",
    "expression": "str(calculator.today() if data.income > 1_000_000 else calculator.next_week())",
    "return_type": "str"
  },
  {
    "name": "Rule_12",
    "domain": "<some high-level domain>",
    "category": "<some lower-level name within the domain>",
    "description": "Evaluates the expression: str('even' if data.income % 2 == 0 else 'odd')",
    "expression": "str('even' if data.income % 2 == 0 else 'odd')",
    "return_type": "str"
  },
  {
    "name": "Rule_13",
    "domain": "<some high-level domain>",
    "category": "<some lower-level name within the domain>",
    "description": "Evaluates the expression: str('even' if (data.income + 1) % 2 == 0 else 'odd')",
    "expression": "str('even' if (data.income + 1) % 2 == 0 else 'odd')",
    "return_type": "str"
  }
]
```

### The results, using the above data passed into the rules

The primitive output shows the expression: => and result:

```
$ python main.py evaluate_rules_from_json_files

Calculator today:     2025-06-06
Calculator next week: 2025-06-13

expression: float((1 + 17) / 4.0) => result: 4.5
expression: int(data.income + 42) => result: 100042
expression: float(data.income * data.state_tax_rate) => result: 7000.000000000001
expression: float(data.income * (data.state_tax_rate + data.county_tax_rate)) => result: 7500.000000000001
expression: int(data.income * (data.state_tax_rate + data.county_tax_rate)) => result: 7500
expression: int(sum([1,2,3,data.income])) => result: 100006
Error evaluating 'float([6.2,3.1,13.1,9.3,1.0])': float() argument must be a string or a real number, not 'list'
expression: str(hex(255)) => result: 0xff
expression: str(data.county[0:1].lower()) => result: m
expression: str('wealthy' if data.income > 1_000_000 else 'middle_class') => result: middle_class
expression: str(calculator.today() if data.income > 1_000_000 else calculator.next_week()) => result: 2025-06-13
expression: str('even' if data.income % 2 == 0 else 'odd') => result: even
expression: str('even' if (data.income + 1) % 2 == 0 else 'odd') => result: odd
```
