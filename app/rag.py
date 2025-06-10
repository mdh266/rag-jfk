# LangChain
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import PromptTemplate
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_groq import ChatGroq


import os
from typing import Dict, Any


def ask_question(
        question: str, 
        index_name: str,
        embedding_model: str,
        dimension: int,
        model: str,
        temperature: float = 0.0,
        k: int = 5
        ) -> Dict[str, Any]:
    
    with open("app/prompt.txt") as f:
        template = f.read()

    prompt = PromptTemplate(
        template=template,
        input_variables=["input", "context"],
    )

    # embedding = OpenAIEmbeddings(model="text-embedding-ada-002")

    embedding = NVIDIAEmbeddings(
                            model=embedding_model,
                            api_key=os.getenv("NVIDIA_API_KEY"),
                            dimension=dimension,
                            truncate="NONE",
                            )
    
    vectordb = PineconeVectorStore(
        pinecone_api_key=os.getenv("PINECONE_API_KEY"),
        embedding=embedding,
        index_name=index_name,
    )

    llm = ChatGroq(model=model, temperature=temperature)

    generate_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)

    rag_chain = create_retrieval_chain(
        retriever=vectordb.as_retriever(k=k), combine_docs_chain=generate_chain
    )

    response = rag_chain.invoke({"input": question})

    return response
