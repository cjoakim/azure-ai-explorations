# eval() rules_engine

Use simple python built-in functionality with the **eval()** method
to implement a rules engine.

## Links

- https://docs.python.org/3/library/functions.html#eval 
- https://www.w3schools.com/python/ref_func_eval.asp

## Use

Assumes bash shell on macOS.  Create scripts as necessary for Windows.

Also assumes that **uv** is installed on your system.

```
$ venv.sh

$ source .venv/bin/activate

$ python main.py help
Usage:
  python main.py <func>
  python main.py env
  python main.py simple_evals
  python main.py pydantic_evals
  python main.py evaluate_rules_from_json_files

$ python main.py pydantic_evals

pydantic_evals
Calculator today:     2025-06-22
Calculator next week: 2025-06-29
rule_data:
{
  "state": "NC",
  "county": "Mecklenburg",
  "postal_code": 28036,
  "state_tax_rate": 0.07,
  "county_tax_rate": 0.005,
  "income": 100000
}
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
expression: str(calculator.today() if data.income > 1_000_000 else calculator.next_week()) => result: 2025-06-29
expression: str('even' if data.income % 2 == 0 else 'odd') => result: even
expression: str('even' if (data.income + 1) % 2 == 0 else 'odd') => result: odd
WARNING:root:file written: rules/rules.json
WARNING:root:file written: rules/rules_data.json
```