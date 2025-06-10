# DotNet AI Explorations

A collection of **exploratory** DotNet/C# AI projects and tools.

## Links

- https://learn.microsoft.com/en-us/semantic-kernel/get-started/quick-start-guide?pivots=programming-language-csharp

## Project Creation

### Install DotNet 9 on macOS M2 with Homebrew

```
$ brew uninstall --cask dotnet

$ brew install dotnet

$ brew list | grep dotnet
dotnet

$ dotnet --version
9.0.106

$ which dotnet
/opt/homebrew/bin/dotnet

$ dotnet --version
9.0.106
```

### Create Project and Add Packages

See https://www.nuget.org.  Search for packages in the UI.

See script **setup.sh** which executes these steps.

```
$ dotnet new console
The template "Console App" was created successfully.

dotnet add package Microsoft.SemanticKernel
dotnet add package Microsoft.Azure.Cosmos
dotnet add package Azure.Storage.Blobs
dotnet add package Newtonsoft.Json
dotnet add package DotNetEnv
dotnet add package Microsoft.SemanticKernel.Plugins.Core --version 1.53.1-preview
dotnet add package Microsoft.SemanticKernel.Planners 
dotnet add package Microsoft.SemanticKernel.Planners.Handlebars;
dotnet add package Microsoft.SemanticKernel.Planners.Liquid
dotnet add package Microsoft.SemanticKernel.Planners.OpenAI
dotnet add package Microsoft.SemanticKernel.PromptTemplates.Handlebars
dotnet add package Microsoft.SemanticKernel.PromptTemplates.Liquid
dotnet add package Microsoft.SemanticKernel.Yaml --version 1.54.0
dotnet add package Azure.Monitor.OpenTelemetry.Exporter
dotnet add package Joakimsoftware.M26 --version 2.0.0

$ dotnet list package
Project 'dotnetx' has the following package references
   [net9.0]:
   Top-level Package                                          Requested        Resolved
   > Azure.Monitor.OpenTelemetry.Exporter                     1.4.0            1.4.0
   > Azure.Storage.Blobs                                      12.24.0          12.24.0
   > DotNetEnv                                                3.1.1            3.1.1
   > Joakimsoftware.M26                                       2.0.0            2.0.0
   > Microsoft.Azure.Cosmos                                   3.51.0           3.51.0
   > Microsoft.SemanticKernel                                 1.54.0           1.54.0
   > Microsoft.SemanticKernel.Plugins.Core                    1.53.1-preview   1.53.1-preview
   > Microsoft.SemanticKernel.PromptTemplates.Handlebars      1.54.0           1.54.0
   > Microsoft.SemanticKernel.PromptTemplates.Liquid          1.54.0           1.54.0
   > Microsoft.SemanticKernel.Yaml                            1.54.0           1.54.0
   > Newtonsoft.Json                                          13.0.3           13.0.3

$ dotnet build

$ dotnet run
Hello, World!
```
