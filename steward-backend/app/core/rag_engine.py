import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "data/chroma")

def answer_query(question: str):
    if not OPENAI_API_KEY:
        return {"answer": "❌ Missing OpenAI API key.", "sources": []}

    # Initialize components
    embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
    vectordb = Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embeddings
    )
    retriever = vectordb.as_retriever(search_kwargs={"k": 4})

    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.2,
        api_key=OPENAI_API_KEY
    )

    # Build the RAG chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )

    # Run query
    response = qa_chain({"query": question})
    answer = response["result"]
    sources = [doc.metadata.get("source") for doc in response["source_documents"]]

    return {
        "answer": answer.strip(),
        "sources": list(set(sources))  # remove duplicates
    }
