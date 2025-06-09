using System;
using System.IO;
using System.Collections.Generic;
using System.Resources;
using System.Text.Json;
using System.Collections.Generic;

//using RulesEngine;
using RulesEngine.Actions;
using RulesEngine.Models;
using RulesEngine.Interfaces;
using App.IO;

namespace App {
    class Program {
        private static string[] cliArgs = [];

        static async Task<int> Main(string[] args) {
            cliArgs = args;
            string func = GetRunFunction(args);
            Console.WriteLine("run function: " + func);
            DotNetEnv.Env.Load();

            switch (func) {
                case "env":
                    await EnvExamples();
                    break;
                case "adhoc":
                    await AdHoc();
                    break;
                case "rule_examples1":
                    await RuleExamples1();
                    break;
                default:
                    Console.WriteLine("Undefined function given on command-line; " + func);
                    Console.WriteLine("Command-line examples:");
                    Console.WriteLine("  dotnet run env");
                    Console.WriteLine("  dotnet run rule_examples1");
                    Console.WriteLine("  dotnet run adhoc");
                    break;
            }

            return 0;
        }

        private static async Task EnvExamples() {
            Console.WriteLine("pwd:        " + Core.Env.Pwd());
            Console.WriteLine("home:       " + Core.Env.HomeDir());
            Console.WriteLine("os arch:    " + Core.Env.OsArch());
            Console.WriteLine("os desc:    " + Core.Env.OsDesc());
            Console.WriteLine("is windows: " + Core.Env.IsWindows());
            Console.WriteLine("is macos:   " + Core.Env.IsMacOS());
            Console.WriteLine("is linux:   " + Core.Env.IsLinux());
            await Task.Delay(0);
        }

        private static async Task RuleExamples1() {
            // EOD 6/4 - see repos/ChatWithYourBusinessRules/experiments/ExpToRules02/Program.cs 
            // https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/identifier-names

            List<Rule> rules = new List<Rule>();
            FileIO fileIo = new FileIO();
            
            string temperature = ConsoleIO.PromptUser("Temperature: ");
            string usStateAbbrev = ConsoleIO.PromptUser("US State Abbreviation: ").ToUpper();
            
            Rule rule1 = new Rule();
            rule1.RuleName = "TemperatureIsBoiling";
            rule1.SuccessEvent = "Temperature is above the boiling point";
            rule1.ErrorMessage = "Temperature is below the boiling point";
            rule1.Expression = "Convert.ToInt32(input1.temperature) >= 220";
            rule1.RuleExpressionType = RuleExpressionType.LambdaExpression;
            // NOTE: Beware of using keywords like 'count' in expressions!

            Rule rule2 = new Rule();
            rule2.RuleName = "StateIsNC";
            rule2.SuccessEvent = "State is North Carolina.";
            rule2.ErrorMessage = "State is not North Carolina.";
            rule2.Expression = "Convert.ToString(input1.state) == \"NC\"";
            rule2.RuleExpressionType = RuleExpressionType.LambdaExpression;
            rule2.Actions = new RuleActions {
                OnSuccess = new ActionInfo {
                    Name = "OutputExpression",
                    Context = new Dictionary<string, object> {
                        { "Expression", "input1.state" }
                    }
                }
            };
                
            rules.Add(rule1);
            rules.Add(rule2);
            
            Workflow wf1 = new Workflow();
            wf1.WorkflowName = "wf1";
            wf1.Rules = rules;

            var re = new RulesEngine.RulesEngine();
            re.AddWorkflow(wf1);
            var input1 = new Dictionary<string, object>();
            input1.Add("temperature", temperature);
            input1.Add("state", usStateAbbrev);
            Console.WriteLine("Input1:");
            fileIo.LogObjectAsJson(input1);
            
            List<RuleResultTree> resultList = await re.ExecuteAllRulesAsync("wf1", input1);
            var resultsDict = new Dictionary<string, bool>();
            
            foreach (var result in resultList) {
                string ruleName = result.Rule.RuleName;
                resultsDict.Add(ruleName, result.IsSuccess);
                Console.WriteLine($"Rule - {result.Rule.RuleName}, IsSuccess - {result.IsSuccess}, Ex: {result.ExceptionMessage}");
                Console.WriteLine($"ActionResult.Output - {result.ActionResult.Output}");
            }
            fileIo.LogObjectAsJson(resultsDict);

            await Task.Delay(0);
        }

        private static async Task AdHoc() {
            await Task.Delay(0);
            string infile = "rules/sample_workflow1.json";
            Console.WriteLine($"Workflow: {infile}");
            FileIO fileIo = new FileIO();
            List<Dictionary<string, object>>? wf = fileIo.ReadJsonDictionaryList(infile);
            fileIo.LogObjectAsJson(wf);
            
            infile = "rules/sample_rule1.json";
            Console.WriteLine($"Rule: {infile}");
            Dictionary<string, object>? rule = fileIo.ReadJsonDictionary(infile);
            fileIo.LogObjectAsJson(rule);
        }
        
        private static string GetRunFunction(string[] args) {
            if ((args != null) && (args.Length > 0)) {
                return args[0].ToLower();
            }
            else {
                return "";
            }
        }

        private static string ReadEnvVar(string name, string defaultValue) {
            return Core.Env.EnvVar(name, defaultValue);
        }
    }
}