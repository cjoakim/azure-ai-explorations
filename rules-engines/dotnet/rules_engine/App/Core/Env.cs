
using System;
using System.IO;
using System.Runtime.InteropServices;

namespace App.Core {

    public class Env {

        public static bool IsWindows() =>
            RuntimeInformation.IsOSPlatform(OSPlatform.Windows);

        public static bool IsMacOS() =>
            RuntimeInformation.IsOSPlatform(OSPlatform.OSX);

        public static bool IsLinux() =>
            RuntimeInformation.IsOSPlatform(OSPlatform.Linux);

        public static string OsArch() =>
            RuntimeInformation.OSArchitecture.ToString();
            // X64

        public static string OsDesc() =>
            RuntimeInformation.OSDescription.ToString();
            // Microsoft Windows 10.0.17134

        public static string Pwd() => Directory.GetCurrentDirectory();
        // C:\Users\chris\github\cj-dotnet\Console1\Console1

        public static string? HomeDir() {
            
            if (Env.IsWindows()) {
                return Env.EnvVar("HOMEPATH");
            }
            else {
                return Env.EnvVar("HOME");
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
    }
}
