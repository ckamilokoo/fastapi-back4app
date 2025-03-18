from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, START, END
from langchain_ibm import WatsonxLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import settings


class State(MessagesState):
    mensaje: str
    informacion_paciente:str
    evento_traumatico:str

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


template = """
        <|begin_of_text|>

        <|start_header_id|>system<|end_header_id|>
        You are an artificial intelligence.
        your task is to simulate being a patient of a psychology doctor, who suffered
        a traumatic event, who attends the psychologist for help so you must answer the 
        doctor's questions by answering his questions and following the conversation in 
        relation to the traumatic event that occurred.
        contextual information that you should take into consideration when the doctor 
        talks to you, the description is information about the person you are simulating
        and the traumatic event is the situation that happened to the person you are simulating.
        Patient information: {informacion_paciente}
        description of the traumatic event: {evento_traumatico}
        In your response always speak in Spanish.
        your answers should not exceed a maximum of 15 words.
        
        <|eot_id|>

        <|start_header_id|>user<|end_header_id|>
        
        respuesta del doctor:{respuesta}
        The patient must answer following all the instructions given by the psychiatrist.
        Answer:


        <|eot_id|>

        <|start_header_id|>assistant<|end_header_id|>"""

prompt = PromptTemplate.from_template(template )

# Crear una cadena que combine el prompt y el modelo
llm_chain = prompt | watsonx_llm | StrOutputParser()

def chatbot(state: State):
    ai_message = llm_chain.invoke({"respuesta":state["messages"] , "informacion_paciente":state["informacion_paciente"] , "evento_traumatico":state["evento_traumatico"]})
    return {"messages": [ai_message]}

graph_builder.add_node("chatbot", chatbot)
graph_builder.set_entry_point("chatbot")
graph_builder.add_edge("chatbot", END)

from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
graph_paciente_psicologia = graph_builder.compile(checkpointer=memory)





