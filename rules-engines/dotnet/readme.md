# Microsoft RulesEngine

Exploring the microsoft/RulesEngine - 
a Json based Rules Engine with extensive Dynamic expression support.

## Links

- [Github.io](https://microsoft.github.io/RulesEngine/)
- [GitHub](https://github.com/microsoft/RulesEngine)
- [NuGET](https://www.nuget.org/packages/RulesEngine/)
- [Wiki](https://github.com/microsoft/RulesEngine/wiki/Getting-Started)
- [Schema Definition](https://github.com/microsoft/RulesEngine/blob/main/schema/workflow-schema.json)
- [C# Lambda Expressions](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/lambda-expressions)
- [Medium.com Blog - Vamsi Dogiparthi](https://medium.com/@vamsidogiparthi)
  - See the 6-part blog series on RulesEngine 

### Users of the RulesEngine package

- https://github.com/microsoft/ChatWithYourBusinessRules
- https://github.com/microsoft/FeatureFlightingManagement

---

## Project Setup

```
$ dotnet --version
9.0.300

$ dotnet new console --output console_app

$ cd console_app

$ dotnet add package RulesEngine --version 6.0.0
# dotnet add package DotNetEnv
```