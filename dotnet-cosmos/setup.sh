#!/bin/bash

# Bootstrap this project with the dotnet CLI.
# Chris Joakim, 2025 

which dotnet

dotnet --version

#dotnet new console

# See https://www.nuget.org 
dotnet add package Microsoft.Azure.Cosmos --version 3.52.0
dotnet add package Azure.Storage.Blobs
dotnet add package Newtonsoft.Json
dotnet add package DotNetEnv

dotnet add package Azure.Identity 
dotnet add package Azure.ResourceManager.CosmosDB

dotnet list package


#    Top-level Package                     Requested   Resolved
#    > Azure.Identity                      1.14.0      1.14.0
#    > Azure.ResourceManager.CosmosDB      1.3.2       1.3.2
#    > Azure.Storage.Blobs                 12.24.1     12.24.1
#    > DotNetEnv                           3.1.1       3.1.1
#    > Microsoft.Azure.Cosmos              3.52.0      3.52.0
#    > Newtonsoft.Json                     13.0.3      13.0.3