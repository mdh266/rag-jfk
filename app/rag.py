# LangChain
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import PromptTemplate

import os
from typing import Dict, Any


def ask_question(question: str, index_name: str) -> Dict[str, Any]:
    with open("app/prompt.txt") as f:
        template = f.read()

    prompt = PromptTemplate(
        template=template,
        input_variables=["input", "context"],
    )

    embedding = OpenAIEmbeddings(model="text-embedding-ada-002")

    vectordb = PineconeVectorStore(
        pinecone_api_key=os.getenv("PINECONE_API_KEY"),
        embedding=embedding,
        index_name=index_name,
    )

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    generate_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)

    rag_chain = create_retrieval_chain(
        retriever=vectordb.as_retriever(), combine_docs_chain=generate_chain
    )

    response = rag_chain.invoke({"input": question})

    return response
