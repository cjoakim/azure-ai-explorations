namespace App.IO;

public class ConsoleIO {
    
    public static string PromptUser(string message) {
        Console.WriteLine(message);
        return "" + Console.ReadLine();
    }
}