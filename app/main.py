import streamlit as st
from rag import ask_question

st.markdown("""# RAG On JFK
This app uses [LangChain](https://www.langchain.com/) to retrieve and generate answers to questions about
[John F. Kennedy's speeches](https://www.jfklibrary.org/archives/other-resources/john-f-kennedy-speeches). 
It uses a combination of [Pinecone](https://pinecone.io/) for vector storage and [OpenAI](https://openai.com/) 
for LLM based texxt generation. The front end is built using [Streamlit](https://streamlit.io/).
""")


question = st.text_input("Enter your question here", "How did Kennedy feel about the Soviet Union?")


if st.button("Submit"):
    index_name = "prez-speeches"

    with st.spinner("Ask not...", show_time=True):
        response = ask_question(question=question, index_name=index_name)

    st.markdown("#### Answer:")
    st.markdown(f"{response['answer']}")
    st.markdown("---")
    st.markdown("#### Sources:")

    for num, doc in enumerate(response["context"]):
        st.markdown(f"{num+1}. [{doc.metadata['title']}]({doc.metadata['url']})")
