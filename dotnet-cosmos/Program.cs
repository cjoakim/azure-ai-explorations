
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
            case "azure_env":
                DisplayAzureEnv();
                break;
            case "cosmos_install_index_policy":
                return await CosmosInstallIndexPolicy(args);
            case "cosmos_seq_load_container":
                return await CosmosSeqLoadContainer(args);
            case "cosmos_bulk_load_container":
                return await CosmosBulkLoadContainer(args);
            case "cosmos_queries":
                return await CosmosQueries(args);
            default:
                Log("Undefined function given on command-line; " + func);
                Log("Command-line examples:");
                Log("  dotnet run azure_env");
                Log("  dotnet run cosmos_install_index_policy");
                Log("  dotnet run cosmos_seq_load_libraries");
                Log("  dotnet run cosmos_bulk_load_libraries");
                Log("  dotnet run cosmos_queries");
                break;
        }
        return 1;
    }

    private static void DisplayAzureEnv()
    {
        Console.WriteLine("pwd:        " + App.Core.Env.Pwd());
        Console.WriteLine("home:       " + App.Core.Env.HomeDir());
        Console.WriteLine("os arch:    " + App.Core.Env.OsArch());
        Console.WriteLine("os desc:    " + App.Core.Env.OsDesc());
        Console.WriteLine("is windows: " + App.Core.Env.IsWindows());
        Console.WriteLine("is macos:   " + App.Core.Env.IsMacOS());
        Console.WriteLine("is linux:   " + App.Core.Env.IsLinux());
    }


    static async Task<int> CosmosInstallIndexPolicy(string[] args)
    {
        // TODO - implement
        await Task.Delay(1);
        return 0; 
    }

    static async Task<int> CosmosSeqLoadContainer(string[] args)
    {
        // TODO - implement
        await Task.Delay(1);
        return 0; 
    }

    static async Task<int> CosmosBulkLoadContainer(string[] args)
    {
        // TODO - implement
        await Task.Delay(1);
        return 0; 
    }

    static async Task<int> CosmosQueries(string[] args)
    {
        // TODO - implement
        await Task.Delay(1);
        return 0; 
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