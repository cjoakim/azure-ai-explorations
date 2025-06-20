# Python with uv, ruff, etc

This directory explores using **"hypermodern python tooling"**
such as uv and ruff.

See the O'Reilly book of this title at:
https://www.oreilly.com/library/view/hypermodern-python-tooling/9781098139575/

## Astral

Astral’s mission is to make the Python ecosystem more productive
by building high-performance developer tools, starting with Ruff.

See https://astral.sh

### UV

An extremely fast Python package and project manager, written in Rust.

- https://github.com/astral-sh/uv

### Ruff

An extremely fast Python linter, written in Rust.

- https://docs.astral.sh/ruff/


---

## Example Repos

- https://github.com/Azure/azure-sdk-for-python
- https://github.com/pamelafox

---

## Installation

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