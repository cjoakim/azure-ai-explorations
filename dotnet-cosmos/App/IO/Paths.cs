using App.Core;

namespace App.IO;

/**
 * Class App.IO.Paths contains methods for local file path operations.
 * Chris Joakim, 2025
 */
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
        string sep = PathSeperator();
        return $"{home}{sep}github";
    }
}

