import streamlit as st
import pandas as pd
import numpy as np
import streamlit_nested_layout

def init():
    if "score_df" not in st.session_state:
        st.session_state.score_df = None
    
    if "comment_df" not in st.session_state:
        st.session_state.comment_df = None

    if "selected_index" not in st.session_state:
        st.session_state.selected_index = None

init()

st.set_page_config(
    layout="wide", 
    initial_sidebar_state="expanded",
)

sheet_names = ["Điểm", "Đánh giá"]
uploaded_file = st.file_uploader("Choose a file to preview")
if uploaded_file:
    st.session_state.score_df = pd.read_excel(uploaded_file, sheet_name="Điểm", header=[0, 1])
    st.session_state.comment_df = pd.read_excel(uploaded_file, sheet_name="Đánh giá", header=[0, 1])

    score_sheet, comment_sheet = st.tabs(sheet_names)
    with score_sheet:
        st_df = st.dataframe(st.session_state.score_df, selection_mode="single-row", use_container_width=True, hide_index=True, on_select="rerun")
        selected_row = st_df.selection.rows
        st.session_state.selected_index = st.session_state.score_df.iloc[selected_row].index
        # st.write(st.session_state.selected_index)
        st.markdown("<h2 style='text-align: center; color: green;'>Comment</h2>", unsafe_allow_html=True)

        with st.expander(label="Claude 3.5", expanded=True):
            # st.markdown("**Claude Sonnet 3.5**")
            col11, col12, col13 = st.columns(3)
            with col11:
                st.write(":green[**Câu trả lời sau rà soát**]")
                with st.expander(label="Ground-truth answer", expanded=True):
                    st.write(st.session_state.comment_df.loc[st.session_state.selected_index, ("Câu trả lời sau rà soát", "Unnamed: 1_level_1")].values[0])
            with col12:
                st.write(":green[**Claude answer**]")
                with st.expander(label="LLM answer", expanded=True):
                    st.write(st.session_state.comment_df.loc[st.session_state.selected_index, ("LLM anwser", "Claude")].values[0])
            with col13:
                st.write(":green[**Đánh giá**]")
                with st.expander(label="Comment", expanded=True):
                    st.write(st.session_state.comment_df.loc[st.session_state.selected_index, ("Đánh giá", "Claude")].values[0])

        with st.expander(label="Llama", expanded=True):
            # st.markdown("**Claude Sonnet 3.5**")
            col11, col12, col13 = st.columns(3)
            with col11:
                st.write(":green[**Câu trả lời sau rà soát**]")
                with st.expander(label="Ground-truth answer", expanded=True):
                    st.write(st.session_state.comment_df.loc[st.session_state.selected_index, ("Câu trả lời sau rà soát", "Unnamed: 1_level_1")].values[0])
            with col12:
                st.write(":green[**Llama answer**]")
                with st.expander(label="LLM answer", expanded=True):
                    st.write(st.session_state.comment_df.loc[st.session_state.selected_index, ("LLM anwser", "Llama")].values[0])
            with col13:
                st.write(":green[**Đánh giá**]")
                with st.expander(label="Comment", expanded=True):
                    st.write(st.session_state.comment_df.loc[st.session_state.selected_index, ("Đánh giá", "Llama")].values[0])

        with st.expander(label="Claude 3.7", expanded=True):
            # st.markdown("**Claude Sonnet 3.5**")
            col11, col12, col13 = st.columns(3)
            with col11:
                st.write(":green[**Câu trả lời sau rà soát**]")
                with st.expander(label="Ground-truth answer", expanded=True):
                    st.write(st.session_state.comment_df.loc[st.session_state.selected_index, ("Câu trả lời sau rà soát", "Unnamed: 1_level_1")].values[0])
            with col12:
                st.write(":green[**Cucthue_chatbot answer**]")
                with st.expander(label="LLM answer", expanded=True):
                    st.write(st.session_state.comment_df.loc[st.session_state.selected_index, ("LLM anwser", "Claude 3.7")].values[0])
            with col13:
                st.write(":green[**Đánh giá**]")
                with st.expander(label="Comment", expanded=True):
                    st.write(st.session_state.comment_df.loc[st.session_state.selected_index, ("Đánh giá", "Claude 3.7")].values[0])

        with st.expander(label="Chatbot cục thuế", expanded=True):
            # st.markdown("**Claude Sonnet 3.5**")
            col11, col12, col13 = st.columns(3)
            with col11:
                st.write(":green[**Câu trả lời sau rà soát**]")
                with st.expander(label="Ground-truth answer", expanded=True):
                    st.write(st.session_state.comment_df.loc[st.session_state.selected_index, ("Câu trả lời sau rà soát", "Unnamed: 1_level_1")].values[0])
            with col12:
                st.write(":green[**Cucthue_chatbot answer**]")
                with st.expander(label="LLM answer", expanded=True):
                    st.write(st.session_state.comment_df.loc[st.session_state.selected_index, ("LLM anwser", "Chatbot cục thuế")].values[0])
            with col13:
                st.write(":green[**Đánh giá**]")
                with st.expander(label="Comment", expanded=True):
                    st.write(st.session_state.comment_df.loc[st.session_state.selected_index, ("Đánh giá", "Chatbot cục thuế")].values[0])           

    