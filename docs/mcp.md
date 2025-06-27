# MCP - Model Context Protocol 

## Anthropic

- https://docs.anthropic.com/en/docs/mcp
- https://modelcontextprotocol.io/introduction
- https://github.com/modelcontextprotocol
- https://github.com/modelcontextprotocol/modelcontextprotocol
- https://modelcontextprotocol.io/specification/2025-06-18

#### MCP Repos

- https://github.com/modelcontextprotocol/modelcontextprotocol
- https://github.com/modelcontextprotocol/quickstart-resources

---

## Microsoft 

- https://learn.microsoft.com/en-us/azure/developer/ai/intro-agents-mcp

### MCP Server 

- https://learn.microsoft.com/en-us/azure/developer/azure-mcp-server/
- https://learn.microsoft.com/en-us/azure/developer/azure-mcp-server/
- https://learn.microsoft.com/en-us/azure/developer/azure-mcp-server/tools/
- https://learn.microsoft.com/en-us/azure/developer/azure-mcp-server/tools/ai-search
- https://learn.microsoft.com/en-us/azure/developer/azure-mcp-server/tools/cosmos-db
- https://github.com/AzureCosmosDB/azure-cosmos-mcp-server-samples
- https://github.com/Azure/azure-mcp

### VSC Extension

- https://code.visualstudio.com/docs/copilot/chat/mcp-servers

### VSC Insiders Build

- https://code.visualstudio.com/docs/?dv=darwinarm64&build=insiders 

### Cosmos DB Example

- See https://github.com/AzureCosmosDB/azure-cosmos-mcp-server-samples
- See the mcp/microsoft/azure-cosmos-mcp-server-samples directory in this repo where the following was copied:

```
git clone https://github.com/AzureCosmosDB/azure-cosmos-mcp-server-samples.git
```

- https://github.com/AzureCosmosDB/azure-cosmos-mcp-server-samples/tree/main/javascript
  - VSC Insiders version: https://code.visualstudio.com/insiders/

---

## Anthropic Claude Desktop

See https://github.com/AzureCosmosDB/azure-cosmos-mcp-server-samples/tree/main/javascript

/Users/cjoakim/Library/Application Support/Claude/claude_desktop_config.json

```
{
  "mcpServers": {
    "cosmosdb": {
      "command": "node",
      "args": [ "/Users/cjoakim/github/azure-ai-explorations/mcp/microsoft/azure-cosmos-mcp-server-samples/javascript/dist/index.js" ]for the Azure Cosmos DB MCP server file,
      "env": {
        "COSMOSDB_URI": "Your Cosmos DB Account URI",
        "COSMOSDB_KEY": "Your Cosmos DB KEY",
        "COSMOS_DATABASE_ID": "dev",
        "COSMOS_CONTAINER_ID": "airports"
      }
    }
  }
}
```

---

## Hugging Face Course

- https://huggingface.co/learn/mcp-course/en/unit0/introduction
