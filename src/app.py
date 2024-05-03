#pip install streamlit langchain lanchain-openai beautifulsoup4 python-dotenv chromadb
import streamlit as st
from langchain_core.messages import AIMessage,HumanMessage
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever,create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
load_dotenv()

def get_context_retriever_chain(vector_store):
    llm = ChatOpenAI()
    retriever = vector_store.as_retriever()
    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("user","{input}"),
        ("user","This command commits any files you’ve added with the git add command and also commits any files you’ve changed since then")
    ])
    retriever_chain = create_history_aware_retriever(llm,retriever,prompt)
    return retriever_chain
def get_vectorstore_from_url(url):
    loader = WebBaseLoader(url)
    try:
        document = loader.load()
        text_splitter = RecursiveCharacterTextSplitter()
        document_chunks = text_splitter.split_documents(document)
        if not document_chunks:
            raise ValueError("No document chunks found")
        vector_store = Chroma.from_documents(document_chunks, OpenAIEmbeddings())
        return vector_store
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

def get_conversational_rag_chain(retriever_chain):
    llm=ChatOpenAI()
    prompt=ChatPromptTemplate.from_messages([
        ("system","answer the user's question :\n\n{context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user","{input}"),
    ])
    stuff_documents_chain=create_stuff_documents_chain(llm,prompt)
    return create_retrieval_chain(retriever_chain,stuff_documents_chain)

def get_response(user_input):
    retriever_chain = get_context_retriever_chain(st.session_state.vector_store)
    conversation_rag_chain = get_conversational_rag_chain(retriever_chain)
    response = conversation_rag_chain.invoke({
            "chat_history": st.session_state.chat_history,
            "input": user_query
        })
    return response['answer']

st.set_page_config(page_title="CHAT WITH WEBSITE", page_icon="page")
st.title("CHAT WITH WEBSITE")

with st.sidebar:
    st.header("settings")
    website_url = st.text_input("website url")

if  website_url  is None or website_url == "":
    st.info("You must provide a website url ")
else:
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            AIMessage(content="hello, iam a bot . how can i help you")]

    if "vector_store" not in st.session_state:
        st.session_state.vector_store = get_vectorstore_from_url(website_url)

    user_query = st.chat_input('type your message here')
    if user_query is not None and user_query!= "":
        response=get_response(user_query)
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        st.session_state.chat_history.append(AIMessage(content=response))
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.write(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.write(message.content)
