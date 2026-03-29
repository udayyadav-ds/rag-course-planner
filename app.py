import streamlit as st
import os
from rag import load_index, ask

st.set_page_config(page_title="Course Planning Assistant", page_icon="🎓", layout="wide")
st.title("🎓 Prerequisite & Course Planning Assistant")
st.caption("Grounded in MIT OpenCourseWare catalog documents")

with st.sidebar:
    st.header("📋 Student Profile")
    completed = st.text_area("Completed Courses (one per line)", placeholder="6.001\n18.06\n6.042J", height=120)
    target_major = st.text_input("Target Major", placeholder="Computer Science")
    target_term = st.selectbox("Target Term", ["Fall 2026", "Spring 2027", "Fall 2027"])
    max_courses = st.slider("Max Courses Next Term", 1, 6, 4)
    st.markdown("---")
    st.caption("Purple Merit Technologies Assessment")

@st.cache_resource(show_spinner="Loading index...")
def get_index():
    return load_index()

index, chunks, sources = get_index()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("📚 Sources"):
                for s in msg["sources"]:
                    st.markdown(f"- [{s}]({s})")

if user_input := st.chat_input("Ask about prerequisites, course plans, or requirements..."):
    profile = ""
    if completed.strip():
        profile += f"\nCompleted courses: {completed.strip()}"
    if target_major.strip():
        profile += f"\nTarget major: {target_major}"
    profile += f"\nTarget term: {target_term}, Max courses: {max_courses}"

    full_question = user_input + ("\n\nStudent profile:" + profile if profile else "")

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Searching catalog..."):
            answer, srcs = ask(full_question, index, chunks, sources)
        st.markdown(answer)
        if srcs:
            with st.expander("📚 Sources"):
                for s in srcs:
                    st.markdown(f"- [{s}]({s})")

    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": srcs})