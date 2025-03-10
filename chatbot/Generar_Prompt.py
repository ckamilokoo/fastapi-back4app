from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

from langgraph.graph import END, StateGraph
from langchain_ibm import WatsonxLLM
# For State Graph 
from typing_extensions import TypedDict
import os
from config import settings
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState


from langgraph.graph import StateGraph, START, END
from typing import Literal


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


generate_prompt = PromptTemplate(
    template="""
    
    <|begin_of_text|>
    
    <|start_header_id|>system<|end_header_id|> 
    
    you are an expert and very nice female artificial intelligence assistant called jimena, your task is to collect information from the prompt that the user 
    wants to create so you have to talk to the users in a respectful and friendly way always with the goal that the users tell you that they want to create the prompt. 
    you have to talk to the users in a respectful and friendly way always with the objective that the users tell you that they want to create 
    the prompt for which you need to know the purpose of the prompt, variables it uses, unwanted outputs and output format, 
    so try to orient all your answers to the objective of obtaining the information needed to create a prompt.  
    your answers must be precise, coherent and always in Spanish and you cannot exceed 40 words in your answer.
    if the user mentions that he/she wants to create a prompt you should ask the following questions :
      -what is the purpose of their prompt .
      -Does their prompt have variables that should be used within the prompt?
      -are there any unwanted responses within the prompt?
      -Does the output of the prompt have to be in some format?

    If the user already answered you the 4 questions to create the prompt you must confirm the information you have by telling them to the user,
    if the user rejects it or has some change ask for it and change the information and confirm again if the information is correct you must do this step as many times as necessary as the user wants to change something in prompt but if he accepts you must answer with a text that says Prompt to generate and the json that only must have
    only the information the user gave you in the following format:
    [
    "objetivo": ‘target that the user told you’,
    “prompt variables": ‘the variables that the user mentioned verbatim’,
    “respuesta no deseada": ‘what the user said about it’,
    “formato salida": ‘format the user wants or plain text’, 
    ]

    
    
    <|eot_id|>
    
    <|start_header_id|>user<|end_header_id|>
    
    question:{question}
    Answer: 
    
    <|eot_id|>
    
    <|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["question"],
)

# Chain
generate_chain = generate_prompt | watsonx_llm | StrOutputParser()

# Router

router_prompt = PromptTemplate(
    template="""
    
    <|begin_of_text|>
    
    <|start_header_id|>system<|end_header_id|>
    
    You are an expert at directing a user question to generación de prompt or finalizar ciclo. 
    Use finalizar ciclo for any natural text that responds to the llm such as :
        -hello.
        -you want to create a prompt.
    Otherwise if you receive a text containing [] and within it come out target, prompt variables, output format you should classify the text as generación de prompt, 
    example text for generación de prompt:
      [
      “target": ‘target that the user told you’,
      “prompt variables": ‘the variables that the user mentioned verbatim’,
      “unwanted response": ‘what the user said about it’,
      “output format": ‘format the user wanted or plain text’, 
      ] 
    
    Give a binary option 'generación de prompt' or 'finalizar ciclo' depending on the question. 
    Return the JSON with a single key 'choice' without premable or explanation.
    

    examples that you should only use as a guide for your answers and nothing else.
    example 1:
      question to route:hello
      answer :finalizar ciclo

    example 2:
      question to route:i want to create a prompt 
      answer :finalizar ciclo

    example 3:
      question to route:i want to create a rag prompt
      answer :finalizar ciclo

    example 4:
      question to route:output format plain text
      answer :finalizar ciclo

    example 5:
      question to route: 
      Prompt para generar:
      [
        “objective": ‘create a prompt to answer questions based on a text’,
        “prompt variables": ‘question and help text to answer the question’,
        “unwanted answer“: '”none',
        “output format": ‘plain text output’, 
        ]

      answer :generación de prompt

    example 6:
      question to route: 
      Prompt para generar:
      [
        “objective": ‘create a prompt to parse text and sort it’,
        “prompt variables": ‘text to sort’,
        “unwanted response“: '”none',
        “output format": ‘plain text output’, 
        ]
      answer :generación de prompt

    example 6:
      question to route:
      Confirmar la informacion del prompt [
        “objective": ‘create a prompt to parse text and sort it’,
        “prompt variables": ‘text to sort’,
        “unwanted response“: '”none',
        “output format": ‘plain text output’, 
        ]
      answer :finalizar ciclo
    
    Question to route: {question} 
    answer:
    
    <|eot_id|>
    
    <|start_header_id|>assistant<|end_header_id|>
    
    """,
    input_variables=["question"],
)

# Chain
question_router = router_prompt | watsonx_llm | JsonOutputParser()




class State(MessagesState):
    mensaje: str

graph_builder = StateGraph(State)

def chatbot(state: State):
    ai_message = generate_chain.invoke({"question":state["messages"]})
    return {"messages": [ai_message]}


def generador_prompt(state: State):
    
    ai_message = state["messages"][-1].content
    return {"messages": [ai_message]}

def route_question(state: State) -> Literal["generar_prompt", "__end__"]:
    """
    route question to web search or generation.

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """

    print("Step: Routing Query")
    question = state["messages"][-1].content
    print(question)
    print(type(question))
    output = question_router.invoke({"question": question})
    print(output)
    if output['choice'] == "generación de prompt":
        print("Step: Routing Query to Web Search")
        return "generar_prompt"
    elif output['choice'] == 'finalizar ciclo':
        print("Step: Routing Query to Generation")
        return '__end__'



graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("generar_prompt", generador_prompt)




graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", route_question)

graph_builder.add_edge("generar_prompt", END)



memory = MemorySaver()
# View
graph_2=graph_builder.compile(checkpointer=memory)