# ollama

- https://ollama.com
- https://ollama.com/library (see and download models)
- https://ollama.com/library/phi3
- https://github.com/ollama/ollama 
- https://pypi.org/project/ollama/
- https://github.com/ollama/ollama-python
- https://python.langchain.com/docs/integrations/llms/ollama/

Runs on Mac, Linux, or Windows.

ollama is primarily a Terminal/CLI-oriented program.

## Installation on macOS

- Download the application from https://ollama.com
- Copy it to the Applications folder
- Double-click execute it in the Applications folder
- Install the CLI tool and first model upon first execution of the app UI

### Alternative macOS installation with Homebrew

```
$ brew install ollama

$ which ollama
/opt/homebrew/bin/ollama
```

Optional configuration

```
$ brew services start ollama

$ brew services list
```

Otherwise, just run "ollama serve" as necessary:

```
$ ollama serve
```

## CLI interaction

See the help info.

```
$ ollama help
Large language model runner

Usage:
  ollama [flags]
  ollama [command]

Available Commands:
  serve       Start ollama
  create      Create a model from a Modelfile
  show        Show information for a model
  run         Run a model
  stop        Stop a running model
  pull        Pull a model from a registry
  push        Push a model to a registry
  list        List models
  ps          List running models
  cp          Copy a model
  rm          Remove a model
  help        Help about any command
```

List the currently installed models; it's an empty list at first.

```
$ ollama list
NAME    ID    SIZE    MODIFIED
```

Run the phi3 model (it appears to be a Docker image).
Then exit the shell with the /bye command.

```
$ ollama run phi3
pulling manifest
pulling 633fc5be925f: 100% ▕████████████████████████████████████████████████▏ 2.2 GB
pulling fa8235e5b48f: 100% ▕████████████████████████████████████████████████▏ 1.1 KB
pulling 542b217f179c: 100% ▕████████████████████████████████████████████████▏  148 B
pulling 8dde1baf1db0: 100% ▕████████████████████████████████████████████████▏   78 B
pulling 23291dc44752: 100% ▕████████████████████████████████████████████████▏  483 B
verifying sha256 digest
writing manifest
success
>>> /bye
```

List the models again; phi3 is now present.

```
$ ollama list
NAME           ID              SIZE      MODIFIED
phi3:latest    4f2222927938    2.2 GB    2 minutes ago
```

---

## Run and Serve

In one terminal, run a model:

```
$ ollama run --verbose phi3
```

In another terminal, run the server:

```
$ ollama serve
$ ollama serve --help
```

---

## ollama python lib

- https://pypi.org/project/ollama/
- https://github.com/ollama/ollama-python

