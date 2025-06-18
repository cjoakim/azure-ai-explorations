
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.Azure.Cosmos;
using Newtonsoft.Json;

using DotNetEnv;

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
        Console.WriteLine("Program run function: " + func);
        
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
            case "cosmos_smoketest":
                return await CosmosSmokeTest(args);
            default:
                Console.WriteLine("Undefined function given on command-line; " + func);
                Console.WriteLine("Command-line examples:");
                Console.WriteLine("  dotnet run azure_env");
                Console.WriteLine("  dotnet run cosmos_get_index_policy");
                Console.WriteLine("  dotnet run cosmos_create_container");
                Console.WriteLine("  dotnet run cosmos_create_container_with_vector_index");
                Console.WriteLine("  dotnet run cosmos_update_index_policy");
                Console.WriteLine("  dotnet run cosmos_seq_load_libraries");
                Console.WriteLine("  dotnet run cosmos_bulk_load_libraries");
                Console.WriteLine("  dotnet run cosmos_queries");
                Console.WriteLine("  dotnet run cosmos_smoketest");
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
                string jstr = AsJson(ip);
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
                string jstr = AsJson(ip0);
                Console.Write("===");
                Console.WriteLine("Current IndexingPolicy for " + dbName + "." + cName + ":");
                Console.WriteLine(jstr);
            }
            
            IndexingPolicy? ip2 = await cosmosUtil.UpdateIndexPolicy(dbName, cName, idxPolicyFile);
            if (ip2 != null) {
                string jstr = AsJson(ip2);
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

    static async Task<int> CosmosSmokeTest(string[] args)
    {
        await Task.Delay(1);
        int returnCode = 1;
        CosmosNoSqlUtil? cosmosUtil = null;
        string testDbName = "smoketest"; // ""test" + App.Core.Env.Epoch();
        Console.WriteLine("testDbName: " + testDbName);
        ContainerResponse? cResp = null;
        HttpStatusCode? statusCode = null;
        
        try {
            Console.WriteLine("CosmosNoSqlUtil constructor...");
            cosmosUtil = new CosmosNoSqlUtil();

            try {
                statusCode = await cosmosUtil.DeleteDatabaseAsync(testDbName);
                Console.WriteLine("DeleteDatabaseAsync returned: " + statusCode);
                await Task.Delay(2000);
            }
            catch (Exception ex) {
                // ignore the exception if the database does not exist
                Console.WriteLine("Exception in DeleteDatabaseAsync: " + ex.Message);
            }
            
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
            cResp = await cosmosUtil.CreateContainerAsync(testDbName, "c1");
            if (cResp != null) {
                Console.WriteLine("Container Resource.Id: " + cResp.Resource.Id);
                Console.WriteLine("Container StatusCode:  " + cResp.StatusCode);
            }
            else {
                Console.WriteLine("Container c1 creation failed.");
            }
            
            Console.WriteLine("Creating container c2 in database " + testDbName);
            cResp = await cosmosUtil.CreateContainerAsync(testDbName, "c2");
            if (cResp != null) {
                Console.WriteLine("Container Resource.Id: " + cResp.Resource.Id);
                Console.WriteLine("Container StatusCode:  " + cResp.StatusCode);
            }
            else {
                Console.WriteLine("Container c3 creation failed.");
            }
            
            Console.WriteLine("Creating container v1 in database " + testDbName);
            cResp = await cosmosUtil.CreateContainerWithVectorIndexAsync(testDbName, "v1");
            if (cResp != null) {
                Console.WriteLine("Container Resource.Id: " + cResp.Resource.Id);
                Console.WriteLine("Container StatusCode:  " + cResp.StatusCode);
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
                string jstr = AsJson(idxPolicy);
                Console.WriteLine("IndexingPolicy JSON: " + jstr);
            }
            else {
                Console.WriteLine("IndexingPolicy for v1 is null");
            }
            
            Console.WriteLine("SetCurrentContainerAsync to: c1");
            await cosmosUtil.SetCurrentContainerAsync(testDbName, "c1");
            Console.WriteLine("GetCurrentContainerName: " + cosmosUtil.GetCurrentContainerName());

            // Create a document with nested objects
            var neighborhoods = new List<String>() { "river_run", "st_albans", "lake" };
            var restaurants = new Dictionary<string, int> {
                ["Brickhouse"] = 91,
                ["Sabi"] = 83,
                ["KingCanary"] = 77
            };
            var attractions = new Dictionary<string, object> {
                ["neighborhoods"] = neighborhoods,
                ["restaurants"] = restaurants
            };
            
            Dictionary<string, object> doc1 = new Dictionary<string, object>();
            var pk = "NC";
            var id1 = Guid.NewGuid().ToString();
            doc1.Add("id", id1);
            doc1.Add("pk", pk);
            doc1.Add("city", "Davidson");
            doc1.Add("population", 9876);
            doc1.Add("lat", 35.492543);
            doc1.Add("lng", -80.854912);
            doc1.Add("attractions", attractions);
            
            CosmosDocument doc2 = new CosmosDocument(doc1);
            doc2.EnsureId();
            doc2.SetId();
            Console.WriteLine("CosmosDocument HasAttribute pk: " + doc2.HasAttribute("pk"));
            Console.WriteLine("CosmosDocument HasAttribute xx: " + doc2.HasAttribute("xx"));
            ItemResponse<dynamic>? itemResp = await cosmosUtil.UpsertItemAsync(doc1, pk, null);
            itemResp = await cosmosUtil.UpsertItemAsync(doc2, pk, null);
            if (itemResp != null) {
                Console.WriteLine("UpsertItemAsync StatusCode:    " + itemResp.StatusCode);
                Console.WriteLine("UpsertItemAsync RequestCharge: " + itemResp.RequestCharge);
                Console.WriteLine("UpsertItemAsync Resource:\n" + AsJson(itemResp.Resource));
            }
            
            string id = doc2.GetId();
            ItemResponse<dynamic>? pointReadResp = await cosmosUtil.PointReadAsync(id, pk);
            if (pointReadResp != null) {
                Console.WriteLine("PointReadAsync StatusCode:    " + pointReadResp.StatusCode);
                Console.WriteLine("PointReadAsync RequestCharge: " + pointReadResp.RequestCharge);
                Console.WriteLine("PointReadAsync Resource:\n" + AsJson(pointReadResp.Resource));
            }
            
            string sql = "SELECT * FROM c WHERE c.pk = 'NC' and c.city = \"Davidson\"";
            Console.WriteLine("SQL Query 1: " + sql);
            List<dynamic> docs = await cosmosUtil.Query(sql, "NC");
            Console.WriteLine("Query Document count: " + docs.Count);
            docs.ForEach(doc => Console.WriteLine(AsJson(doc)));
            
            sql = "SELECT * FROM c WHERE c.city = \"Davidson\"";
            Console.WriteLine("SQL Query 2: " + sql);
            docs = await cosmosUtil.Query(sql);
            Console.WriteLine("Query Document count: " + docs.Count);
            docs.ForEach(doc => Console.WriteLine(AsJson(doc)));
            
            Console.WriteLine("Document count: " + await cosmosUtil.CountDocumentsInCurrentContainer());
            ItemResponse<dynamic>? deleteResp1 = await cosmosUtil.DeleteItemAsync(id1, pk);
            if (deleteResp1 != null) {
                Console.WriteLine("DeleteItemAsync 1 StatusCode:    " + deleteResp1.StatusCode);
                Console.WriteLine("DeleteItemAsync 1 RequestCharge: " + deleteResp1.RequestCharge);
            }
            ItemResponse<dynamic>? deleteResp2 = await cosmosUtil.DeleteItemAsync(id1, pk);
            if (deleteResp2 != null) {
                Console.WriteLine("DeleteItemAsync 2 StatusCode:    " + deleteResp2.StatusCode);
                Console.WriteLine("DeleteItemAsync 2 RequestCharge: " + deleteResp2.RequestCharge);
            }
            Console.WriteLine("Document count: " + await cosmosUtil.CountDocumentsInCurrentContainer());

            await cosmosUtil.SetCurrentContainerAsync(testDbName, "c1");
            List<CosmosDocument> bulkLoadDocs = new List<CosmosDocument>();
            for (int i = 1; i <= 1000; i++) {
                CosmosDocument doc = new CosmosDocument();
                if (i <= 25) {
                    doc["pk"] = "NC";
                }
                else {
                    doc["pk"] = "NC";
                }
                doc["city"] = "TestCity" + i;
                doc["population"] = 1000 + i;
                doc.EnsureId();
                bulkLoadDocs.Add(doc);
            }
            Console.WriteLine("Bulk loading " + bulkLoadDocs.Count + " documents into container c1");
            List<Dictionary<string, object>> results = 
                await cosmosUtil.BulkUpsertDocumentsAsync(bulkLoadDocs, "pk");
            Console.WriteLine(AsJson(results));
            Console.WriteLine(AsJson(results.Count));
            
            statusCode = await cosmosUtil.DeleteContainerAsync(testDbName, "c2");
            Console.WriteLine("DeleteContainerAsync c2 returned: " + statusCode);
        }
        catch (Exception ex) {
            Console.WriteLine("Exception in CosmosTest: " + ex.Message);
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

    private static string AsJson(object? obj, bool pretty = true) {
        if (obj == null) {
            return "null";
        }
        if (pretty) {
            return JsonConvert.SerializeObject(obj, Formatting.Indented);  
        }
        else {
            return JsonConvert.SerializeObject(obj);
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