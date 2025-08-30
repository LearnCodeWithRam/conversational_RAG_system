
from langchain_core.messages import SystemMessage, HumanMessage
from config import ollama_llm

def ollama_response(system_prompt: str, user_prompt: str):
    response = ollama_llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    return response.content if hasattr(response, "content") else str(response)

       
   