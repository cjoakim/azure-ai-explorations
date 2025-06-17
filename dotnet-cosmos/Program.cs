
using System.Net;
using DotNetEnv;

using System.Text.Json;
    
using Microsoft.Azure.Cosmos;

using App.DB;
using App.Core;
using App.IO;
using Env = App.Core.Env;

/**
 * Main program and entry point for this console/CLI app.
 * Chris Joakim, 2025
 */
class Program
{
    private static string[] cliArgs = [];

    static async Task<int> Main(string[] args)
    {
        await Task.Delay(1);
        DotNetEnv.Env.Load();
        cliArgs = args;
        string func = "none";
        if (args.Length > 0) {
            func = args[0].ToLower();
        }
        Log("Program run function: " + func);
        
        switch (func)
        {
            case "azure_env":
                DisplayAzureEnv();
                return 0;
            case "cosmos_get_index_policy":
                return await CosmosGetIndexPolicy(args);
            case "cosmos_update_index_policy":
                return await CosmosUpdateIndexPolicy(args);
            case "cosmos_create_container":
                return await CosmosCreateContainer(args);
            case "cosmos_create_container_with_vector_index":
                return await CosmosCreateContainerWithVectorIndex(args);
            case "cosmos_seq_load_libraries":
                return await CosmosSeqLoadContainer(args);
            case "cosmos_bulk_load_container":
                return await CosmosBulkLoadContainer(args);
            case "cosmos_queries":
                return await CosmosQueries(args);
            case "cosmos_test":
                return await CosmosTest(args);
            default:
                Log("Undefined function given on command-line; " + func);
                Log("Command-line examples:");
                Log("  dotnet run azure_env");
                Log("  dotnet run cosmos_get_index_policy");
                Log("  dotnet run cosmos_create_container");
                Log("  dotnet run cosmos_create_container_with_vector_index");
                Log("  dotnet run cosmos_update_index_policy");
                Log("  dotnet run cosmos_seq_load_libraries");
                Log("  dotnet run cosmos_bulk_load_libraries");
                Log("  dotnet run cosmos_queries");
                Log("  dotnet run cosmos_test");
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
        
        App.Core.Env.DisplayEnvVars();
    }

    static async Task<int> CosmosGetIndexPolicy(string[] args)
    {
        await Task.Delay(1);
        int returnCode = 1;
        CosmosNoSqlUtil? cosmosUtil = null;
        
        try {
            cosmosUtil = new CosmosNoSqlUtil();
            var dbName = App.Core.Env.EnvVar("AZURE_COSMOSDB_NOSQL_DATABASE", "?");
            var cName  = App.Core.Env.EnvVar("AZURE_COSMOSDB_NOSQL_CONTAINER", "?");
            Console.WriteLine("dbName: " + dbName);
            Console.WriteLine("cName:  " + cName);

            IndexingPolicy? ip = await cosmosUtil.GetIndexPolicy(dbName, cName);
            if (ip != null) {
                Console.WriteLine("ip: " + ip.GetType().Name);
                string jstr = JsonSerializer.Serialize(
                    ip, new JsonSerializerOptions { WriteIndented = true });
                Console.Write("===");
                Console.WriteLine("Current IndexingPolicy for " + dbName + "." + cName + ":");
                Console.WriteLine(jstr);
            }
            else {
                Console.WriteLine("IndexingPolicy is null");
            }

            returnCode = 0;
        }
        catch (Exception ex) {
            Console.WriteLine("Exception in CosmosInstallIndexPolicy: " + ex.Message);
            Console.WriteLine(ex.StackTrace);
            returnCode = 1;
        }
        finally {
            if (cosmosUtil != null) {
                cosmosUtil.Close();
            }
        }

        return returnCode;

    }
    
    static async Task<int> CosmosUpdateIndexPolicy(string[] args)
    {
        await Task.Delay(1);
        int returnCode = 1;
        CosmosNoSqlUtil? cosmosUtil = null;
        
        try {
            cosmosUtil = new CosmosNoSqlUtil();
            var dbName = App.Core.Env.EnvVar("AZURE_COSMOSDB_NOSQL_DATABASE", "?");
            var cName  = App.Core.Env.EnvVar("AZURE_COSMOSDB_NOSQL_CONTAINER", "?");
            var idxPolicyFile = App.Core.Env.EnvVar(
                "AZURE_COSMOSDB_NOSQL_INDEX_POLICY_FILE", "cosmos/index-policy.json");
            Console.WriteLine("dbName: " + dbName);
            Console.WriteLine("cName:  " + cName);
            Console.WriteLine("idxPolicyFile: " + idxPolicyFile);
            
            IndexingPolicy? ip0 = await cosmosUtil.GetIndexPolicy(dbName, cName);
            if (ip0 != null) {
                string jstr = JsonSerializer.Serialize(
                    ip0, new JsonSerializerOptions { WriteIndented = true });
                Console.Write("===");
                Console.WriteLine("Current IndexingPolicy for " + dbName + "." + cName + ":");
                Console.WriteLine(jstr);
            }
            
            IndexingPolicy? ip2 = await cosmosUtil.UpdateIndexPolicy(dbName, cName, idxPolicyFile);
            if (ip2 != null) {
                string jstr = JsonSerializer.Serialize(
                    ip2, new JsonSerializerOptions { WriteIndented = true });
                Console.Write("===");
                Console.WriteLine("Updated IndexingPolicy for " + dbName + "." + cName + ":");
                Console.WriteLine(jstr);
            }
            else {
                Console.WriteLine("IndexingPolicy is null");
            }

            returnCode = 0;
        }
        catch (Exception ex) {
            Console.WriteLine("Exception in CosmosInstallIndexPolicy: " + ex.Message);
            Console.WriteLine(ex.StackTrace);
            returnCode = 1;
        }
        finally {
            if (cosmosUtil != null) {
                cosmosUtil.Close();
            }
        }

        return returnCode;

    }

    
    /**
     * Create a Cosmos DB NoSQL container.
     * The parameters are read from environment variables, some have sensible defaults.
     */
    static async Task<int> CosmosCreateContainer(string[] args) {
        await Task.Delay(1);
        int returnCode = 1;
        CosmosNoSqlUtil? cosmosUtil = null;

        try {
            cosmosUtil = new CosmosNoSqlUtil();
            var dbName = Env.EnvVar("AZURE_COSMOSDB_NOSQL_DATABASE", "?");
            var cName  = Env.EnvVar("AZURE_COSMOSDB_NOSQL_CONTAINER", "?");
            var pkPath = Env.EnvVar("AZURE_COSMOSDB_NOSQL_PK_PATH", "/pk");
            var throughput= Int32.Parse(Env.EnvVar("AZURE_COSMOSDB_NOSQL_CONTAINER_RU", "4000"));

            Console.WriteLine("CosmosCreateVectorContainer parameters:");
            Console.WriteLine("  dbName:     " + dbName);
            Console.WriteLine("  cName:      " + cName);
            Console.WriteLine("  pkPath:     " + pkPath);
            Console.WriteLine("  throughput: " + throughput);

            ContainerResponse? resp = await cosmosUtil.CreateContainerAsync(
                dbName, cName, pkPath, throughput);

            if (resp != null) {
                Console.WriteLine("Response StatusCode: " + resp.StatusCode);
                if (resp.StatusCode < HttpStatusCode.Ambiguous) {  // Ambiguous = 300
                    returnCode = 0;
                }
            }
        }
        catch (Exception e) {
            Console.WriteLine(e);
        }
        return returnCode;
    }
    
    
    
    
    
    
    /**
     * Create a Cosmos DB NoSQL container with vector index.
     * The parameters are read from environment variables, some have sensible defaults.
     */
    static async Task<int> CosmosCreateContainerWithVectorIndex(string[] args) {
        await Task.Delay(1);
        int returnCode = 1;
        CosmosNoSqlUtil? cosmosUtil = null;

        try {
            cosmosUtil = new CosmosNoSqlUtil();
            var dbName = Env.EnvVar("AZURE_COSMOSDB_NOSQL_DATABASE", "?");
            var cName  = Env.EnvVar("AZURE_COSMOSDB_NOSQL_CONTAINER", "?");
            var pkPath = Env.EnvVar("AZURE_COSMOSDB_NOSQL_PK_PATH", "/pk");
            var throughput= Int32.Parse(Env.EnvVar("AZURE_COSMOSDB_NOSQL_CONTAINER_RU", "4000"));
            var embeddingPath = Env.EnvVar("AZURE_COSMOSDB_NOSQL_EMBEDDING_PATH", "/embedding");
            var embeddingDimensions= Int32.Parse(Env.EnvVar("AZURE_COSMOSDB_NOSQL_EMBEDDING_DIMENSIONS", "1536"));
            var distanceFunction = Env.EnvVar("AZURE_COSMOSDB_NOSQL_DISTANCE_FUNCTION", "cosine");
            var indexType = Env.EnvVar("AZURE_COSMOSDB_NOSQL_VECTOR_INDEX_TYPE", "diskann");
            
            Console.WriteLine("CosmosCreateVectorContainer parameters:");
            Console.WriteLine("  dbName:              " + dbName);
            Console.WriteLine("  cName:               " + cName);
            Console.WriteLine("  pkPath:              " + pkPath);
            Console.WriteLine("  throughput:          " + throughput);
            Console.WriteLine("  embeddingPath:       " + embeddingPath);
            Console.WriteLine("  embeddingDimensions: " + embeddingDimensions);
            Console.WriteLine("  distanceFunction:    " + distanceFunction);
            Console.WriteLine("  indexType:           " + indexType);

            ContainerResponse? resp = await cosmosUtil.CreateContainerWithVectorIndexAsync(
                dbName, cName, pkPath, throughput, 
                embeddingPath, embeddingDimensions,
                distanceFunction, indexType);

            if (resp != null) {
                Console.WriteLine("Response StatusCode: " + resp.StatusCode);
                if (resp.StatusCode < HttpStatusCode.Ambiguous) {  // Ambiguous = 300
                    returnCode = 0;
                }
            }
        }
        catch (Exception e) {
            Console.WriteLine(e);
        }
        return returnCode;
    }
    static async Task<int> CosmosSeqLoadContainer(string[] args)
    {
        // TODO - implement

        await Task.Delay(1);
        int returnCode = 1;
        CosmosNoSqlUtil? cosmosUtil = null;
        
        try {
            cosmosUtil = new CosmosNoSqlUtil();

            returnCode = 0;
        }
        catch (Exception ex) {
            Console.WriteLine("Exception in CosmosSeqLoadContainer: " + ex.Message);
            Console.WriteLine(ex.StackTrace);
            returnCode = 1;
            
        }
        finally {
            if (cosmosUtil != null) {
                cosmosUtil.Close();
            }
        }

        return returnCode;
    }

    static async Task<int> CosmosBulkLoadContainer(string[] args)
    {
        await Task.Delay(1);
        int returnCode = 1;
        CosmosNoSqlUtil? cosmosUtil = null;
        
        try {
            cosmosUtil = new CosmosNoSqlUtil();

            returnCode = 0;
        }
        catch (Exception ex) {
            Console.WriteLine("Exception in CosmosBulkLoadContainer: " + ex.Message);
            Console.WriteLine(ex.StackTrace);
            returnCode = 1;
            
        }
        finally {
            if (cosmosUtil != null) {
                cosmosUtil.Close();
            }
        }
        return returnCode;
    }

    static async Task<int> CosmosQueries(string[] args)
    {
        // TODO - implement
        await Task.Delay(1);
        int returnCode = 1;
        CosmosNoSqlUtil? cosmosUtil = null;
        
        try {
            cosmosUtil = new CosmosNoSqlUtil();


            returnCode = 0;
        }
        catch (Exception ex) {
            Console.WriteLine("Exception in CosmosQueries: " + ex.Message);
            Console.WriteLine(ex.StackTrace);
            returnCode = 1;
            
        }
        finally {
            if (cosmosUtil != null) {
                cosmosUtil.Close();
            }
        }
        return returnCode;
    }

    static async Task<int> CosmosTest(string[] args)
    {
        // TODO - implement
        await Task.Delay(1);
        int returnCode = 1;
        CosmosNoSqlUtil? cosmosUtil = null;
        string testDbName = "test" + App.Core.Env.Epoch();
        Console.WriteLine("testDbName: " + testDbName);
        
        try {
            Console.WriteLine("CosmosNoSqlUtil constructor...");
            cosmosUtil = new CosmosNoSqlUtil();
            
            Console.WriteLine("CreateDatabaseAsync: " + testDbName);
            await cosmosUtil.CreateDatabaseAsync(testDbName);
            await Task.Delay(2000);
            
            List<string>? dbList = await cosmosUtil.ListDatabasesAsync();
            if (dbList != null) {
                Console.WriteLine("Databases in Cosmos DB account:");
                foreach (string dbName in dbList) {
                    Console.WriteLine("  " + dbName);
                }
            }
            else {
                Console.WriteLine("No databases found.");
            }

            Console.WriteLine("SetCurrentDatabaseAsync to: " + testDbName);
            await cosmosUtil.SetCurrentDatabaseAsync(testDbName);
            Console.WriteLine("GetCurrentDatabaseName: " + cosmosUtil.GetCurrentDatabaseName());
            
            Console.WriteLine("Creating container c1 in database " + testDbName);
            ContainerResponse? cResp1 = 
                await cosmosUtil.CreateContainerAsync(testDbName, "c1");
            if (cResp1 != null) {
                Console.WriteLine("Container created: " + cResp1.Resource.Id);
                Console.WriteLine("Container StatusCode: " + cResp1.StatusCode);
            }
            else {
                Console.WriteLine("Container c1 creation failed.");
            }
            
            Console.WriteLine("Creating container v1 in database " + testDbName);
            ContainerResponse? cResp2 = 
                await cosmosUtil.CreateContainerWithVectorIndexAsync(testDbName, "v1");
            if (cResp2 != null) {
                Console.WriteLine("Container created: " + cResp2.Resource.Id);
                Console.WriteLine("Container StatusCode: " + cResp2.StatusCode);
            }
            else {
                Console.WriteLine("Container v1 creation failed.");
            }

            List<string>? cList = await cosmosUtil.ListContainersAsync(testDbName);
            if (cList != null) {
                Console.WriteLine("Containers in database: " + testDbName);
                foreach (string c in cList) {
                    Console.WriteLine("  " + c);
                }
            }
            else {
                Console.WriteLine("No databases found.");
            }
            
            IndexingPolicy? idxPolicy = await cosmosUtil.GetIndexPolicy(testDbName, "v1");
            if (idxPolicy != null) {
                Console.WriteLine("IndexingPolicy for v1: " + idxPolicy.GetType().Name);
                string jstr = JsonSerializer.Serialize(
                    idxPolicy, new JsonSerializerOptions { WriteIndented = true });
                Console.WriteLine("IndexingPolicy JSON: " + jstr);
            }
            else {
                Console.WriteLine("IndexingPolicy for v1 is null");
            }

        }
        catch (Exception ex) {
            Console.WriteLine("Exception in CosmosTest: " + ex.Message);
            Console.WriteLine(ex.StackTrace);
            returnCode = 1;
            
        }
        finally {
            if (cosmosUtil != null) {
                Console.WriteLine("Pausing for 60 seconds before deleting the test database...");
                await Task.Delay(60 * 1000);
                
                HttpStatusCode? statusCode = await cosmosUtil.DeleteContainerAsync(testDbName, "c1");
                Console.WriteLine("DeleteContainerAsync c1 returned: " + statusCode);
                
                statusCode = await cosmosUtil.DeleteDatabaseAsync(testDbName);
                Console.WriteLine("DeleteDatabaseAsync returned: " + statusCode);
                cosmosUtil.Close();
            }
        }
        return returnCode;
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