namespace App.DB;

using System.Collections.Generic;

public class CosmosDocument : Dictionary<string, object> {
    
    public CosmosDocument() : base() { }

    public CosmosDocument(IDictionary<string, object> dictionary) : base(dictionary) { }
    
    public void EnsureId() {
        if (!this.ContainsKey("id")) {
            this["id"] = Guid.NewGuid().ToString();
        }
    }
    
    public bool HasAttribute(string name) {
        return this.ContainsKey(name);
    }
}