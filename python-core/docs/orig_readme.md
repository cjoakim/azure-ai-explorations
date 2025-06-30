# Python AI

A collection of Python AI projects and tools.

# Interesting Links 

## General

- [OpenAI](https://openai.com)
- [OpenAI SDK @ PyPi](https://pypi.org/project/openai/)
- [OpenAI SDK @ GitHub](https://github.com/openai/openai-python)
- [LangChain](https://www.langchain.com/)
- [LangServe](https://python.langchain.com/docs/langserve/)
- [LangGraph](https://www.langchain.com/langgraph)
- [Ollama](https://ollama.com/)
- [LM Studio](https://lmstudio.ai)

## Azure

- [Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Azure OpenAI SDK Use](https://learn.microsoft.com/en-us/azure/ai-services/openai/supported-languages)
- [Azure OpenAI Models](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models)
- [Azure AI Foundry](https://azure.microsoft.com/en-us/products/ai-foundry)
- [Azure AI Search](https://azure.microsoft.com/en-us/products/ai-services/ai-search)
- [Azure AI Document Intelligence](https://azure.microsoft.com/en-us/products/ai-services/ai-document-intelligence)
- [PromptFlow](https://learn.microsoft.com/en-us/azure/machine-learning/prompt-flow/overview-what-is-prompt-flow)
- [Semantic Kernel](https://learn.microsoft.com/en-us/semantic-kernel/overview/)
- [Prompt engineering techniques](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/prompt-engineering)
- [Microsoft Fabric Docs](https://learn.microsoft.com/en-us/fabric/)

## CosmosAIGraph and AIGraph4pg 

- [CosmosAIGraph Blog](https://learn.microsoft.com/en-us/azure/cosmos-db/gen-ai/cosmos-ai-graph)
- [CosmosAIGraph Repo](https://github.com/AzureCosmosDB/CosmosAIGraph)
- [CosmosAIGraph YouTube](https://www.youtube.com/watch?v=0alvRmEgIpQ)
- [AIGraph4pg Repo](https://github.com/cjoakim/AIGraph4pg)

## Personal

- [cjoakim.github.io - JoakimSoftware](https://cjoakim.github.io)

---

## LM Studio

- [See lm_studio.md in this directory](docs/lm_studio.md)
- Run LLMs/SLMs locally

---

## ollama

- [See ollama.md in this directory](docs/ollama.md)
- Run LLMs/SLMs locally
- Integrates with LangChain

---

## chromadb

- https://www.trychroma.com
- [See chromadb.md in this directory](docs/chromadb.md)


---

## LangChain libraries for Python Virtual Environment

See the requirements.txt file in this directory, which includes:

```
$ pip list

...
ollama                   0.4.8
langchain                0.3.25
langchain-community      0.3.23
langchain-core           0.3.58
langchain-ollama         0.3.2
langchain-openai         0.3.16
langchain-text-splitters 0.3.8
langsmith                0.3.42
...
```

### LangChain with ollama links

- https://python.langchain.com/docs/integrations/llms/ollama/
- https://medium.com/@abonia/ollama-and-langchain-run-llms-locally-900931914a46
- https://medium.com/towards-agi/how-to-use-ollama-effectively-with-langchain-tutorial-546f5dbffb70
- https://python.langchain.com/docs/integrations/providers/ollama/
- https://dev.to/emmakodes_/how-to-run-llama-31-locally-in-python-using-ollama-langchain-k8k

### Example program

#### References

- https://pypi.org/project/langchain-ollama/
- https://python.langchain.com/docs/integrations/llms/ollama/
- https://python.langchain.com/api_reference/ollama/llms/langchain_ollama.llms.OllamaLLM.html
- Also see "ollama1.py" in this directory.

```
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

template = """Question: {question}

Answer: Let's think step by step.
"""

model = "llama3.1"
prompt = ChatPromptTemplate.from_template(template)
model = OllamaLLM(model=model)
chain = prompt | model
chain.invoke({"question": "What is LangChain?"})
```

Chat, see https://python.langchain.com/api_reference/ollama/chat_models/langchain_ollama.chat_models.ChatOllama.html

```
from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama3-groq-tool-use")
llm.invoke("Sing a ballad of LangChain.")
```

Embeddings, see https://python.langchain.com/api_reference/community/embeddings/langchain_community.embeddings.ollama.OllamaEmbeddings.html

```
from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="llama3")
embeddings.embed_query("What is the meaning of life?")
```

---

## LangServe

See https://python.langchain.com/docs/langserve/

> [!WARNING] We recommend using LangGraph Platform rather than LangServe for new projects.

---

## LangGraph

References:
- https://www.langchain.com/langgraph 
- https://langchain-ai.github.io/langgraph/

> LangGraph — used by Replit, Uber, LinkedIn, GitLab and more — is a low-level
> orchestration framework for building controllable agents. While langchain provides 
> integrations and composable components to streamline LLM application development, 
> the LangGraph library enables agent orchestration — offering customizable architectures, 
> long-term memory, and human-in-the-loop to reliably handle complex tasks.

```
pip install -U langgraph
```

