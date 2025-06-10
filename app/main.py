import streamlit as st
from rag import ask_question
import yaml
from typing import Dict, Any


st.set_page_config(
    page_title="RAG-JFK",
    page_icon=":eagle:",
)

with st.sidebar:
    st.page_link("https://michael-harmon.com", label="About Me", icon="👀")
    st.page_link("https://michael-harmon.com/blog/ragjfk1.html", label="Speeches & Data", icon="📊")
    st.page_link("https://michael-harmon.com/blog/ragjfk2.html", label="About RAG", icon="🤖")
    st.page_link("https://github.com/mdh266/rag-jfk", label="GitHub Rep", icon="🧑‍💻")



def main(config: Dict[str, Any], debug: bool = False) -> None:
    if debug:
        from dotenv import load_dotenv
        load_dotenv()

    st.markdown("""
    # :eagle: RAG On JFK Speeches
    This app uses [LangChain](https://www.langchain.com/) to retrieve and generate answers to questions about
    [John F. Kennedy's 800+ speeches](https://www.jfklibrary.org/archives/other-resources/john-f-kennedy-speeches). 
    It uses a combination of [Pinecone](https://pinecone.io/) for vector storage and retrieval, [Nvidia](https://python.langchain.com/api_reference/nvidia_ai_endpoints/embeddings/langchain_nvidia_ai_endpoints.embeddings.NVIDIAEmbeddings.html) for
    embeddings as well as [Llama 3.2](https://ai.meta.com/blog/llama-3-2-connect-2024-vision-edge-mobile-devices/) and [Groq](https://groq.com/) for generating answers. The frontend is built with
    [Streamlit](https://streamlit.io/) and it's deployed on [Google Cloud Run](https://cloud.google.com/run) using [Docker](https://www.docker.com/).
    """)

    question = st.text_input(
        "Enter your question here", "How did Kennedy feel about the Soviet Union?"
    )

    # k = st.slider("Number of sources", 0, 10, 5)

    if st.button("Submit"):
        index_name = config.get("index_name", "jfk-speeches")
        embedding_model = config.get("embedding_model", "nvidia/llama-3.2-nv-embedqa-1b-v2")
        dimension = config.get("dimension", 2048)
        model = config.get("model", "llama-3.3-70b-versatile")
        temperature = config.get("temperature", 0.0)

        with st.spinner("Ask not...", show_time=True):
            response = ask_question(question=question, 
                                    index_name=index_name,
                                    embedding_model=embedding_model,
                                    dimension=dimension,
                                    model=model,
                                    temperature=temperature)

        st.markdown("#### Answer:")
        st.markdown(f"{response['answer']}")
        st.markdown("---")
        st.markdown("#### Sources:")

        # TODO: Deduplicate the results
        speeches = response["context"]

        # deduplicate references
        # by using a set comprehension to extract unique (title, url) pairs
        references = {(doc.metadata['title'], doc.metadata['url'])
                      for doc in speeches}
        
        for num, reference in enumerate(references):
            st.markdown(f"{num + 1}. [{reference[0]}]({reference[1]})")


if __name__ == "__main__":
    with open('config.yml', 'r') as file:
        config = yaml.safe_load(file)

    main(config=config, debug=False)
