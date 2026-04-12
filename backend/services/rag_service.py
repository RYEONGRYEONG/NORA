import os
import sys
import types

sys.modules['pwd'] = types.ModuleType('pwd')

from dotenv import load_dotenv 
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_community.document_loaders.web_base import WebBaseLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma

# RetrievalQA -> deprecated
# create_retrieval_chain recommended
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain


load_dotenv()
os.environ["USER_AGENT"] = "NORA_Agent"

api_key = os.getenv("NORA_RAG")
if api_key:
    os.environ["OPENAI_API_KEY"] = api_key
else:
    print("NORA_RAG key not found in .env file.")

EMBEDDING = OpenAIEmbeddings(model="text-embedding-3-small")
PERSIST_DIR = "backend/db/chroma_db"

def ingest_knowledge(source_path, is_url=True):
    print(f"Fetching data from {source_path}")
    loader = WebBaseLoader(source_path) if is_url else PyPDFLoader(source_path)
    docs = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=600, chunk_overlap=100)
    chunks = text_splitter.split_documents(docs)

    db = Chroma.from_documents(documents=chunks, embedding=EMBEDDING, persist_directory=PERSIST_DIR)
    print(f"Ingestion complete. ({len(chunks)} chunks saved)")

def generate_nora_reasoning(target_date, smd_value, rain_forecast, final_score):
    if not os.path.exists(PERSIST_DIR):
        return "No trained data found."

    db = Chroma(persist_directory=PERSIST_DIR, embedding_function=EMBEDDING)
    retriever = db.as_retriever(search_kwargs={"k": 3})
    
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    
    system_prompt = (
    "You are an AI assistant for the NORA (Nitrate and Optimised Rainfall Analysis) system, helping Irish farmers.\n"
    "Explain to the farmer WHY the system gave the '{final_score}' rating. \n"
    "Search your knowledge base (Teagasc official agricultural guidelines) using the retrieved context below.\n"
    "Keep the explanation under 3 sentences, professional, easy to understand.\n\n"
    "Context: {context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Target Date: {target_date}, SMD: {smd_value}, Expected Rain: {rain_forecast} mm, Recommendation: {final_score}")
    ])

    document_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, document_chain)

    search_query = f"spreading fertiliser guidelines for SMD {smd_value} and rainfall {rain_forecast}mm"

    response = rag_chain.invoke({
        "input": search_query,
        "target_date": target_date,
        "smd_value": smd_value,
        "rain_forecast": rain_forecast,
        "final_score": final_score
    })

    return response["answer"]

if __name__ == "__main__":

    target_url = "https://teagasc.ie/environment/water-quality/water-quality-week/utilising-nitrogen-inputs-efficiently/#nleaching"
    ingest_knowledge(target_url, is_url=True)

    test_date = "2026-04-15"
    test_smd = 5.2
    test_rain = 12.5
    test_score = "High Risk"
    
    explanation = generate_nora_reasoning(test_date, test_smd, test_rain, test_score)
    print(f"Recommendation: {test_score}\n Reason: {explanation}")
