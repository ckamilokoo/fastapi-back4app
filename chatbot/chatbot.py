from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, START, END
from langchain_ibm import WatsonxLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import settings


class State(MessagesState):
    mensaje: str

graph_builder = StateGraph(State)

# Configurar los parámetros del modelo
parameters = {
    "decoding_method": "greedy",
  "max_new_tokens": 4096,
  "min_new_tokens": 0,
  "repetition_penalty": 1,
    "stop_sequences": [
   ";"
  ],
}

#meta-llama/llama-3-3-70b-instruct

# Inicializar el modelo WatsonxLLM
watsonx_llm = WatsonxLLM(
    model_id=settings.watsonx_model_id,
    url=settings.watsonx_url,
    project_id=settings.watsonx_project_id,
    apikey=settings.watsonx_api_key,
    params=parameters
)


template = """<|begin_of_text|>

        <|start_header_id|>system<|end_header_id|>
        you are a very friendly female AI assistant named jimena, your task is to talk to users naturally and accurately in Spanish, and your answers cannot exceed a maximum of 50 words.

            
        <|eot_id|>

        <|start_header_id|>user<|end_header_id|>
        mensaje usuario:{mensaje}
        answer:
        

        <|eot_id|>

        <|start_header_id|>assistant<|end_header_id|>"""

prompt = PromptTemplate.from_template(template)

# Crear una cadena que combine el prompt y el modelo
llm_chain = prompt | watsonx_llm | StrOutputParser()

def chatbot(state: State):
    ai_message = llm_chain.invoke({"mensaje":state["messages"]})
    return {"messages": [ai_message]}

graph_builder.add_node("chatbot", chatbot)
graph_builder.set_entry_point("chatbot")
graph_builder.add_edge("chatbot", END)

from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)
