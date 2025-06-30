# Python with uv, ruff, etc

Using **"hypermodern python tooling"** such as uv and ruff.

ALL PYTHON SUBPROJECTS IN THIS REPO HAVE BEEN CONVERTED TO USING uv AND ruff.

See the O'Reilly book of this title at:
https://www.oreilly.com/library/view/hypermodern-python-tooling/9781098139575/

## TOML and pyproject.toml

**pyproject.toml** is a configuration file used by packaging tools, as well as
other tools such as linters, type checkers, etc. 

### TOML 

Tom's Obvious Minimal Language

- https://toml.io/en/
- https://toml.io/en/v1.0.0

### pyproject.toml 

- https://packaging.python.org/en/latest/specifications/pyproject-toml/
- https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#writing-pyproject-toml
- https://realpython.com/python-pyproject-toml/
- https://docs.python.org/3/library/tomllib.html
  - python standard library for reading/parsing a TOML 1.0.0 file

---

## Astral

Astral’s mission is to make the Python ecosystem more productive
by building high-performance developer tools, starting with Ruff.

See https://astral.sh

### UV

An extremely fast Python package and project manager, written in Rust.

See https://github.com/astral-sh/uv

### Ruff

An extremely fast Python linter, written in Rust.

See https://docs.astral.sh/ruff/

### pipx

Install and Run Python Applications in Isolated Environments

See https://github.com/pypa/pipx

---

## Example Repos

- https://github.com/Azure/azure-sdk-for-python
- https://github.com/pamelafox

---

## Installation

Install the following "modern python" tools below:

- py
- uv
- ruff
- pipx
- hatch / hatchling

### py (python launcher)

```
$ brew install python-launcher

$ which py
/opt/homebrew/bin/py

$ py --version
Python 3.13.5

$ py -V
Python 3.13.5

$ py --list
 3.13 │ /opt/homebrew/bin/python3.13
 3.12 │ /opt/homebrew/bin/python3.12
```

### uv 

```
$ brew install uv

$ which uv
/opt/homebrew/bin/uv

$ uv --version
uv 0.7.13 (Homebrew 2025-06-12)
```

### ruff

```
$ brew install ruff

$ which ruff
/opt/homebrew/bin/ruff

$ ruff --version
ruff 0.12.0
```

### pipx

```
$ brew install pipx

$ which pipx
/opt/homebrew/bin/pipx

$ pipx --version
1.7.1

$ pipx ensurepath

above ensures that ~/.local/bin is in the PATH environment variable
```

### hatch (hatchling)

```
$ brew install hatch

$ which hatch
/opt/homebrew/bin/hatch

$ hatch --version
Hatch, version 1.14.1
```

---

## Tool Use: pipx

```
$ pipx install black
$ pipx list
$ pipx install httpx
$ pipx install httpx[cli] --force
$ pipx list
$ pipx install uv  (alternatively, install wuth homebrew)
```

---

## Tool Use: uv

```
$ uv --help
$ uv init .
$ uv venv
$ uv pip install --editable .
$ uv tree
$ uv pip compile pyproject.toml -o requirements.txt
```

---

## Tool Use: ruff

```
$ ruff check > tmp/ruff-check.txt
```

Then address the issues in your code listed in tmp/ruff-check.txt.
