namespace App.DB;

using System.Text.Json;
using System.Text.Json.Nodes;

/**
 * Simple datastructure class used in the bulk loading and vector search example.
 * See the CosmosAIGraph project at https://github.com/AzureCosmosDB/CosmosAIGraph
 * Chris Joakim, 2025
 */
public class PythonLib {
    public string id {get;set;}
    public string pk {get;set;}
    public string? packageUrl {get;set;}
    public string? keywords {get;set;}
    public string? description {get;set;}
    public string[]? developers {get;set;}
    public double[]? embedding {get;set;}
    public PythonLib() {
        this.id = ""; // Guid.NewGuid().ToString();
        this.pk = "";
    }

    public void SetDescription(object? desc) {
        if (desc != null) {
            try {
                JsonElement jsonElement = JsonSerializer.SerializeToElement(desc);
                if (jsonElement.ValueKind == JsonValueKind.String) {
                    this.description = ("" + jsonElement.GetString()).Split('\n')[0];
                    if (this.description.Length > 100) {
                        this.description = this.description.Substring(0, 100) + "...";
                    }
                }
            }
            catch (Exception e) {
                Console.WriteLine("PythonLib#SetDescription - Exception: " + e.Message);
            }
        }
    }
    

    public void SetDevelopers(object? devs) {
        if (devs != null) {
            try {
                JsonElement jsonElement = JsonSerializer.SerializeToElement(devs);
                if (jsonElement.ValueKind == JsonValueKind.Array) {
                    // Convert the JsonElement to an array of strings
                    this.developers = jsonElement.EnumerateArray().Select(e => e.ToString()).ToArray();
                }
            }
            catch (Exception e) {
                Console.WriteLine("PythonLib#SetDevelopers - Exception: " + e.Message);
            }
        }
    }
    public void SetEmbeddings(object? vector) {
        if (vector != null) {
            try {
                JsonElement jsonElement = JsonSerializer.SerializeToElement(vector);
                if (jsonElement.ValueKind == JsonValueKind.Array) {
                    // Convert the JsonElement to an array of doubles
                    this.embedding = jsonElement.EnumerateArray().Select(e => e.GetDouble()).ToArray();
                }
                else {
                    Console.WriteLine("PythonLib#SetEmbeddings - jsonElement isn't an array");
                }
            }
            catch (Exception e) {
                Console.WriteLine("PythonLib#SetEmbeddings - Exception: " + e.Message);
            }
        }
        else {
            Console.WriteLine("PythonLib#SetEmbeddings - method arg is null");
        }
    }
}