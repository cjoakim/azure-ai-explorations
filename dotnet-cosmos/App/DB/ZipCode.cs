namespace App.DB;

public class ZipCode {
    public string? id {get;set;}
    public string? pk {get;set;}
    public string? city {get;set;}
    public long   population {get;set;}
    public double latitude {get;set;}
    public double longitude {get;set;}
    
    public ZipCode() {
        this.id = Guid.NewGuid().ToString();
    }
    
    
}