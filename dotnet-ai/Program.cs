using System;
using System.IO;
using System.Collections.Generic;
using System.Resources;
using Azure.Monitor.OpenTelemetry.Exporter;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Plugins;
using Microsoft.SemanticKernel.Plugins.Core;
using Microsoft.SemanticKernel.PromptTemplates.Handlebars;
using Microsoft.Extensions.Logging;
using OpenTelemetry;
using OpenTelemetry.Logs;
using OpenTelemetry.Metrics;
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;
using DotNetEnv;
using Fluid;
using Fluid.Ast;
using Joakimsoftware.M26; // This is a NuGet Package
using Joakimsoftware.Plugins; // These three are in this codebase
using Joakimsoftware.Core;
using Joakimsoftware.IO;
using Joakimsoftware.SK;
using Microsoft.SemanticKernel.Connectors.OpenAI;


namespace Joakimsoftware {
    class Program {
        private static string[] cliArgs = [];
        
        static async Task<int> Main(string[] args) {
            cliArgs = args;
            string func = GetRunFunction(args);
            Log("run function: " + func);
            DotNetEnv.Env.Load();

            switch (func) {
                case "env":
                    EnvExamples();
                    break;
                case "io":
                    IoExamples();
                    break;
                case "paths":
                    PathsExamples();
                    break;
                case "m26":
                    M26Examples();
                    break;
                case "sk_simple_prompt":
                    await SKSimplePrompt();
                    break;
                case "sk_simple_plugins":
                    await SKSimplePlugins();
                    break;
                default:
                    Log("Undefined function given on command-line; " + func);
                    Log("Command-line examples:");
                    Log("  dotnet run env");
                    Log("  dotnet run io");
                    Log("  dotnet run paths");
                    Log("  dotnet run m26");
                    Log("  dotnet run sk_simple_prompt");
                    Log("  dotnet run sk_simple_plugins");
                    break;
            }
            return 0;
        }

        private static void EnvExamples() {
            Console.WriteLine("pwd:        " + Core.Env.Pwd());
            Console.WriteLine("home:       " + Core.Env.HomeDir());
            Console.WriteLine("os arch:    " + Core.Env.OsArch());
            Console.WriteLine("os desc:    " + Core.Env.OsDesc());
            Console.WriteLine("is windows: " + Core.Env.IsWindows());
            Console.WriteLine("is macos:   " + Core.Env.IsMacOS());
            Console.WriteLine("is linux:   " + Core.Env.IsLinux());
        }

        private static void IoExamples() {
            string githubDir = Paths.GithubDir();
            Console.WriteLine("github dir:  " + githubDir);

            List<string> subpaths = new List<string> { "cj-dotnet", "Console1", "Console1" };
            String fullpath = Paths.Normalize(githubDir, subpaths);
            Console.WriteLine("fullpath:  " + fullpath);

            //Console.WriteLine("normalized:  " + Paths.Normalize("");

            FileIO fio = new FileIO();

            //string infile = pwd + @"\Program.cs";
            //Console.WriteLine("infile: " + infile);
            //Console.WriteLine(fio.ReadText(infile));
        }

        private static void PathsExamples() {
            Log("norm: " + Paths.Normalize(@"\"));
            Log("norm: " + Paths.Normalize(@"/"));
            Log("norm: " + Paths.Normalize(@"\Users\chris\github\cj-dotnet\Console1\Console1"));
            Log("norm: " + Paths.Normalize(@"/Users/chris/github/cj-dotnet/Console1/Console1"));
            Log("norm: " + Paths.Normalize(@"Program.cs"));
        }

        private static void M26Examples() {
            // See https://www.nuget.org/packages/Joakimsoftware.M26
            // This method explores the Joakimsoftware.M26 package before 
            // implementing its' functionality in a Semantic Kernel plugin.

            Distance d = new Distance(26.2);
            double m = d.asMiles();
            double k = d.asKilometers();
            double y = d.asYards();
            Console.WriteLine($"Distance - miles:        {m}");
            Console.WriteLine($"Distance - kilometers:   {k}");
            Console.WriteLine($"Distance - yards:        {y}");

            ElapsedTime et1 = new ElapsedTime("3:47:30");
            ElapsedTime et2 = new ElapsedTime(3, 47, 30);
            ElapsedTime et3 = new ElapsedTime(13650.0);
            Console.WriteLine($"ElapsedTime - et1 hhmmss: {et1.asHHMMSS()}");
            Console.WriteLine($"ElapsedTime - et2 hhmmss: {et2.asHHMMSS()}");
            Console.WriteLine($"ElapsedTime - et3 hhmmss: {et3.asHHMMSS()}");

            // Construct a Speed from a Distance and ElapsedTime
            Speed sp = new Speed(d, et1);
            double mph = sp.mph();
            double kph = sp.kph();
            double yph = sp.yph();
            double spm = sp.secondsPerMile();
            string ppm = sp.pacePerMile();
            Console.WriteLine($"Speed - mph:             {mph}");
            Console.WriteLine($"Speed - kph:             {kph}");
            Console.WriteLine($"Speed - yph:             {yph}");
            Console.WriteLine($"Speed - secondsPerMile:  {spm}");
            Console.WriteLine($"Speed - pacePerMile:     {ppm}");

            // Project the Speed to another Distance, simple formula
            ElapsedTime etp1 = sp.projectedTime(new Distance(31.0));
            Console.WriteLine($"Speed projected to 31m:  {etp1.asHHMMSS()}");

            // Project the Speed to another Distance, riegel exponential formula
            ElapsedTime etp2 = sp.projectedTime(new Distance(31.0), Constants.SpeedFormulaRiegel);
            Console.WriteLine($"Speed projected to 31m:  {etp2.asHHMMSS()}");

            Age a1 = new Age(42.4);
            Age a2 = new Age(67.5);

            Speed agsp = sp.ageGraded(a1, a2);
            Console.WriteLine($"age-graded to 67.5:      {agsp.elapsedTime.asHHMMSS()}");

            RunWalkCalculator rwc = new RunWalkCalculator();
            // method signature: calculate(runHHMMSS, runPPM, walkHHMMSS, walkPPM, miles)
            // returns a RunWalkCalculation struct
            RunWalkCalculation calc = rwc.calculate("4:30", "9:30", "00:30", "17:00", 26.2);
            Console.WriteLine($"RunWalkCalc - mph:       {calc.averageSpeed.mph()}");
            Console.WriteLine($"RunWalkCalc - proj time: {calc.projectedTime}");
        }


        /**
         * Build and return the Semantic Kernel instance used in this app/program.
         * The method name "BuildAppKernel" is used here to avoid confusion with SK SDK.
         * See https://learn.microsoft.com/en-us/semantic-kernel/concepts/plugins/native-plugins
         */
        private static Kernel BuildAppKernel() {

            string apiUrl = ReadEnvVar("AZURE_OPENAI_URL", "none");
            string apiKey = ReadEnvVar("AZURE_OPENAI_KEY", "none");
            string depName = ReadEnvVar("AZURE_OPENAI_COMPLETIONS_DEPLOYMENT", "gpt-3.5-turbo");
            if (CliFlagPresent("--personal")) {
                apiUrl = ReadEnvVar("AZURE_PERSONAL_OPENAI_URL", "none");
                apiKey = ReadEnvVar("AZURE_PERSONAL_OPENAI_KEY", "none");
                depName = ReadEnvVar("AZURE_PERSONAL_OPENAI_COMPLETIONS_DEPLOYMENT", "gpt-3.5-turbo");
            }
            Console.WriteLine("BuildAppKernel - apiUrl:  " + apiUrl);
            Console.WriteLine("BuildAppKernel - apiKey:  " + apiKey);
            Console.WriteLine("BuildAppKernel - depName: " + depName);

            IKernelBuilder builder = Kernel.CreateBuilder();

            var telemmetryLogger = BuildTelementryLogger();
            if (telemmetryLogger != null) {
                builder.Services.AddSingleton(telemmetryLogger);
            }

            // Add built-in Plugins
            // See https://learn.microsoft.com/en-us/dotnet/api/microsoft.semantickernel.plugins.core?view=semantic-kernel-dotnet
            builder.Plugins.AddFromType<FileIOPlugin>();
            builder.Plugins.AddFromType<HttpPlugin>();
            builder.Plugins.AddFromType<TextPlugin>();
            builder.Plugins.AddFromType<TimePlugin>();
            builder.Plugins.AddFromType<ConversationSummaryPlugin>();
            //builder.Plugins.AddFromType<MathPlugin>();  // moved or obsolete?
            //builder.Plugins.AddFromType<WaitPlugin>();  // moved or obsolete?

            // Add custom native Plugins
            builder.Plugins.AddFromType<RunningPlugin>();

            // Add a custom prompt logger; see PromptLogger.cs in this repo
            builder.Services.AddSingleton<IPromptRenderFilter, PromptLogger>();

            // Add your app-specific Completions with your deployed model(s)
            builder.AddAzureOpenAIChatCompletion(
                deploymentName: depName,
                apiKey: apiKey,
                endpoint: apiUrl
            );

            Kernel kernel = builder.Build();
            Console.WriteLine("BuildAppKernel - kernel: " + kernel);
            return kernel;
        }

        /**
         * Configure App Insights Telemetry
         * See https://learn.microsoft.com/en-us/semantic-kernel/concepts/enterprise-readiness/observability/telemetry-with-app-insights?tabs=Powershell&pivots=programming-language-csharp
         */
        private static ILoggerFactory? BuildTelementryLogger() {
            string appInsightsConnStr = ReadEnvVar("APP_INSIGHTS_CONNECTION_STRING", "none");
            if (appInsightsConnStr.Trim().Length < 10) {
                Log("APP_INSIGHTS_CONNECTION_STRING not set, ConfigureTelementry() returning null ILoggerFactory");
                return null;
            }

            Console.WriteLine("BuildTelementryLogger appInsightsConnStr: " + appInsightsConnStr);

            var resourceBuilder = ResourceBuilder
                .CreateDefault()
                .AddService("SKTelemetryApp");
            AppContext.SetSwitch("Microsoft.SemanticKernel.Experimental.GenAI.EnableOTelDiagnosticsSensitive", true);

            using var traceProvider = Sdk.CreateTracerProviderBuilder()
                .SetResourceBuilder(resourceBuilder)
                .AddSource("Microsoft.SemanticKernel*")
                .AddAzureMonitorTraceExporter(options => options.ConnectionString = appInsightsConnStr)
                .Build();

            using var meterProvider = Sdk.CreateMeterProviderBuilder()
                .SetResourceBuilder(resourceBuilder)
                .AddMeter("Microsoft.SemanticKernel*")
                .AddAzureMonitorMetricExporter(options => options.ConnectionString = appInsightsConnStr)
                .Build();

            return LoggerFactory.Create(builder => {
                builder.AddOpenTelemetry(options => {
                    options.SetResourceBuilder(resourceBuilder);
                    options.AddAzureMonitorLogExporter(options => options.ConnectionString = appInsightsConnStr);
                    options.IncludeFormattedMessage = true;
                    options.IncludeScopes = true;
                });
                builder.SetMinimumLevel(LogLevel.Information);
            });
        }

        private static async Task<string> SKSimplePrompt() {
            Kernel kernel = BuildAppKernel();
            string prompt = PromptUser("enter a prompt, then enter: ");
            string resultText = "none";
            Console.WriteLine("prompt: " + prompt);

            if (prompt.Trim().Length > 0) {
                var result = await kernel.InvokePromptAsync(prompt);
                resultText = result.ToString();
                Console.WriteLine("resultText: " + resultText);
            }
            else {
                Console.WriteLine("no prompt given");
            }

            return resultText;
        }

        private static async Task<string> SKSimplePlugins() {
            string resultText = "none";
            Kernel kernel = BuildAppKernel();

            LogConsoleHeader("Invoke the built-in TimePlugin");
            // See docs at https://learn.microsoft.com/en-us/dotnet/api/microsoft.semantickernel.plugins.core.timeplugin
            var date = await kernel.InvokeAsync("TimePlugin", "Date");
            Console.WriteLine("date: " + date);
            var today = await kernel.InvokeAsync("TimePlugin", "DayOfWeek");
            Console.WriteLine("today: " + today);
            var tz = await kernel.InvokeAsync("TimePlugin", "TimeZoneName");
            Console.WriteLine("tz: " + tz);

            LogConsoleHeader("Invoke the custom RunningPlugin");
            var dist = await kernel.InvokeAsync(
                "RunningPlugin", "MarathonDistance", new KernelArguments());
            Console.WriteLine("marathon distance: " + dist);

            var args = new KernelArguments();
            args.Add("distance", "26.2");
            args.Add("hhmmss", "3:47:30");
            var ppm = await kernel.InvokeAsync(
                "RunningPlugin", "CalculatePacePerMile", args);
            Console.WriteLine("ppm: " + ppm);

            LogConsoleHeader("Adding a conventional Plugin with a config.json and skprompt.txt; jokes");
            var jokesPluginDir = Path.Combine(
                System.IO.Directory.GetCurrentDirectory(), "..", "plugins", "jokes");
            kernel.ImportPluginFromPromptDirectory(jokesPluginDir);
            Console.WriteLine("jokes plugin added");

            LogConsoleHeader("YAML Function example");
            ResourceUtil resourceUtil = new ResourceUtil();
            resourceUtil.DisplayResourceNames();
            string jokeYaml = resourceUtil.ReadResource("joke.yaml");
            Console.WriteLine(jokeYaml);
            args = new KernelArguments();
            args.Add("topic", "Tell me a joke about North Carolina");
            // https://learn.microsoft.com/en-us/semantic-kernel/concepts/prompts/handlebars-prompt-templates
            var templateFactory = new HandlebarsPromptTemplateFactory();
            var function = kernel.CreateFunctionFromPromptYaml(jokeYaml, templateFactory);
            var response = await kernel.InvokeAsync(function, args);
            Console.WriteLine(response);

            LogConsoleHeader("Invoke the custom native RunningPlugin explicitly with code and KernelArguments");
            response = await kernel.InvokeAsync("RunningPlugin", "MarathonDistance");
            Console.WriteLine($@"RunningPlugin:MarathonDistance -> {response}");
            args = new KernelArguments();
            args.Add("distance", "10.0");
            args.Add("hhmmss", "1:27:13");
            response = await kernel.InvokeAsync("RunningPlugin", "CalculatePacePerMile", args);
            Console.WriteLine($@"RunningPlugin:CalculatePacePerMile -> {response}");

            LogConsoleHeader(
                "Inline invocation of the MarathonDistance method of the RunningPlugin plugin in a Prompt");
            string prompt = @"
Convert the following distance in miles to kilometers: 
{{ RunningPlugin.MarathonDistance }} miles and also to yards.".Trim();
            response = await kernel.InvokePromptAsync(prompt);
            Console.WriteLine(response);

            LogConsoleHeader("Passing multiple args to a Plugin in a Prompt");
            // Passing multiple args to a Plugin in a Prompt syntax is harder; use KernelArguments.
            // The Chain-of-thought "Let's think step by step." made this prompt accurate!
            args = new KernelArguments();
            args.Add("d", "1.0");
            args.Add("t", "9:00");
            prompt = @"
Given a pace per mile of {{RunningPlugin.CalculatePacePerMile $d hhmmss=$t }},
how long would it take to run {{ RunningPlugin.MarathonDistance }} miles?

Let's think step by step.

Calculate the elapsed time in HH:MM:SS format.".Trim();
            response = await kernel.InvokePromptAsync(prompt, args);
            Console.WriteLine("========== \nYAML Function example");
            Console.WriteLine(response);

            LogConsoleHeader("Automatic/agentic Function Calling");
            OpenAIPromptExecutionSettings executionSettings = new OpenAIPromptExecutionSettings();
            executionSettings.ToolCallBehavior = ToolCallBehavior.AutoInvokeKernelFunctions;
            prompt = @"
Answer three questions:
First, tell me something funny on the topic of Connecticut.

Next, how many miles are in a marathon?

Next, if I run 3.1 miles in 26:12, what is my pace per mile?

Let's think step by step.
";
            response = await kernel.InvokePromptAsync(prompt, new(executionSettings));
            Console.WriteLine(response);

            return resultText;
        }

        private static void Log(string msg) {
            Console.WriteLine(msg);
        }

        private static void LogConsoleHeader(string msg) {
            Console.WriteLine("========================================");
            Console.WriteLine(msg);
        }

        private static string GetRunFunction(string[] args) {
            if ((args != null) && (args.Length > 0)) {
                return args[0].ToLower();
            }
            else {
                return "";
            }
        }

        private static bool CliFlagPresent(string flag) {
            foreach (string arg in cliArgs) {
                if (arg.ToLower().Trim() == flag.ToLower().Trim()) {
                    return true;
                }
            }
            return false;
        }

        private static string ReadEnvVar(string name, string defaultValue) {
            return Core.Env.EnvVar(name, defaultValue);
        }

        private static string PromptUser(string message) {
            Console.WriteLine(message);
            return "" + Console.ReadLine();
        }
    }
}