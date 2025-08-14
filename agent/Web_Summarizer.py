from langgraph.graph import StateGraph, END # type: ignore
from langchain.prompts import PromptTemplate
from langchain_mistralai.chat_models import ChatMistralAI # type: ignore
from langchain_google_genai import ChatGoogleGenerativeAI # type: ignore
from langchain.schema import HumanMessage
import os
from typing import TypedDict, List, Dict
from dotenv import load_dotenv
# from duckduckgo_search import DDGS # type: ignore

load_dotenv()

class State(TypedDict):
    query:str
    classification:str
    entities:List[str]
    summary:str
    url:str
    urls:List[str]
    information:str
    keywords:List[str]
    metadata:Dict

llm = ChatMistralAI(model="mistral-small", temperature=0)

def obtain_keyword_node(state:State):
    '''Obtain keywords from the given user query'''

    prompt = PromptTemplate(
        input_variables=["query"],
        template="From the given user query, return a list of comma separated keywords. \n\nUser query:{query}.\n\nKeywords:"
    )

    message = HumanMessage(content=prompt.format(query=state["query"]))

    keywords = llm.invoke([message]).content.strip().split(",")

    return {"keywords":keywords}

def web_scraper_node(state:State):
    '''Scrape the web to find a list of relevant urls'''
    
    prompt = PromptTemplate(
        input_variables=["keywords"],
        template="Search the web and return a list of comma separated relevant urls given a list of keywords. \n\nList of keywords to search:{keywords}\n\nUrls:"
    )

    message = HumanMessage(content=prompt.format(keywords=state["keywords"]))

    urls=llm.invoke([message]).content.strip().split(",")

    return {"urls":urls}

def web_crawler_node(state:State):
    '''Use the list of urls and obtain information from each of them'''

    prompt = PromptTemplate(
        input_variables=["urls"],
        template="From the given list of urls, search all of them, and assemble them into one unified detailed and exhaustive summary agnosic of the source.\n\nList of Urls:{urls}"
    )

    message = HumanMessage(content=prompt.format(urls=state["urls"]))

    information = llm.invoke([message]).content.strip()

    return {"information":information}

def attach_metadata_node(state:State):
    '''Attach metadata to the response based on user query and provided summary'''

    prompt = PromptTemplate(
        input_variables=["query","information"],
        template="Attach metadata(Tone, Location, Topic) to the provided summary {information} according to the user query {query}, return a dictionary of metadata"
    )

    message = HumanMessage(content=prompt.format(information=state["information"], query=state["query"]))

    metadata = llm.invoke([message]).content.split()

    return {"metadata":metadata}

def classification_node(state:State):
    ''' Classify the given text into one of the categories: News, Blog, Research or Other '''

    prompt = PromptTemplate(
        input_variables=["information"],
        template="Classify the following text into one of the categories: News, Blog, Research, Article, Review or Other.\n\nInformation:{information}\n\nCategory:"
    )

    message = HumanMessage(content=prompt.format(information=state["information"]))

    classification = llm.invoke( [message] ).content.strip()

    return {"classification":classification}

def entity_extraction_node(state:State):
    ''' Extract all the entities (Person, Organization, Location) from the text'''

    prompt = PromptTemplate(
        input_variables=["text"],
        template="Extract all the entities (Person, Organization, Location, Name, Place) from the following text. Provide the result as a comma-separated list.\n\nText:{text}\n\nEntities:"
    )

    message = HumanMessage(content=prompt.format(text=state["text"]))

    entities = llm.invoke([message]).content.strip().split(",")

    return {"entities":entities}

def summarization_node(state:State):
    ''' Summarize the text in one short sentence '''

    prompt = PromptTemplate(
        input_variables=["information"],
        template="Summarize the following text in one short sentence.\n\nInformation:{information}\n\nSummary:"
    )

    message = HumanMessage(content=prompt.format(information=state["information"]))

    summary = llm.invoke([message]).content.strip()

    return {"summary":summary}

workflow = StateGraph(State)

workflow.add_node("obtain_keyword_node", obtain_keyword_node)
workflow.add_node("web_scraper_node", web_scraper_node)
workflow.add_node("web_crawler_node", web_crawler_node)
workflow.add_node("attach_metadata_node", attach_metadata_node)

workflow.set_entry_point("obtain_keyword_node")
workflow.add_edge("obtain_keyword_node","web_scraper_node")
workflow.add_edge("web_scraper_node","web_crawler_node")
workflow.add_edge("web_crawler_node","attach_metadata_node")
workflow.add_edge("attach_metadata_node",END)

app=workflow.compile()

query = input("Enter query! ")

input_state={"query":query}
result = app.invoke(input_state)

print(f"Keyword List: {result["keywords"]}")
print(f"\n List of urls: {result["urls"]}")
print(f"\n Metadata: {result["metadata"]}")
print(f"\n SUMMARY: {result["information"]}")