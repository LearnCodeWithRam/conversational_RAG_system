from langchain_ollama import OllamaLLM
from langchain_core.messages import SystemMessage, HumanMessage

ollama_llm = OllamaLLM(
    model="llama3.1:8b",
    base_url="http://115.241.186.203",
    temperature=0.7
)

def ollama_response(system_prompt: str, user_prompt: str):
    response = ollama_llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    return response.content if hasattr(response, "content") else str(response)






       
   