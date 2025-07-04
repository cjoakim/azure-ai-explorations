using System.Collections;
using System.Runtime.InteropServices;
using System.Collections.Generic;
using System.Linq;

namespace App.Core;

/**
 * Class App.Core.Env contains methods for accessing environment variables and system information.
 * Chris Joakim, 2025
 */
public class Env {
    public static bool IsWindows() =>
        RuntimeInformation.IsOSPlatform(OSPlatform.Windows);

    public static bool IsMacOS() =>
        RuntimeInformation.IsOSPlatform(OSPlatform.OSX);

    public static bool IsLinux() =>
        RuntimeInformation.IsOSPlatform(OSPlatform.Linux);

    public static string OsArch() =>
        RuntimeInformation.OSArchitecture.ToString(); // X64

    public static string OsDesc() =>
        RuntimeInformation.OSDescription.ToString(); // Microsoft Windows 10.0.17134

    public static string Pwd() => Directory.GetCurrentDirectory();

    public static long Epoch() => DateTimeOffset.Now.ToUnixTimeSeconds();
    
    public static string? HomeDir() {
        if (IsWindows()) {
            return EnvVar("HOMEPATH");
        }
        else {
            return EnvVar("HOME");
        }
    }

    public static string? EnvVar(string name) {
        return Environment.GetEnvironmentVariable(name);
    }

    public static string EnvVar(string name, string defaultValue) {
        string? value = Environment.GetEnvironmentVariable(name);
        if (value == null) {
            return defaultValue;
        }
        else {
            return value;
        }
    }

    public static void DisplayEnvVars(string prefix = "AZURE_") {
        var envVars = Environment.GetEnvironmentVariables();
        var filtered = new SortedDictionary<string, string>();

        foreach (DictionaryEntry entry in envVars) {
            string key = entry.Key.ToString() ?? "";
            string value = entry.Value?.ToString() ?? "";
            if (key.StartsWith(prefix, StringComparison.Ordinal)) {
                filtered[key] = value;
            }
        }

        foreach (var kvp in filtered) {
            Console.WriteLine($"{kvp.Key}={kvp.Value}");
        }
    }
}