# Python with uv, ruff, etc

This directory explores using **"hypermodern python tooling"**
such as uv and ruff.

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

Creates an isolated shared environment for CLI tools.

```
$ pipx install black
  installed package black 25.1.0, installed using Python 3.13.5
  These apps are now globally available
    - black
    - blackd
done! ✨ 🌟 ✨

$ ls -al ~/.local/bin/
lrwxr-xr-x@ 1 cjoakim  staff   48 Jun 20 12:41 black -> /Users/cjoakim/.local/pipx/venvs/black/bin/black
lrwxr-xr-x@ 1 cjoakim  staff   49 Jun 20 12:41 blackd -> /Users/cjoakim/.local/pipx/venvs/black/bin/blackd

$ black .
No Python files are present to be formatted. Nothing to do 😴

$ pipx list
venvs are in /Users/cjoakim/.local/pipx/venvs
apps are exposed on your $PATH at /Users/cjoakim/.local/bin
manual pages are exposed at /Users/cjoakim/.local/share/man
   package black 25.1.0, installed using Python 3.13.5
    - black
    - blackd

$ pipx install httpx
$ pipx install httpx[cli] --force

$ pipx list
venvs are in /Users/cjoakim/.local/pipx/venvs
apps are exposed on your $PATH at /Users/cjoakim/.local/bin
manual pages are exposed at /Users/cjoakim/.local/share/man
   package black 25.1.0, installed using Python 3.13.5
    - black
    - blackd
   package httpx 0.28.1, installed using Python 3.13.5
    - httpx

$ httpx https://cosmos.azure.com/

$ pipx install uv  (alternatively, install wuth homebrew)
```

---

## Tool Use: uv

```
$ uv --help
An extremely fast Python package manager.

Usage: uv [OPTIONS] <COMMAND>

Commands:
  run      Run a command or script
  init     Create a new project
  add      Add dependencies to the project
  remove   Remove dependencies from the project
  version  Read or update the project's version
  sync     Update the project's environment
  lock     Update the project's lockfile
  export   Export the project's lockfile to an alternate format
  tree     Display the project's dependency tree
  tool     Run and install commands provided by Python packages
  python   Manage Python versions and installations
  pip      Manage Python packages with a pip-compatible interface
  venv     Create a virtual environment
  build    Build Python packages into source distributions and wheels
  publish  Upload distributions to an index
  cache    Manage uv's cache
  self     Manage the uv executable
  help     Display documentation for a command
...
```

Bootstrap a project in the current directory:

```
$ uv init .

$ ls -al
-rw-r--r--@ 1 cjoakim  staff    5 Jun 20 13:02 .python-version
-rw-r--r--@ 1 cjoakim  staff   85 Jun 20 13:02 main.py
-rw-r--r--@ 1 cjoakim  staff  153 Jun 20 13:02 pyproject.toml
-rw-r--r--@ 1 cjoakim  staff   79 Jun 20 13:03 README.md
```

Create the python virtual environment in the current directory.
Note that it's directory name is **.venv/** not **venv**.

```
$ uv venv
Using CPython 3.13.5 interpreter at: /opt/homebrew/opt/python@3.13/bin/python3.13
Creating virtual environment at: .venv
Activate with: source .venv/bin/activate

$ source .venv/bin/activate
(uv_init) [~/github/azure-ai-explorations/python-uv-ruff/uv_init]$
```

Install the python libraries into the venv per the
[project] dependencies in the pyproject.toml file.
(note: it's very fast compared to 'pip install')

```
[project]
name = "aax-example"
version = "0.1.0"
dependencies = [
  "aiohttp",
  "azure-ai-documentintelligence>=1.0.2",
  "azure-ai-projects",
  "azure-cosmos>=4.9.0",
  "azure-identity",
  "azure-storage-blob",
  "docopt",
...
```

```
$ uv pip install --editable .
Resolved 61 packages in 11ms
      Built docopt==0.6.2
      Built aax-example @ file:///Users/cjoakim/github/azure-ai-explorations/python-uv-ruff/uv_init
Prepared 2 packages in 880ms
Installed 61 packages in 176ms
 + aax-example==0.1.0 (from file:///Users/cjoakim/github/azure-ai-explorations/python-uv-ruff/uv_init)
 + aiohappyeyeballs==2.6.1
 + aiohttp==3.12.13
 + aiosignal==1.3.2
 + annotated-types==0.7.0
 + anyio==4.9.0
 + attrs==25.3.0
 + azure-ai-agents==1.0.1
 + azure-ai-documentintelligence==1.0.2
 + azure-ai-projects==1.0.0b11
 + azure-core==1.34.0
 + azure-cosmos==4.9.0
 + azure-identity==1.23.0
 + azure-storage-blob==12.25.1
 + certifi==2025.6.15
 + cffi==1.17.1
 + charset-normalizer==3.4.2
 + coverage==7.9.1
 + cryptography==45.0.4
 + distro==1.9.0
 + docopt==0.6.2
 + duckdb==1.3.1
 + faker==37.4.0
 + frozenlist==1.7.0
 + h11==0.16.0
 + httpcore==1.0.9
 + httpx==0.28.1
 + idna==3.10
 + iniconfig==2.1.0
 + isodate==0.7.2
 + jinja2==3.1.6
 + jiter==0.10.0
 + markupsafe==3.0.2
 + msal==1.32.3
 + msal-extensions==1.3.1
 + multidict==6.5.0
 + openai==1.88.0
 + packaging==25.0
 + pluggy==1.6.0
 + propcache==0.3.2
 + psutil==7.0.0
 + pycparser==2.22
 + pydantic==2.11.7
 + pydantic-core==2.33.2
 + pygments==2.19.1
 + pyjwt==2.10.1
 + pytest==8.4.1
 + pytest-asyncio==1.0.0
 + pytest-cov==6.2.1
 + python-dotenv==1.1.0
 + pytz==2025.2
 + redis==6.2.0
 + requests==2.32.4
 + six==1.17.0
 + sniffio==1.3.1
 + tqdm==4.67.1
 + typing-extensions==4.14.0
 + typing-inspection==0.4.1
 + tzdata==2025.2
 + urllib3==2.5.0
 + yarl==1.20.1
```

Display the project's dependency tree.

```
$ uv tree
Resolved 62 packages in 1ms
aax-example v0.1.0
├── aiohttp v3.12.13
│   ├── aiohappyeyeballs v2.6.1
│   ├── aiosignal v1.3.2
│   │   └── frozenlist v1.7.0
│   ├── attrs v25.3.0
│   ├── frozenlist v1.7.0
│   ├── multidict v6.5.0
│   ├── propcache v0.3.2
│   └── yarl v1.20.1
│       ├── idna v3.10
│       ├── multidict v6.5.0
│       └── propcache v0.3.2
├── azure-ai-documentintelligence v1.0.2
│   ├── azure-core v1.34.0
│   │   ├── requests v2.32.4
│   │   │   ├── certifi v2025.6.15
│   │   │   ├── charset-normalizer v3.4.2
│   │   │   ├── idna v3.10
│   │   │   └── urllib3 v2.5.0
│   │   ├── six v1.17.0
│   │   └── typing-extensions v4.14.0
│   ├── isodate v0.7.2
│   └── typing-extensions v4.14.0
├── azure-ai-projects v1.0.0b11
│   ├── azure-ai-agents v1.0.1
│   │   ├── azure-core v1.34.0 (*)
│   │   ├── isodate v0.7.2
│   │   └── typing-extensions v4.14.0
│   ├── azure-core v1.34.0 (*)
│   ├── azure-storage-blob v12.25.1
│   │   ├── azure-core v1.34.0 (*)
│   │   ├── cryptography v45.0.4
│   │   │   └── cffi v1.17.1
│   │   │       └── pycparser v2.22
│   │   ├── isodate v0.7.2
│   │   └── typing-extensions v4.14.0
│   ├── isodate v0.7.2
│   └── typing-extensions v4.14.0
├── azure-cosmos v4.9.0
│   ├── azure-core v1.34.0 (*)
│   └── typing-extensions v4.14.0
├── azure-identity v1.23.0
│   ├── azure-core v1.34.0 (*)
│   ├── cryptography v45.0.4 (*)
│   ├── msal v1.32.3
│   │   ├── cryptography v45.0.4 (*)
│   │   ├── pyjwt[crypto] v2.10.1
│   │   │   └── cryptography v45.0.4 (extra: crypto) (*)
│   │   └── requests v2.32.4 (*)
│   ├── msal-extensions v1.3.1
│   │   └── msal v1.32.3 (*)
│   └── typing-extensions v4.14.0
├── azure-storage-blob v12.25.1 (*)
├── docopt v0.6.2
├── duckdb v1.3.1
├── faker v37.4.0
│   └── tzdata v2025.2
├── httpx v0.28.1
│   ├── anyio v4.9.0
│   │   ├── idna v3.10
│   │   └── sniffio v1.3.1
│   ├── certifi v2025.6.15
│   ├── httpcore v1.0.9
│   │   ├── certifi v2025.6.15
│   │   └── h11 v0.16.0
│   └── idna v3.10
├── jinja2 v3.1.6
│   └── markupsafe v3.0.2
├── openai v1.88.0
│   ├── anyio v4.9.0 (*)
│   ├── distro v1.9.0
│   ├── httpx v0.28.1 (*)
│   ├── jiter v0.10.0
│   ├── pydantic v2.11.7
│   │   ├── annotated-types v0.7.0
│   │   ├── pydantic-core v2.33.2
│   │   │   └── typing-extensions v4.14.0
│   │   ├── typing-extensions v4.14.0
│   │   └── typing-inspection v0.4.1
│   │       └── typing-extensions v4.14.0
│   ├── sniffio v1.3.1
│   ├── tqdm v4.67.1
│   └── typing-extensions v4.14.0
├── psutil v7.0.0
├── pytest v8.4.1
│   ├── iniconfig v2.1.0
│   ├── packaging v25.0
│   ├── pluggy v1.6.0
│   └── pygments v2.19.1
├── pytest-asyncio v1.0.0
│   └── pytest v8.4.1 (*)
├── pytest-cov v6.2.1
│   ├── coverage v7.9.1
│   ├── pluggy v1.6.0
│   └── pytest v8.4.1 (*)
├── python-dotenv v1.1.0
├── pytz v2025.2
└── redis v6.2.0
```

Export a requirements.txt file.

```
$ uv pip compile pyproject.toml -o requirements.txt

Resolved 60 packages in 16ms
# This file was autogenerated by uv via the following command:
#    uv pip compile pyproject.toml -o requirements.txt
aiohappyeyeballs==2.6.1
    # via aiohttp
aiohttp==3.12.13
    # via aax-example (pyproject.toml)
aiosignal==1.3.2
    # via aiohttp
annotated-types==0.7.0
    # via pydantic
anyio==4.9.0
    # via
    #   httpx
    #   openai
attrs==25.3.0
    # via aiohttp
azure-ai-agents==1.0.1
    # via azure-ai-projects
azure-ai-documentintelligence==1.0.2
    # via aax-example (pyproject.toml)
azure-ai-projects==1.0.0b11
    # via aax-example (pyproject.toml)
azure-core==1.34.0
    # via
    #   azure-ai-agents
    #   azure-ai-documentintelligence
    #   azure-ai-projects
    #   azure-cosmos
    #   azure-identity
    #   azure-storage-blob
azure-cosmos==4.9.0
    # via aax-example (pyproject.toml)
azure-identity==1.23.0
    # via aax-example (pyproject.toml)
azure-storage-blob==12.25.1
    # via
    #   aax-example (pyproject.toml)
    #   azure-ai-projects
certifi==2025.6.15
    # via
    #   httpcore
    #   httpx
    #   requests
cffi==1.17.1
    # via cryptography
charset-normalizer==3.4.2
    # via requests
coverage==7.9.1
    # via pytest-cov
cryptography==45.0.4
    # via
    #   azure-identity
    #   azure-storage-blob
    #   msal
    #   pyjwt
distro==1.9.0
    # via openai
docopt==0.6.2
    # via aax-example (pyproject.toml)
duckdb==1.3.1
    # via aax-example (pyproject.toml)
faker==37.4.0
    # via aax-example (pyproject.toml)
frozenlist==1.7.0
    # via
    #   aiohttp
    #   aiosignal
h11==0.16.0
    # via httpcore
httpcore==1.0.9
    # via httpx
httpx==0.28.1
    # via
    #   aax-example (pyproject.toml)
    #   openai
idna==3.10
    # via
    #   anyio
    #   httpx
    #   requests
    #   yarl
iniconfig==2.1.0
    # via pytest
isodate==0.7.2
    # via
    #   azure-ai-agents
    #   azure-ai-documentintelligence
    #   azure-ai-projects
    #   azure-storage-blob
jinja2==3.1.6
    # via aax-example (pyproject.toml)
jiter==0.10.0
    # via openai
markupsafe==3.0.2
    # via jinja2
msal==1.32.3
    # via
    #   azure-identity
    #   msal-extensions
msal-extensions==1.3.1
    # via azure-identity
multidict==6.5.0
    # via
    #   aiohttp
    #   yarl
openai==1.88.0
    # via aax-example (pyproject.toml)
packaging==25.0
    # via pytest
pluggy==1.6.0
    # via
    #   pytest
    #   pytest-cov
propcache==0.3.2
    # via
    #   aiohttp
    #   yarl
psutil==7.0.0
    # via aax-example (pyproject.toml)
pycparser==2.22
    # via cffi
pydantic==2.11.7
    # via openai
pydantic-core==2.33.2
    # via pydantic
pygments==2.19.1
    # via pytest
pyjwt==2.10.1
    # via msal
pytest==8.4.1
    # via
    #   aax-example (pyproject.toml)
    #   pytest-asyncio
    #   pytest-cov
pytest-asyncio==1.0.0
    # via aax-example (pyproject.toml)
pytest-cov==6.2.1
    # via aax-example (pyproject.toml)
python-dotenv==1.1.0
    # via aax-example (pyproject.toml)
pytz==2025.2
    # via aax-example (pyproject.toml)
redis==6.2.0
    # via aax-example (pyproject.toml)
requests==2.32.4
    # via
    #   azure-core
    #   msal
six==1.17.0
    # via azure-core
sniffio==1.3.1
    # via
    #   anyio
    #   openai
tqdm==4.67.1
    # via openai
typing-extensions==4.14.0
    # via
    #   azure-ai-agents
    #   azure-ai-documentintelligence
    #   azure-ai-projects
    #   azure-core
    #   azure-cosmos
    #   azure-identity
    #   azure-storage-blob
    #   openai
    #   pydantic
    #   pydantic-core
    #   typing-inspection
typing-inspection==0.4.1
    # via pydantic
tzdata==2025.2
    # via faker
urllib3==2.5.0
    # via requests
yarl==1.20.1
    # via aiohttp
```

---

## Tool Use: ruff

```
$ ruff check > tmp/ruff-check.txt
```

Then address the issues in your code listed in tmp/ruff-check.txt.
