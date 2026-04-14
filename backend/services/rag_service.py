import os
from dotenv import load_dotenv
os.environ["USER_AGENT"] = "NORA_Agent"
#import sys
#import types

#sys.modules['pwd'] = types.ModuleType('pwd')

#from langchain_community.document_loaders.pdf import PyPDFLoader
#from langchain_community.document_loaders.web_base import WebBaseLoader
#from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# RetrievalQA -> deprecated
# create_retrieval_chain recommended
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
OPENAI_API_KEY = os.getenv("NORA_RAG")
COLLECTION_NAME = "nora-vector-db"

EMBEDDING = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=OPENAI_API_KEY)

qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

db = QdrantVectorStore(
    client=qdrant_client,
    collection_name=COLLECTION_NAME,
    embedding=EMBEDDING
)

# def ingest_knowledge(source_path):
#     print(f"Fetching data from {source_path}")
#     loader = WebBaseLoader(source_path)
#     docs = loader.load()

#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100, separators=["\n\n", "\n", ".", ","])
#     chunks = text_splitter.split_documents(docs)

#     QdrantVectorStore.from_documents(
#         chunks,
#         EMBEDDING,
#         url=QDRANT_URL,
#         api_key=QDRANT_API_KEY,
#         collection_name=COLLECTION_NAME,
#         force_recreate=True
#     )

#     print(f"Cloud Ingestion completed. ({len(chunks)} chunks saved to Qdrant)")

# target_date, final_risk, smd_value, forecast_rain_sum, past_rain_sum, soil_type
def generate_nora_reasoning(target_date, final_risk, smd_value, forecast_rain_sum, past_rain_sum, soil_type):

    retriever = db.as_retriever(search_kwargs={"k": 3})
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, openai_api_key=OPENAI_API_KEY)
    
    system_prompt = (
    "You are an AI assistant for the NORA (Nitrate and Optimised Rainfall Analysis) system, helping Irish farmers.\n"
    "Explain WHY the system gave the '{final_score}' rating based on your knowledge base.\n"
    "Keep the explanation professional, easy for farmers to understand.\n"
    "Context: {context}" # knowledge base
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Target Date: {target_date}, Risk: {final_score}, SMD: {smd_value}, Expected Rain (next 48h): {forecast_rain_sum} mm, Past 2 days Rain: {past_rain_sum} mm, Soil Drainage: {soil_type}")
    ])

    document_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, document_chain)

    # a targeted query for the vector database search
    search_query = f"fertiliser spreading guidelines for SMD {smd_value} and forecast rain {forecast_rain_sum}mm in {soil_type} soil"

    # execute the chain to get the final AI reasoning
    response = rag_chain.invoke({
        "input": search_query,
        "final_score": final_risk,
        "target_date": target_date,
        "smd_value": smd_value,
        "forecast_rain_sum": forecast_rain_sum,
        "past_rain_sum": past_rain_sum,
        "soil_type": soil_type
    })

    return response["answer"]

# if __name__ == "__main__":

#     target_url = [
#         "https://teagasc.ie/environment/water-quality/water-quality-week/utilising-nitrogen-inputs-efficiently/#nleaching",
#         "https://www.gov.ie/en/department-of-agriculture-food-and-the-marine/press-releases/technical-note-amendment-to-the-good-agricultural-practices-for-the-protection-of-water-regulations/",
#         "https://teagasc.ie/news--events/daily/fertiliser-advice-under-prolonged-dry-soil-conditions/",
#         "https://teagasc.ie/environment/water-quality/farming-for-water-quality-assap/assap-factsheets/early-nitrogen-for-spring-grassland/",
#         "https://teagasc.ie/environment/water-quality/farming-for-water-quality-assap/improving-my-water-quality/nutrient-and-fertiliser-management/",
#         "https://teagasc.ie/news--events/daily/focus-on-ground-conditions-and-weather-before-spreading-slurry/",
#         "https://teagasc.ie/publications/how-to-reduce-nitrogen-losses-at-farm-level-php",
#         "https://farmingforwater.ie/top-tips-to-protect-water-quality-in-march-and-april/"
#     ]

#     for url in target_url:
#         try:
#             ingest_knowledge(url)
#         except Exception as e:
#             print(f"Error {url}: {e}")

# print("All saved successfully.")
