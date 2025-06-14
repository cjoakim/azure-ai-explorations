using System;
using System.Collections.Generic;
using System.Text.Json;

namespace App.IO {
    public class FileIO {
        public FileIO() {
        }

        public string ReadText(string filename) {
            return System.IO.File.ReadAllText(filename);
        }

        public List<string> ReadLines(string filename) {
            List<string> lines = new List<string>();
            string? line = null;
            System.IO.StreamReader file = new System.IO.StreamReader(filename);
            while ((line = file.ReadLine()) != null) {
                lines.Add(line);
            }
            return lines;
        }

        public List<Dictionary<string, object>>? ReadJsonDictionaryList(string infile) {
            List<Dictionary<string, object>>? data = null;
            try {
                string? jsonString = File.ReadAllText(infile);
                if (jsonString != null) {
                    data = JsonSerializer.Deserialize<List<Dictionary<string, object>>>(jsonString);
                }
            }
            catch (Exception e) {
                Console.WriteLine(e);
            }
            return data;
        }

        public Dictionary<string, object>? ReadJsonDictionary(string infile) {
            Dictionary<string, object>? data = null;
            try {
                string? jsonString = File.ReadAllText(infile);
                if (jsonString != null) {
                    data = JsonSerializer.Deserialize<Dictionary<string, object>>(jsonString);
                }
            }
            catch (Exception e) {
                Console.WriteLine(e);
            }
            return data;
        }
        
        public void LogObjectAsJson(object? obj) {
            if (obj != null) {
                var options = new JsonSerializerOptions { WriteIndented = true };
                string jsonString = JsonSerializer.Serialize(obj, options);
                Console.WriteLine(jsonString);
            }
        }
    }
}