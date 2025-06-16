
using DotNetEnv;
using App.IO;

/**
 * Main program and entry point for this console/CLI app.
 * Chris Joakim, 2025
 */
class Program
{
    private static string[] cliArgs = [];

    static async Task<int> Main(string[] args)
    {
        cliArgs = args;
        string func = GetRunFunction(args);
        Log("run function: " + func);
        Env.Load();

        await Task.Delay(1);

        switch (func)
        {
            case "env":
                EnvExamples();
                break;
            case "io":
                IoExamples();
                break;
            case "paths":
                PathsExamples();
                break;
            default:
                Log("Undefined function given on command-line; " + func);
                Log("Command-line examples:");
                Log("  dotnet run env");
                Log("  dotnet run io");
                Log("  dotnet run paths");
                break;
        }
        return 0;
    }

    private static void EnvExamples()
    {
        Console.WriteLine("pwd:        " + App.Core.Env.Pwd());
        Console.WriteLine("home:       " + App.Core.Env.HomeDir());
        Console.WriteLine("os arch:    " + App.Core.Env.OsArch());
        Console.WriteLine("os desc:    " + App.Core.Env.OsDesc());
        Console.WriteLine("is windows: " + App.Core.Env.IsWindows());
        Console.WriteLine("is macos:   " + App.Core.Env.IsMacOS());
        Console.WriteLine("is linux:   " + App.Core.Env.IsLinux());
    }

    private static void IoExamples()
    {
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

    private static void PathsExamples()
    {
        Log("norm: " + Paths.Normalize(@"\"));
        Log("norm: " + Paths.Normalize(@"/"));
        Log("norm: " + Paths.Normalize(@"\Users\chris\github\cj-dotnet\Console1\Console1"));
        Log("norm: " + Paths.Normalize(@"/Users/chris/github/cj-dotnet/Console1/Console1"));
        Log("norm: " + Paths.Normalize(@"Program.cs"));
    }

    private static void Log(string msg)
    {
        Console.WriteLine(msg);
    }

    private static void LogConsoleHeader(string msg)
    {
        Console.WriteLine("========================================");
        Console.WriteLine(msg);
    }

    private static string GetRunFunction(string[] args)
    {
        if ((args != null) && (args.Length > 0))
        {
            return args[0].ToLower();
        }
        else
        {
            return "";
        }
    }

    private static bool CliFlagPresent(string flag)
    {
        foreach (string arg in cliArgs)
        {
            if (arg.ToLower().Trim() == flag.ToLower().Trim())
            {
                return true;
            }
        }

        return false;
    }

    private static string ReadEnvVar(string name, string defaultValue)
    {
        return App.Core.Env.EnvVar(name, defaultValue);
    }

    private static string PromptUser(string message)
    {
        Console.WriteLine(message);
        return "" + Console.ReadLine();
    }
}