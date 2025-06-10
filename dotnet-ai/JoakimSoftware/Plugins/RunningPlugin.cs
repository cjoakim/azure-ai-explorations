namespace Joakimsoftware.Plugins;

using System;
using System.ComponentModel;
using System.Threading.Tasks;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Plugins;
using M26;

/**
 * This is a custom native SK Plugin that performs running calculations
 * using the NuGet Joakimsoftware.M26 package.
 */
public class RunningPlugin {
    [KernelFunction("MarathonDistance")]
    [Description("Return the distance of a marathon as a double")]
    public async Task<double> MarathonDistance() {
        try {
            Console.WriteLine($"RunningPlugin.MarathonDistance");
            await Task.Delay(0); // Simulate async work
            return 26.2;
        }
        catch (Exception e) {
            Console.WriteLine(e.ToString());
            return -1.0;
        }
    }

    [KernelFunction("CalculatePacePerMile")]
    [Description("Calculate a running pace per mile given a distance and time")]
    public async Task<string> CalculatePacePerMile(
        [Description("Distance as a float")] string distance,
        [Description("Elapsed time in HH:MM:SS format")]
        string hhmmss) {
        try {
            Console.WriteLine($"RunningPlugin.CalculatePacePerMile - distance: {distance}, hhmmss: {hhmmss} ");
            await Task.Delay(0); // Simulate async work
            Distance d = new Distance(Convert.ToDouble(distance));
            ElapsedTime et = new ElapsedTime(hhmmss);
            Speed sp = new Speed(d, et);
            return sp.pacePerMile();
        }
        catch (Exception e) {
            Console.WriteLine(e.ToString());
            return "error";
        }
    }
}