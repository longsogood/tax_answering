import streamlit as st
import pandas as pd
from langfuse import Langfuse
import requests
from streamlit import secrets
from uuid import uuid4
import pickle

LLAMA_API = secrets["LLAMA_API"]
CLAUDE_API = secrets["CLAUDE_API"]
GRADER_API = secrets["GRADER_API"]
LANGFUSE_PUBLIC_KEY = secrets["LANGFUSE_PUBLIC_KEY"]
LANGFUSE_SECRET_KEY = secrets["LANGFUSE_SECRET_KEY"]

langfuse = Langfuse(public_key=LANGFUSE_PUBLIC_KEY,
                    secret_key=LANGFUSE_SECRET_KEY,
                    host="https://us.cloud.langfuse.com")
current_id  = langfuse.fetch_traces(limit=1).data[0].id
def query(payload, prediction_url):
    # if st.selected_model == "Claude Sonnet 3.5":
    #     prediction_url = CLAUDE_API
    # elif st.selected_model == "Llama 3.3 70B":
    #     prediction_url = LLAMA_API 
    response = requests.post(f"{prediction_url}", json=payload)
    return response

def get_response():
    langfuse.fetch_traces(limit=1)
    

def display_record(record):
    # Display the selected record's details
    with st.container():
        st.subheader(f":green[Question:] {record['question']}")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader(":green[True answer:]")
            st.markdown(record["true_answer"])
        with col2:
            st.subheader(":green[Real answer:]")
            st.markdown(record["real_answer"])
        with col3:
            st.subheader(f":green[Score:] {record['quality_score']}")
            st.subheader(f":green[Evaluation:]")
            st.markdown(record["note"])

def filter_dataframe():
    filter = st.checkbox("Filter")
    st.session_state.filtered_df = st.session_state.df.copy()
    
    if not filter:
        return st.session_state.filtered_df
    
    st.session_state.filtered_df = st.session_state.filtered_df[st.session_state.filtered_df["real_answer"].isna()]
    return st.session_state.filtered_df

st.set_page_config(
    layout="wide", 
    initial_sidebar_state="expanded",
)

if "selected_model" not in st.session_state:
    st.session_state.selected_model = None

if "indices" not in st.session_state:
    st.session_state.indices = None

if "df" not in st.session_state:
    st.session_state.df = None

if "file_processed" not in st.session_state:
    st.session_state.file_processed = False

if "filtered_df" not in st.session_state:
    st.session_state.filtered_df = None



st.title("CMC Tax")
st.write(f"Current id: {current_id}")
st.session_state.df = pd.read_excel("data/tax_answering.xlsx")
st_df = st.dataframe(st.session_state.df, on_select="rerun", selection_mode="multi-row", use_container_width=True)

selected_rows = st_df.selection.rows
st.session_state.selected_indices = st.session_state.df.iloc[selected_rows].index

st.write("**Selected rows**")
process_df = st.session_state.df.loc[st.session_state.selected_indices]
st.dataframe(process_df, use_container_width=True)
# st.selected_model = st.radio(label="Select model",
#                     options=["Claude Sonnet 3.5", "Llama 3.3 70B"])
# question = st.text_area("Question")

questions = list(process_df.loc[:,"Câu hỏi"])
ground_truth_answers = list(process_df.loc[:, "Câu trả lời sau rà soát"])
# st.write(st.session_state.df.loc[st.session_state.selected_indices, :])
process_btn = st.button("Send")
if process_btn:
    llama_answers = []
    claude_answers = []
    compare_llama = []
    compare_claude = []
    for question, ground_truth_answer in zip(questions, ground_truth_answers):
        # Meta Llama
        payload = {"question": question}
        temp = query(payload, LLAMA_API)
        while True:
            data = langfuse.fetch_traces(limit=1).data[0]
            if current_id != data.id and data.output is not None:
                llama_answers.append(data.output["tax_llama"]["messages"][0]["kwargs"]["content"])
                current_id = data.id
                print("Checkpoint: Llama")
                break
        
        # Claude
        payload = {"question": question}
        temp = query(payload, CLAUDE_API)
        while True:
            data = langfuse.fetch_traces(limit=1).data[0]
            if current_id != data.id and data.output is not None:
                claude_answers.append(data.output["tax_claude"]["messages"][0]["kwargs"]["content"])
                current_id = data.id
                print("Checkpoint: Claude")
                break

        # Comparison Llama
        compare_question = f"""
        Ground-truth answer: {ground_truth_answer}\n
        LLM answer: {llama_answers[-1]}
"""
        payload = {"question": compare_question}
        temp = query(payload, GRADER_API)
        while True:
            data = langfuse.fetch_traces(limit=1).data[0]
            if current_id != data.id and data.output is not None:
                compare_llama.append(data.output["tax_grader"]["messages"][0]["kwargs"]["content"])
                current_id = data.id
                print("Checkpoint: Llama comparison")
                break

        # Compare Claude
        compare_question = f"""
        Ground-truth answer: {ground_truth_answer}\n
        LLM answer: {claude_answers[-1]}
"""
        payload = {"question": compare_question}
        temp = query(payload, GRADER_API)
        while True:
            data = langfuse.fetch_traces(limit=1).data[0]
            if current_id != data.id and data.output is not None:
                compare_claude.append(data.output["tax_grader"]["messages"][0]["kwargs"]["content"])
                current_id = data.id
                print("Checkpoint: Claude comparison")
                break
    
    pickle_file = {"Llama 3.3 70b": llama_answers,
                   "Claude sonnet 3.5": claude_answers,
                   "Llama vs. groundtruth": compare_llama,
                   "Claude vs. groundtruth": compare_claude
                   }
    
    with open('data/saved_dictionary.pkl', 'wb') as f:
        pickle.dump(pickle_file, f)
    
    for i in enumerate(list(st.session_state.selected_indices)):
        st.session_state.df.loc[i, "Llama 3.3 70b"] = llama_answers[i]
        st.session_state.df.loc[i, "Claude sonnet 3.5"] = claude_answers[i]
        st.session_state.df.loc[i, "Llama vs. groundtruth"] = compare_llama[i]
        st.session_state.df.loc[i, "Claude vs. groundtruth"] = compare_claude[i]
    st.write(st.session_state.df)