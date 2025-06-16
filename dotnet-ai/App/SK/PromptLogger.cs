namespace App.SK;

using Microsoft.SemanticKernel;

/**
 * This is a custom native SK Plugin that performs running calculations
 * using the NuGet Joakimsoftware.M26 package.
 * Chris Joakim, 2025
 */

public class PromptLogger : IPromptRenderFilter {
    public async Task OnPromptRenderAsync(PromptRenderContext context, Func<PromptRenderContext, Task> next) {
        await next(context);
        Console.WriteLine($">>>\nPromptLogger:\n{context.RenderedPrompt}\n<<<\n");
    }
}