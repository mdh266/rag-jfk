# LangChain
from langchain_google_community.gcs_directory import GCSDirectoryLoader
from langchain_community.document_loaders import JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_pinecone.vectorstores import PineconeVectorStore
from langchain_core.documents import Document

import asyncio
import os
from typing import Dict, List

# Google Cloud
from google.oauth2 import service_account

from pinecone import Pinecone
from pinecone import ServerlessSpec

# Load environment variables
from dotenv import load_dotenv
load_dotenv()



def metadata_func(record: Dict[str, str], metadata: Dict[str, str]) -> Dict[str, str]:
    metadata["title"] = record.get("title")
    metadata["source"] = record.get("source")
    metadata["url"] = record.get("url")
    metadata["filename"] = record.get("filename")
    return metadata

    
def load_json(file_path: str, jq_schema: str=".") -> JSONLoader:
    return JSONLoader(
                file_path, 
                jq_schema=jq_schema, 
                text_content=False,
                content_key="text",
                metadata_func=metadata_func)


# async def load_documents(
#         loader: GCSDirectoryLoader,
#         text_splitter: RecursiveCharacterTextSplitter
# ) -> List[Document]:
#     documents = loader.alazy_load()
#     return await text_splitter.atransform_documents([document async for document in documents])

# async def insert_documents(
#         dimension: int,
#         model: str,
#         index_name: str,
#         documents: List[Document]
# ) -> None:
    
#     embedding = NVIDIAEmbeddings(
#                             model=model,
#                             api_key=os.getenv("NVIDIA_API_KEY"),
#                             dimension=dimension,
#                             truncate="NONE",
#                             )

#     vectordb = PineconeVectorStore(
#                 pinecone_api_key=os.getenv("PINECONE_API_KEY"),
#                 embedding=embedding,
#                 index_name=index_name
#     )

#     await vectordb.aadd_documents(documents=documents)


async def load_documents(
        loader: GCSDirectoryLoader,
        text_splitter: RecursiveCharacterTextSplitter,
        dimension: int,
        model: str,
        index_name: str
) -> List[Document]:
    
    embedding = NVIDIAEmbeddings(
                            model=model,
                            api_key=os.getenv("NVIDIA_API_KEY"),
                            dimension=dimension,
                            truncate="NONE",
                            )

    vectordb = PineconeVectorStore(
                pinecone_api_key=os.getenv("PINECONE_API_KEY"),
                embedding=embedding,
                index_name=index_name
    )
    documents = loader.alazy_load()

    async for document in documents:
        docs = await text_splitter.atransform_documents([document])
        await vectordb.aadd_documents(documents=docs)




async def main(
            project_name: str,
            bucket: str,
            index_name: str,
            dimension: int,
            model: str,
            chunk_size=2_000,
            chunk_overlap=100
) -> None:

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, 
                                                   chunk_overlap=chunk_overlap)

    loader = GCSDirectoryLoader(
                project_name=project_name,
                bucket=bucket,
                loader_func=load_json)

    await load_documents(
                    loader=loader,
                    text_splitter=text_splitter,
                    dimension=dimension,
                    model=model,
                    index_name=index_name)


def create_pinecone_index(
        index_name: str,
        dimension: int
) -> None:
    
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

    # delete the index if it exists
    if pc.has_index(index_name):
        pc.delete_index(index_name)

    # create the index
    pc.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
            )
    )

if __name__ == "__main__":
    # 149.48s user 6.55s system 22% cpu 11:25.25 total
    bucket = "kennedyskis"
    index_name = "jfk-speeches"
    dimension = 2048
    model = "nvidia/llama-3.2-nv-embedqa-1b-v2"

    credentials = service_account.Credentials.from_service_account_file('../credentials.json')
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../credentials.json"

    create_pinecone_index(
        index_name=index_name,
        dimension=dimension
    )

    asyncio.run(
        main(
            project_name=credentials.project_id,
            bucket=bucket,
            index_name=index_name,
            dimension=dimension,
            model=model
        )
    )
