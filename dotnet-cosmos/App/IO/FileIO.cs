namespace App.IO;

using System.Text.Json;

/**
 * Class App.IO.FileIO contains methods for local File I/O operations.
 * Chris Joakim, 2025
 */
public class FileIO {
    public FileIO() {
    }

    public string[] ListFilesInDirctory(string dirPath, string suffixPattern = "*.json", bool recursive = false) {
        try {
            if (Directory.Exists(dirPath)) {
                if (recursive) {
                    return Directory.GetFiles(dirPath, suffixPattern, SearchOption.AllDirectories);
                }
                else {      
                    return Directory.GetFiles(dirPath, suffixPattern, SearchOption.TopDirectoryOnly);
                }  
            }
        }
        catch (Exception e) {
            Console.WriteLine("FileIO#ListFilesInDirctory - Exception: " + e.Message);
        }
        return new string[0];
    }
    
    public string? ReadText(string filename) {
        try {
            return File.ReadAllText(filename);
        }
        catch (Exception e) {
            Console.WriteLine("FileIO#ReadText - Exception: " + e.Message);
            return null;
        }
    }
    
    public Dictionary<string, object>? ReadParseJsonDictionary(string filename) {
        try {
            string jsonString = File.ReadAllText(filename).Trim();
            return JsonSerializer.Deserialize<Dictionary<string, object>>(jsonString);
        }
        catch (Exception e) {
            Console.WriteLine("FileIO#ReadParseJsonDictionary - Exception: " + e.Message);
            return null;
        }
    }
    
    public List<Dictionary<string, object>>? ReadParseJsonDictionaryList(string filename) {
        try {
            string jsonString = File.ReadAllText(filename).Trim();
            return JsonSerializer.Deserialize<List<Dictionary<string, object>>>(jsonString);
        }
        catch (Exception e) {
            Console.WriteLine("FileIO#ReadParseJsonDictionaryList - Exception: " + e.Message);
            return null;
        }
    }

    public List<string>? ReadLines(string filename) {
        List<string> lines = new List<string>();
        try {
            string? line = null;
            StreamReader file = new StreamReader(filename);
            while ((line = file.ReadLine()) != null) {
                lines.Add(line);
            }
        }
        catch (Exception e) {
            Console.WriteLine("FileIO#ReadLines - Exception: " + e.Message);
            return null;
        }
        return lines;
    }
}

