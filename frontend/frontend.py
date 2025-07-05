import streamlit as st
import requests

st.set_page_config(page_title="JARVIS - Assistant", layout="centered")
st.title("🎤 JARVIS - Your AI Assistant")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


def add_message(role, message):
    st.session_state.chat_history.append((role, message))

def print_chat_history():
    for role, message in st.session_state.chat_history:
        st.markdown(f"**{role}:** {message}")

def user_input_call():
    st.subheader("💬 Conversation")
    if user_input:
        add_message("You", user_input)
        res = requests.post("http://backend:8000/command", json={"query": user_input})
        reply = res.json().get("response")
        add_message("Jarvis", reply)
        print_chat_history()

col1, col2 = st.columns([4, 1])
with col1:
    user_input = st.text_input("Type your command:", key="text_input")
    if st.button("📤 Send"):
        user_input_call()

with col2:
    if st.button("🎙️ Listen"):
        voice_res = requests.get("http://backend:8000/listen")
        user_input = voice_res.json().get("response")
        user_input_call()