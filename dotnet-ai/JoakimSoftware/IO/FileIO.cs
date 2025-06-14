using System;
using System.Collections.Generic;

namespace Joakimsoftware.IO {
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
    }
}
