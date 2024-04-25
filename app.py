import streamlit as st
from langchain_core.messages import AIMessage,HumanMessage
def get_response(user_input):
    return "i dont know"

st.set_page_config(page_title="CHAT WITH WEBSITE", page_icon="page")
st.title("CHAT WITH WEBSITE")
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
    AIMessage(content="hello, iam a bot . how can i help you")
]
with st.sidebar:
    st.header("settings")
    website_url = st.text_input("website url")

if  website_url  is None or website_url == "":
    st.info("You must provide a website url ")
else:
    user_query = st.chat_input('type your message here')
    if user_query is not None and user_query!= "":
        response = get_response(user_query)
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        st.session_state.chat_history.append(AIMessage(content=response))
    with st.sidebar:
        st.write(st.session_state.chat_history)
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.write(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.write(message.content)