using App.Core;
using App.IO;
using Azure.Identity;
using Microsoft.Azure.Cosmos;
using Newtonsoft.Json;
//using Azure.ResourceManager;
//using Azure.ResourceManager.Resources;
//using Azure.ResourceManager.CosmosDB;
//using Azure.ResourceManager.CosmosDB.Models;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Net;
using System.Runtime.InteropServices.Swift;
using Microsoft.Extensions.Azure;
using Newtonsoft.Json.Linq;

namespace App.DB;

/**
 * This class is used to access the Azure Cosmos DB NoSQL API
 * via the asynchronous SDK methods.
 * Chris Joakim, 2025
 */
public class CosmosNoSqlUtil {
    // Instance variables
    private CosmosClient? cosmosClient = null;
    private Database? currentDatabase = null;
    private Container? currentContainer = null;
    private string currentDatabaseName = "";
    private string currentContainerName = "";

    /**
     * Constructor method for CosmosNoSqlUtil.
     * All parameters are read from environment variables.
     */
    public CosmosNoSqlUtil() {
        var authType = Env.EnvVar("AZURE_COSMOSDB_NOSQL_AUTH_TYPE", "key").ToLower();
        var uri = Env.EnvVar("AZURE_COSMOSDB_NOSQL_URI", "None");
        var opts = new CosmosClientOptions() { AllowBulkExecution = true };
        Console.WriteLine("CosmosNoSqlUtil authType: " + authType);
        Console.WriteLine("CosmosNoSqlUtil uri: " + uri);

        // Create the CosmosClient instance
        if (authType.Equals("key")) {
            var key = Env.EnvVar("AZURE_COSMOSDB_NOSQL_KEY", "None");
            Console.WriteLine("CosmosNoSqlUtil key: " + key);
            cosmosClient = new CosmosClient(uri, key, opts);
        }
        else {
            cosmosClient = new CosmosClient(uri, new DefaultAzureCredential(), opts);
        }
    }

    /**
     * Close the cosmosClient.  Invoke this method before application exit.
     */
    public bool Close() {
        if (cosmosClient != null) {
            Console.Write("CosmosNoSqlUtil Disposing CosmosClient ... ");
            cosmosClient.Dispose();
            return true;
        }
        return false;
    }

    // ========== Simple Getters and Setters  ==========
    
    public string GetCurrentDatabaseName() {
        return currentDatabaseName;
    }
    
    public Database? GetCurrentDatabase() {
        return currentDatabase;
    }
    
    public string GetCurrentContainerName() {
        return currentContainerName;
    }
    
    public Container? GetCurrentContainer() {
        return currentContainer;
    }
    
    //  ========== Database Methods  ==========
    
    public async Task<List<string>?> ListDatabasesAsync() {
        List<string>? dbList = null;
        if (cosmosClient != null) {
            dbList = new List<string>();
            using (FeedIterator<DatabaseProperties> iterator = 
                   cosmosClient.GetDatabaseQueryIterator<DatabaseProperties>()) {
                while (iterator.HasMoreResults) {
                    foreach (DatabaseProperties db in await iterator.ReadNextAsync()) {
                        dbList.Add(db.Id);
                    }
                }
            }
        }
        return dbList;
    }

    public async Task<Database?> CreateDatabaseAsync(string dbName, int dbLevelThroughput = 0) {
        if (cosmosClient != null) {
            if (dbLevelThroughput > 0) {
                DatabaseResponse response = await cosmosClient.CreateDatabaseIfNotExistsAsync(
                    dbName, throughput: dbLevelThroughput);
                return response.Database;
            }
            else {
                DatabaseResponse response = await cosmosClient.CreateDatabaseIfNotExistsAsync(
                    dbName);
                return response.Database; 
            }
        }
        return null;
    }
    
    public async Task<string?> SetCurrentDatabaseAsync(string dbName) {
        if (cosmosClient != null) {
            Database db = cosmosClient.GetDatabase(dbName);
            DatabaseResponse response = await db.ReadAsync();
            currentDatabase = response.Database;
            if (currentDatabase != null) {
                currentDatabaseName = dbName;
            }
            return GetCurrentDatabaseName();
        }
        return null;
    }
    
    public async Task<Database?> GetDatabaseAsync(string dbName) {
        if (cosmosClient != null) {
            Database db = cosmosClient.GetDatabase(dbName);
            DatabaseResponse response = await db.ReadAsync();
            return response.Database;
        }

        return null;
    }
    
    public async Task<HttpStatusCode?> DeleteDatabaseAsync(string dbName) {
        if (cosmosClient != null) {
            Database? db = await GetDatabaseAsync(dbName);
            if (db != null) {
                DatabaseResponse resp = await db.DeleteAsync();
                return resp.StatusCode;
            }
        }
        return null;
    }
    
    //  ========== Container Methods  ==========

    public async Task<List<string>?> ListContainersAsync(string dbName) {
        List<string>? cList = null;
        if (cosmosClient != null) {
            cList = new List<string>();
            Database? db = await GetDatabaseAsync(dbName);
            if (db != null) {
                FeedIterator<ContainerProperties> containerIterator = 
                    db.GetContainerQueryIterator<ContainerProperties>();
                while (containerIterator.HasMoreResults) {
                    FeedResponse<ContainerProperties> response = await containerIterator.ReadNextAsync();
                    foreach (ContainerProperties container in response) {
                        cList.Add(container.Id);
                    }
                }
            }
        }
        return cList;
    }
    
    /**
    * Create a Cosmos DB NoSQL container per the given parameters.
    * Only the dbName and cName parameters are required; the others have sensible defaults.
    * See https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/how-to-dotnet-vector-index-query
    */
    public async Task<ContainerResponse?> CreateContainerAsync(
        string dbName, 
        string cName, 
        string pkPath = "/pk", 
        int    throughput = 4000
    ) {
        if (cosmosClient == null) return null;
        
        Database? db = await GetDatabaseAsync(dbName);
        if (db != null) {
            ContainerProperties containerProperties = new ContainerProperties(
                id: cName, partitionKeyPath: pkPath);
            ThroughputProperties throughputProperties = 
                ThroughputProperties.CreateAutoscaleThroughput(throughput); 
            containerProperties.IndexingPolicy.IncludedPaths.Add(new IncludedPath { Path = "/*" });    
            return await db.CreateContainerAsync(containerProperties, throughputProperties);
        }
        return null;
    }
    
    /**
    * Create a Cosmos DB NoSQL container with vector index per the given parameters.
    * Only the dbName and cName parameters are required; the others have sensible defaults.
    * See https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/how-to-dotnet-vector-index-query
    */
    public async Task<ContainerResponse?> CreateContainerWithVectorIndexAsync(
        string dbName, 
        string cName, 
        string pkPath = "/pk", 
        int    throughput = 4000,
        string embeddingPath = "/embedding", 
        int    embeddingDimensions = 1536,
        string distanceFunction = "cosine",  // "euclidean", "dotproduct", or "cosine"
        string indexType = "diskann"         // "flat", "quantizedflat", or "diskann"
        ) {
        if (cosmosClient == null) return null;
        
        string dfName = ("" + distanceFunction).ToLower().Trim();
        DistanceFunction df = DistanceFunction.Cosine;
        switch (dfName) {
            case "euclidean":
                df = DistanceFunction.Euclidean;
                break;
            case "dotproduct":
                df = DistanceFunction.DotProduct;
                break;
            default:
                df = DistanceFunction.Cosine;
                break;
        }
        
        string indexTypeName = ("" + indexType).ToLower().Trim();
        VectorIndexType vIdxType = VectorIndexType.DiskANN;
        switch (indexTypeName) {
            case "flat":
                vIdxType = VectorIndexType.Flat;
                break;
            case "quantizedflat":
                vIdxType = VectorIndexType.QuantizedFlat;
                break;
            default:
                vIdxType = VectorIndexType.DiskANN;
                break;
        }
        
        Database? db = await GetDatabaseAsync(dbName);
        if (db != null) {
            List<Embedding> embeddingList = new List<Embedding>() {
                new Embedding() {
                    Path = embeddingPath,
                    DataType = VectorDataType.Float32,
                    DistanceFunction = df,
                    Dimensions = embeddingDimensions
                }
            };
            Collection<Embedding> collection = new Collection<Embedding>(embeddingList);
            ContainerProperties containerProperties = new ContainerProperties(
                id: cName, partitionKeyPath: pkPath) {   
                VectorEmbeddingPolicy = new(collection),
                IndexingPolicy = new IndexingPolicy() {
                    VectorIndexes = new() {
                        new VectorIndexPath() {
                            Path = embeddingPath,
                            Type = vIdxType,
                        }
                    }
                },
            };
            ThroughputProperties throughputProperties = 
                ThroughputProperties.CreateAutoscaleThroughput(throughput); 
            containerProperties.IndexingPolicy.IncludedPaths.Add(new IncludedPath { Path = "/*" });    
            containerProperties.IndexingPolicy.ExcludedPaths.Add(new ExcludedPath { Path = embeddingPath + "/*" });
            
            return await db.CreateContainerAsync(containerProperties, throughputProperties);
        }
        return null;
    }

    public async Task<string?> SetCurrentContainerAsync(string dbName, string cName) {
        if (cosmosClient != null) {
            Database db = cosmosClient.GetDatabase(dbName);
            DatabaseResponse dbResponse = await db.ReadAsync();
            currentDatabase = dbResponse.Database;
            if (currentDatabase != null) {
                currentDatabaseName = dbName;
                currentDatabase.GetContainer(cName);
                ContainerResponse cResponse = await db.GetContainer(cName).ReadContainerAsync();
                if (cResponse != null) {
                    currentContainerName = cName;
                    currentContainer = cResponse.Container;
                    return GetCurrentContainerName();
                }
            }
        }
        return null;
    }

    public async Task<HttpStatusCode?> DeleteContainerAsync(string dbName, string cName) {
        if (cosmosClient != null) {
            Database? db = await GetDatabaseAsync(dbName);
            if (db != null) {
                Container c = db.GetContainer(cName);
                ContainerResponse resp = await c.DeleteContainerAsync();
                return resp.StatusCode;
            }
        }
        return null;
    }

    public async Task<IndexingPolicy?> GetIndexPolicy(string dbName, string cName) {
        if (cosmosClient != null) {
            Console.WriteLine($"CosmosNoSqlUtil#GetIndexPolicy - dbName: {dbName} cName: {cName}");
            ContainerResponse containerResponse =
                await cosmosClient.GetContainer(dbName, cName).ReadContainerAsync();
            IndexingPolicy indexingPolicy = containerResponse.Resource.IndexingPolicy;
            return indexingPolicy;
        }
        return null;
    }
    
    public async Task<IndexingPolicy?> UpdateIndexPolicy(string dbName, string cName, string idxPolicyFile) {
        if (cosmosClient != null) {
            Console.WriteLine(
                $"CosmosNoSqlUtil#UpdateIndexPolicy - dbName: {dbName} cName: {cName} idxPolicyFile: {idxPolicyFile}");
            FileIO fio = new FileIO();
            string jstr = fio.ReadText(idxPolicyFile);
            IndexingPolicy? newPolicy = JsonConvert.DeserializeObject<IndexingPolicy>(jstr);
            if (newPolicy != null) {
                Console.WriteLine($"CosmosNoSqlUtil#UpdateIndexPolicy - newPolicy: {newPolicy}");
                Database? database = await GetDatabaseAsync(dbName);
                if (database != null) {
                    Container container = database.GetContainer(cName);
                    if (container != null) {
                        ContainerResponse cProps = await container.ReadContainerAsync();
                        cProps.Resource.IndexingPolicy = newPolicy;
                        await container.ReplaceContainerAsync(cProps.Resource);
                        await Task.Delay(3000); // wait for the indexing policy to be applied
                        return await GetIndexPolicy(dbName, cName);
                    }
                }
            }
            else {
                Console.WriteLine(
                    $"CosmosNoSqlUtil#UpdateIndexPolicy - failed to deserialize IndexingPolicy from file: {idxPolicyFile}");
            }
        }
        return null;
    }

    //  ========== CRUD Methods  ==========

    public async Task<ItemResponse<dynamic>?> UpsertItemAsync(dynamic doc, string pk, ItemRequestOptions? options) {
        if (cosmosClient == null) return null;
        if (currentContainer == null) return null;

        try {
            if (options == null) {
                return await currentContainer.UpsertItemAsync<dynamic>(
                    item: doc,
                    partitionKey: new PartitionKey(pk)
                );
            }
            else {
                return await currentContainer.UpsertItemAsync<dynamic>(
                    item: doc,
                    partitionKey: new PartitionKey(pk),
                    requestOptions: options
                );
            }
        }
        catch (Exception e) {
            Console.WriteLine("CosmosNoSqlUtil#UpsertItemAsync - Exception: " + e.Message);
        }
        return null;
    }
    
    public async Task<ItemResponse<dynamic>?> DeleteItemAsync(string id, string pk) {
        if (cosmosClient == null) return null;
        if (currentContainer == null) return null;

        try {
            return await currentContainer.DeleteItemAsync<object>(
                id, new PartitionKey(pk));
        }
        catch (Exception e) {
            Console.WriteLine("CosmosNoSqlUtil#DeleteItemAsync - Exception: " + e.Message);
        }
        return null;
    }

    /**
     *
     * See https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/tutorial-dotnet-bulk-import
     */
    public async Task<List<HttpStatusCode>?> BulkUpsertDocumentsAsync(
        List<CosmosDocument> docs, string pkAttr = "pk") {
        
        if (cosmosClient == null) return null;
        if (currentContainer == null) return null;
        Container container = currentContainer;
        List<Task> tasks = new List<Task>();
        List<HttpStatusCode> statusCodes = new List<HttpStatusCode>();
        
        try {
            for (int i = 0; i < docs.Count; i++) {
                CosmosDocument doc = docs[i];
                doc.EnsureId();
                PartitionKey pk = new PartitionKey(doc.GetStringAttribute(pkAttr));
                Console.WriteLine($"bulk upsert doc: {doc.GetId()} pk: {pk.ToString()}");
                Task t = container.UpsertItemAsync<CosmosDocument>(doc, pk);
                //container.UpsertItemAsync()
                // .ContinueWith(itemResponse => {
                //     HttpStatusCode statusCode = itemResponse.Result.StatusCode;
                //     Console.WriteLine($"bulk upsert sc: {statusCode} id: {doc.GetId()}");
                //     statusCodes.Add(statusCode);
                // });
                tasks.Add(t);
                
                // tasks.Add(currentContainer.CreateItemAsync(doc, pk).ContinueWith(
                //     itemResponse => 
                //         Console.WriteLine($"bulk load sc: {itemResponse.Result.StatusCode}")
                //         //statusCodes.Add(itemResponse.Result.StatusCode)
                //         ));
            }
            await Task.WhenAll(tasks);
        }
        catch (Exception e) {
            Console.WriteLine("CosmosNoSqlUtil#BulkLoadDocumentsAsync - Exception: " + e.Message);
            Console.WriteLine(e.StackTrace);
        }
        return statusCodes;
    }

    //  ========== Query Methods  ==========

    /**
     * Return the number of documents in the current container.
     */
    public async Task<int> CountDocumentsInCurrentContainer() {
        int count = -1;
        if (currentContainer != null) {
            try {
                QueryDefinition query = new QueryDefinition("SELECT VALUE COUNT(1) FROM c");
                FeedIterator<int> feedIterator = currentContainer.GetItemQueryIterator<int>(query);
                while (feedIterator.HasMoreResults) {
                    FeedResponse<int> response = await feedIterator.ReadNextAsync();
                    count += response.First();
                }
            }
            catch (Exception e) {
                Console.WriteLine("CosmosNoSqlUtil#CountDocumentsInCurrentContainer - Exception: " + e.Message);
            }
        }
        return count;
    }
    
    public async Task<List<dynamic>> Query(
        string sql, 
        string? pk = null,
        int maxItems = 100,
        string continuationToken = "") {
        
        List<dynamic> documentsList = new List<dynamic>();
        QueryRequestOptions requestOptions = new QueryRequestOptions() {
            MaxItemCount = maxItems
        };
        if (pk != null) {
            requestOptions.PartitionKey = new PartitionKey(pk);
        }
        
        if (currentContainer != null) {
            try {
                QueryDefinition query = new QueryDefinition(sql);
                FeedIterator<dynamic> feedIterator = 
                    currentContainer.GetItemQueryIterator<dynamic>(
                        query, null, requestOptions);
                while (feedIterator.HasMoreResults) {
                    FeedResponse<dynamic> response = await feedIterator.ReadNextAsync();
                    response.ToList().ForEach(doc => documentsList.Add(doc));
                }
            }
            catch (Exception e) {
                Console.WriteLine("CosmosNoSqlUtil#Query - Exception: " + e.Message);
            }
        }
        return documentsList;
    }
    
    public async Task<ItemResponse<dynamic>?> PointReadAsync(string id, string pk) {
        if (cosmosClient == null) return null;
        if (currentContainer == null) return null;
        try {
            return await currentContainer.ReadItemAsync<dynamic>(
                id: id,
                partitionKey: new PartitionKey(pk)
            );
        }
        catch (Exception e) {
            Console.WriteLine(e);
        }
        return null;
    }

}

/**
Python class CosmosNoSqlUtil method signatures:

async def count_documents(self):
async def execute_item_batch(self, item_operations: list, pk: str):

async def query_items(self, sql, cross_partition=False, pk=None, max_items=100):
async def parameterized_query(

async def get_database_throughput(self):
async def get_container_throughput(self):
async def get_container_properties(self) -> dict:
*/