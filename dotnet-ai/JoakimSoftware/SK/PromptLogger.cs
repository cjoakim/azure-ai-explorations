namespace Joakimsoftware.SK;

using Microsoft.SemanticKernel;

public class PromptLogger : IPromptRenderFilter {
    public async Task OnPromptRenderAsync(PromptRenderContext context, Func<PromptRenderContext, Task> next) {
        await next(context);
        Console.WriteLine($">>>\nPromptLogger:\n{context.RenderedPrompt}\n<<<\n");
    }
}