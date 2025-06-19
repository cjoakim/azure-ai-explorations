namespace App.DB;

using System.Collections.Generic;
using System.Text.Json;

/**
 * Generic class that can be used to represent Cosmos DB documents.
 * Inherits from Dictionary<string, object> to allow dynamic properties,
 * and adds methods for id and partition key management.
 * Easily serializable to JSON.
 * Chris Joakim, 2025
 */
public class CosmosDocument : Dictionary<string, object> {
    public CosmosDocument() : base() {
        //EnsureId();
    }

    public CosmosDocument(IDictionary<string, object> dictionary) : base(dictionary) {
        //EnsureId();
    }
    
    public void MergeDictionary(IDictionary<string, object> dict) {
        foreach (var kvp in dict) {
            if (this.ContainsKey(kvp.Key)) {
                this[kvp.Key] = kvp.Value; // Update existing key
            } else {
                this.Add(kvp.Key, kvp.Value); // Add new key
            }
        }
    }

    /**
     * Ensure that the document has an 'id' property.
     * If not present, generate a new GUID and set it as the 'id'.
     */
    public void EnsureId() {
        if (!this.ContainsKey("id")) {
            this["id"] = Guid.NewGuid().ToString();
        }
    }
    
    public string GetId() {
        return "" + this["id"];
    }
    
    public void SetId() {
        this["id"] = Guid.NewGuid().ToString();
    }

    public bool HasAttribute(string name) {
        return this.ContainsKey(name);
    }
    
    public void SetAttribute(string name, object value) {
        this[name] = value;
    }
    
    public string GetStringAttribute(string name, string defaultValue = "") {
        if (this.ContainsKey(name)) {
            return "" + this[name];
        }
        return defaultValue;
    }
    
    public string AsJson(bool pretty = true) {
        if (pretty) {
            var options = new JsonSerializerOptions { WriteIndented = true };
            return System.Text.Json.JsonSerializer.Serialize(this, options);
        }
        else {
            return System.Text.Json.JsonSerializer.Serialize(this);
        }
    }
}