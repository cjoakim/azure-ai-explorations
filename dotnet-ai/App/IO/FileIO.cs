namespace App.IO;

/**
 * Class App.IO.FileIO contains methods for local File I/O operations.
 * Chris Joakim, 2025
 */
public class FileIO {
    public FileIO() {
    }

    public string ReadText(string filename) {
        return File.ReadAllText(filename);
    }

    public List<string> ReadLines(string filename) {
        List<string> lines = new List<string>();
        string? line = null;
        StreamReader file = new StreamReader(filename);
        while ((line = file.ReadLine()) != null) {
            lines.Add(line);
        }

        return lines;
    }
}

