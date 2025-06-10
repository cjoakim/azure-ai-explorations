from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

template = """Question: {question}

Answer: Let's think step by step.
"""

print("template: {}".format(template))

model = "phi3"  # "llama3.1"
print("model: {}".format(model))

prompt = ChatPromptTemplate.from_template(template)
print("prompt: {}".format(prompt))

model = OllamaLLM(model=model)
print("model: {}".format(model))

chain = prompt | model
print("chain: {}".format(chain))

result = chain.invoke({"question": "What is LangChain?"})
print("result:")
print(result)
