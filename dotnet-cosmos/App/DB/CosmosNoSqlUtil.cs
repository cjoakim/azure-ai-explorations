using App.Core;
using App.IO;
using Azure.Identity;
using Microsoft.Azure.Cosmos;
using Newtonsoft.Json;
using Azure.ResourceManager;
using Azure.ResourceManager.Resources;
using Azure.ResourceManager.CosmosDB;
using Azure.ResourceManager.CosmosDB.Models;
using System.Collections.Generic;
using System.Collections.ObjectModel;
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
    private string currentDatabaseName = "";

    public CosmosNoSqlUtil() {
        var authType = Env.EnvVar("AZURE_COSMOSDB_NOSQL_AUTH_TYPE", "key").ToLower();
        var uri = Env.EnvVar("AZURE_COSMOSDB_NOSQL_URI", "None");
        Console.WriteLine("CosmosNoSqlUtil authType: " + authType);
        Console.WriteLine("CosmosNoSqlUtil uri: " + uri);

        // Create the CosmosClient instance
        if (authType.Equals("key")) {
            var key = Env.EnvVar("AZURE_COSMOSDB_NOSQL_KEY", "None");
            Console.WriteLine("CosmosNoSqlUtil key: " + key);
            cosmosClient = new CosmosClient(uri, key);
        }
        else {
            cosmosClient = new CosmosClient(uri, new DefaultAzureCredential());
        }
    }

    public void Close() {
        if (this.cosmosClient != null) {
            Console.Write("CosmosNoSqlUtil Disposing CosmosClient ... ");
            cosmosClient.Dispose();
        }
    }

    public async Task<bool> SetCurrentDatabaseAsync(string dbName) {
        if (cosmosClient != null) {
            Database db = cosmosClient.GetDatabase(dbName);
            DatabaseResponse response = await db.ReadAsync();
            this.currentDatabase = response.Database;
            if (this.currentDatabase != null) {
                this.currentDatabaseName = dbName;
            }

            return true;
        }

        return false;
    }

    public async Task<Database?> GetDatabaseAsync(string dbName) {
        if (cosmosClient != null) {
            Database db = cosmosClient.GetDatabase(dbName);
            DatabaseResponse response = await db.ReadAsync();
            return response.Database;
        }

        return null;
    }

    public async Task<Database?> CreateDatabaseAsync(string dbName, int dbLevelThroughput = 0) {
        if (cosmosClient != null) {
            DatabaseResponse response = await cosmosClient.CreateDatabaseIfNotExistsAsync(
                dbName, throughput: dbLevelThroughput);
            return response.Database;
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

    /**
     * The DiskANN Vector Index seems to be immutable, but the other IndexingPolicy
     * items can be updated.
     *
     * See https://docs.azure.cn/en-us/cosmos-db/nosql/how-to-manage-indexing-policy
     * "Currently, vector policies and vector indexes are immutable after creation. To make changes, please create a new collection"
     */
    public async Task<IndexingPolicy?> UpdateIndexPolicy(string dbName, string cName, string idxPolicyFile) {
        if (cosmosClient != null) {
            Console.WriteLine(
                $"CosmosNoSqlUtil#UpdateIndexPolicy - dbName: {dbName} cName: {cName} idxPolicyFile: {idxPolicyFile}");
            FileIO fio = new FileIO();
            string jstr = fio.ReadText(idxPolicyFile);
            IndexingPolicy? newPolicy = JsonConvert.DeserializeObject<IndexingPolicy>(jstr);
            if (newPolicy != null) {
                Console.WriteLine($"CosmosNoSqlUtil#UpdateIndexPolicy - newPolicy: {newPolicy}");
                Database? database = await this.GetDatabaseAsync(dbName);
                if (database != null) {
                    Container container = database.GetContainer(cName);
                    if (container != null) {
                        ContainerResponse cProps = await container.ReadContainerAsync();
                        cProps.Resource.IndexingPolicy = newPolicy;
                        await container.ReplaceContainerAsync(cProps.Resource);
                        await Task.Delay(3000); // wait for the indexing policy to be applied
                        return await this.GetIndexPolicy(dbName, cName);
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

    /**
    * Create a Cosmos DB NoSQL container per the given parameters.
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
}

/**
Python class CosmosNoSqlUtil method signatures:
async def close(self):
async def create_database(self, dbname, db_level_throughput=0):
async def delete_database(self, dbname):
async def delete_container(self, cname):
async def create_container(self, cname: str, c_ru: int, pkpath: str):
async def list_databases(self):
def set_db(self, dbname):
def get_current_dbname(self):
def get_current_cname(self):
def set_container(self, cname):
def get_database_link(self):
async def get_database_throughput(self):
def get_container_link(self):
async def get_container_throughput(self):
async def get_container_properties(self) -> dict:
async def list_containers(self):
async def point_read(self, id, pk):
async def create_item(self, doc):
async def upsert_item(self, doc):
async def delete_item(self, id, pk):
async def count_documents(self):
async def execute_item_batch(self, item_operations: list, pk: str):
async def query_items(self, sql, cross_partition=False, pk=None, max_items=100):
async def parameterized_query(
def last_response_headers(self) -> dict:
def last_request_charge(self):
*/