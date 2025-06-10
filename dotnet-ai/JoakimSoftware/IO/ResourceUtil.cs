using System.IO.Enumeration;

namespace Joakimsoftware.IO;

using System;
using System.Reflection;

/**
 * Class to read embedded resources.
 * See the csproj file for the embedded resources.
 * See https://khalidabuhakmeh.com/how-to-use-embedded-resources-in-dotnet
 */
public class ResourceUtil {
    public ResourceUtil() {
    }

    public string[] GetResourceNames() {
        return System.Reflection.Assembly.GetExecutingAssembly().GetManifestResourceNames();
    }

    public void DisplayResourceNames() {
        foreach (var name in this.GetResourceNames()) {
            Console.WriteLine($"Resource: {name}"); // dotnetx.Resources.joke.yaml
        }
    }

    public string ReadResource(string resourceBasename) {
        var assemblyName = Assembly.GetExecutingAssembly().GetName(); // dotnetx
        var resourceName = $"{assemblyName.Name}.Resources.{resourceBasename}"; // dotnetx.Resources.joke.yaml

        using (var stream = System.Reflection.Assembly.GetExecutingAssembly().GetManifestResourceStream(resourceName)) {
            if (stream == null) {
                throw new ArgumentException($"Resource '{resourceName}' not found.");
            }

            using (var reader = new System.IO.StreamReader(stream)) {
                return reader.ReadToEnd();
            }
        }
    }
}