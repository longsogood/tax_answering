import streamlit as st
import pandas as pd
import numpy as np
import streamlit_nested_layout

def init():
    if "df" not in st.session_state:
        st.session_state.df = None

    if "selected_index" not in st.session_state:
        st.session_state.selected_index = None

init()

st.set_page_config(
    layout="wide", 
    initial_sidebar_state="expanded",
)

uploaded_file = st.file_uploader("Choose a file to preview")
if uploaded_file:
    st.session_state.df = pd.read_excel(uploaded_file, sheet_name="Prompt 1 Generator 0 Grader 0")
    st_df = st.dataframe(st.session_state.df, selection_mode="single-row", use_container_width=True, hide_index=True, on_select="rerun")
    selected_row = st_df.selection.rows
    st.session_state.selected_index = st.session_state.df.iloc[selected_row].index

    question = st.session_state.df.loc[st.session_state.selected_index, "Question"].values[0]
    groundTruthAnswer = st.session_state.df.loc[st.session_state.selected_index, "Ground-truth answer"].values[0]
    llmAnswer = st.session_state.df.loc[st.session_state.selected_index, "LLM answer"].values[0]
    generation = st.session_state.df.loc[st.session_state.selected_index, "Generation"].values[0]
    generationScore = st.session_state.df.loc[st.session_state.selected_index, "Generation score"].values[0]
    sourcesLaws = st.session_state.df.loc[st.session_state.selected_index, "Sources - Laws"].values[0]
    sourcesLawsScore = st.session_state.df.loc[st.session_state.selected_index, "Sources - Laws score"].values[0]
    brevity = st.session_state.df.loc[st.session_state.selected_index, "Brevity"].values[0]
    brevityScore = st.session_state.df.loc[st.session_state.selected_index, "Brevity score"].values[0]
    comment = st.session_state.df.loc[st.session_state.selected_index, "Comment"].values[0]
    averageScore = st.session_state.df.loc[st.session_state.selected_index, "Average score"].values[0]
    strengthWeakness = st.session_state.df.loc[st.session_state.selected_index, "Strength Weakness"].values[0]
    

    # st.write(st.session_state.selected_index)
    st.markdown("<h2 style='text-align: center; color: green;'>Evaluate</h2>", unsafe_allow_html=True)
    with st.container(height=150):
        st.subheader(":green[Question]")
        st.write(question)

    with st.expander(label="Tổng thể", expanded=True):
        # st.markdown("**Claude Sonnet 3.5**")
        col11, col12, col13, col14 = st.columns(4)
        with col11:
            st.write(":green[**Câu trả lời sau rà soát**]")
            with st.expander(label="Ground-truth answer", expanded=True):
                st.write(groundTruthAnswer)
        with col12:
            st.write(":green[**LLM answer**]")
            with st.expander(label="LLM answer", expanded=True):
                st.write(llmAnswer)
        with col13:
            st.write(":green[**Đánh giá**]")
            with st.expander(label="Comment", expanded=True):
                st.write(f"Average score: {averageScore}\n\n{comment}")
        with col14:
            st.write(":green[Strength - Weakness]")
            with st.expander(label="Strength - Weakness", expanded=True):
                st.write(strengthWeakness)

    with st.expander(label="Generation", expanded=True):
        # st.markdown("**Claude Sonnet 3.5**")
        col21, col22, col23 = st.columns(3)
        with col21:
            st.write(":green[**Câu trả lời sau rà soát**]")
            with st.expander(label="Ground-truth answer", expanded=True):
                st.write(groundTruthAnswer)
        with col22:
            st.write(":green[**LLM answer**]")
            with st.expander(label="LLM answer", expanded=True):
                st.write(llmAnswer)
        with col23:
            st.write(":green[**Generation**]")
            with st.expander(label="Generation", expanded=True):
                st.write(f"Generation score: {generationScore}\n\n{comment}")

    with st.expander(label="Sources - Laws", expanded=True):
        # st.markdown("**Claude Sonnet 3.5**")
        col31, col32, col33 = st.columns(3)
        with col31:
            st.write(":green[**Câu trả lời sau rà soát**]")
            with st.expander(label="Ground-truth answer", expanded=True):
                st.write(groundTruthAnswer)
        with col32:
            st.write(":green[**LLM answer**]")
            with st.expander(label="LLM answer", expanded=True):
                st.write(llmAnswer)
        with col33:
            st.write(":green[**Sources - Laws**]")
            with st.expander(label="Sources - Laws", expanded=True):
                st.write(f"Sources - Laws score: {sourcesLawsScore}\n\n{comment}")

    with st.expander(label="Brevity", expanded=True):
        # st.markdown("**Claude Sonnet 3.5**")
        col41, col42, col43 = st.columns(3)
        with col41:
            st.write(":green[**Câu trả lời sau rà soát**]")
            with st.expander(label="Ground-truth answer", expanded=True):
                st.write(groundTruthAnswer)
        with col42:
            st.write(":green[**LLM answer**]")
            with st.expander(label="LLM answer", expanded=True):
                st.write(llmAnswer)
        with col43:
            st.write(":green[**Brevity**]")
            with st.expander(label="Brevity", expanded=True):
                st.write(f"Brevity score: {brevityScore}\n\n{comment}")

