#!/bin/bash

# which dotnet

# dotnet --version

# dotnet new console

dotnet add package RulesEngine --version 6.0.0

# See https://www.nuget.org 
# dotnet add package Microsoft.SemanticKernel
# dotnet add package Microsoft.Azure.Cosmos
# dotnet add package Azure.Storage.Blobs
# dotnet add package Newtonsoft.Json
# dotnet add package DotNetEnv
# dotnet add package Microsoft.SemanticKernel.Plugins.Core --version 1.53.1-preview
# dotnet add package Microsoft.SemanticKernel.Planners 
# dotnet add package Microsoft.SemanticKernel.Planners.Handlebars;
# dotnet add package Microsoft.SemanticKernel.Planners.Liquid
# dotnet add package Microsoft.SemanticKernel.Planners.OpenAI
# dotnet add package Microsoft.SemanticKernel.PromptTemplates.Handlebars
# dotnet add package Microsoft.SemanticKernel.PromptTemplates.Liquid
# dotnet add package Microsoft.SemanticKernel.Yaml --version 1.54.0
# dotnet add package Azure.Monitor.OpenTelemetry.Exporter
# dotnet add package Joakimsoftware.M26 --version 2.0.0

dotnet list package
