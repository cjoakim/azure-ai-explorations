namespace App.DB;

/**
 * Simple datastructure class used in the bulk loading example.
 * Chris Joakim, 2025
 */
public class ZipCode {
    public string id {get;set;}
    public string pk {get;set;}
    public string? city {get;set;}
    public long   population {get;set;}
    public double latitude {get;set;}
    public double longitude {get;set;}
    public Dictionary<string,object>? nested {get;set;} // can be used to store the original JSON document
    
    public ZipCode() {
        this.id = Guid.NewGuid().ToString();
        this.pk = "";
    }
    
    
}