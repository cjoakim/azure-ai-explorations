using System;
using System.Collections.Generic;
using System.IO;
using App.Core;

namespace App.IO {
    public class Paths {
        public static string Pwd() => Env.Pwd();

        public static string PathSeperator() => Path.DirectorySeparatorChar.ToString();

        public static string Normalize(string p) => Path.GetFullPath(p);

        public static string Normalize(string pathStart, List<string> subpaths) {
            String path = Normalize(pathStart);
            String sep = PathSeperator();

            if (subpaths != null) {
                foreach (string subpath in subpaths) {
                    if (!path.EndsWith(sep)) {
                        path = path + sep;
                    }

                    path = path + subpath;
                }
            }

            return path;
        }

        public static string GithubDir() {
            string home = "" + Env.HomeDir();
            string sep = Paths.PathSeperator();
            return $"{home}{sep}github";
        }
    }
}