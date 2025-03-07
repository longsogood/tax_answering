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

def init():
    if "df" not in st.session_state:
        st.session_state.df = None

    if "file_processed" not in st.session_state:
        st.session_state.file_processed = False

    if "processed_df" not in st.session_state:
        st.session_state.processed_df = None

    if "selectedSourceDoc" not in st.session_state:
        st.session_state.selectedSourceDoc = None

    if "claude_answers" not in st.session_state:
        st.session_state.claude_answers = []

    if "llama_answers" not in st.session_state:
        st.session_state.llama_answers = []

    if "compare_claude" not in st.session_state:
        st.session_state.compare_claude = []

    if "compare_llama" not in st.session_state:
        st.session_state.compare_llama = []

    if "claude_answers" not in st.session_state:
        st.session_state.claude_answers = []

def query(payload, prediction_url):
    # if st.selected_model == "Claude Sonnet 3.5":
    #     prediction_url = CLAUDE_API
    # elif st.selected_model == "Llama 3.3 70B":
    #     prediction_url = LLAMA_API 
    response = requests.post(f"{prediction_url}", json=payload)
    return response

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

def insert_to_df(df, claude_answers, llama_answers, compare_claude, compare_llama):
    for i, index in enumerate(list(st.session_state.selected_indices)):
        df.loc[index, "Llama 3.3 70b"] = llama_answers[i]
        df.loc[index, "Claude sonnet 3.5"] = claude_answers[i]
        df.loc[index, "Llama vs. groundtruth"] = compare_llama[i]
        df.loc[index, "Claude vs. groundtruth"] = compare_claude[i]
def add_to_df_callback():
    insert_to_df(df=st.session_state.df,
                claude_answers=st.session_state.claude_answers,
                llama_answers=st.session_state.llama_answers,
                compare_claude=st.session_state.compare_claude,
                compare_llama=st.session_state.compare_llama)
    st.session_state.df.to_excel("data/tax_answering.xlsx", index=False)
    st.rerun()

def reset_callback():
    st.session_state.df = None
    st.session_state.file_processed = False
    st.session_state.processed_df = None
    st.session_state.selectedSourceDoc = None
    st.session_state.claude_answers = []
    st.session_state.llama_answers = []
    st.session_state.compare_claude = []
    st.session_state.compare_llama = []
    st.session_state.claude_answers = []
    st.rerun()

st.set_page_config(
    layout="wide", 
    initial_sidebar_state="expanded",
)

init()

st.title("CMC Tax")
st.write(f"Current id: {current_id}")
st.session_state.df = pd.read_csv("data/tax_qa.csv")
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
    progress_percent = 0
    progress_bar = st.progress(0.0, text="Processing...")

    for index, question, ground_truth_answer in zip(st.session_state.selected_indices, questions, ground_truth_answers):
        # Meta Llama
        payload = {"question": question}
        temp = query(payload, LLAMA_API)
        while True:
            data = langfuse.fetch_traces(limit=1).data[0]
            if current_id != data.id and (data.output is not None and not isinstance(data.output, str)):
                st.session_state.llama_answers.append(data.output["tax_llama"]["messages"][0]["kwargs"]["content"])
                current_id = data.id
                print("Checkpoint: Llama")
                break

        progress_percent += 1/(len(questions) * 4)
        progress_bar.progress(progress_percent, text=f"Processing... (Generated completion from Llama for question {index})")

        # Claude
        payload = {"question": question}
        temp = query(payload, CLAUDE_API)
        while True:
            data = langfuse.fetch_traces(limit=1).data[0]
            if current_id != data.id and (data.output is not None and not isinstance(data.output, str)):
                st.session_state.claude_answers.append(data.output["tax_claude"]["messages"][0]["kwargs"]["content"])
                current_id = data.id
                print("Checkpoint: Claude")
                break
        
        progress_percent += 1/(len(questions) * 4)
        progress_bar.progress(progress_percent, text=f"Processing... (Generated completion from Claude for question {index})")

        # Comparison Llama
        compare_question = f"""
        Question: {question}
        Ground-truth answer: {ground_truth_answer}\n
        LLM answer: {st.session_state.llama_answers[-1]}
"""
        payload = {"question": compare_question}
        temp = query(payload, GRADER_API)
        while True:
            data = langfuse.fetch_traces(limit=1).data[0]
            if current_id != data.id and (data.output is not None and not isinstance(data.output, str)):
                st.session_state.compare_llama.append(data.output["tax_grader"]["messages"][0]["kwargs"]["content"])
                current_id = data.id
                print("Checkpoint: Llama comparison")
                break
        
        progress_percent += 1/(len(questions) * 4)
        progress_bar.progress(progress_percent, text=f"Processing... (Generated completion from grader for question {index})")

        # Compare Claude
        compare_question = f"""
        Question: {question}
        Ground-truth answer: {ground_truth_answer}\n
        LLM answer: {st.session_state.claude_answers[-1]}
"""
        payload = {"question": compare_question}
        temp = query(payload, GRADER_API)
        while True:
            data = langfuse.fetch_traces(limit=1).data[0]
            if current_id != data.id and (data.output is not None and not isinstance(data.output, str)):
                st.session_state.compare_claude.append(data.output["tax_grader"]["messages"][0]["kwargs"]["content"])
                current_id = data.id
                print("Checkpoint: Claude comparison")
                break
        
        progress_percent += 1/(len(questions) * 4)
        progress_bar.progress(progress_percent, text=f"Processing... (Generated completion from grader for question {index})")
    
    # pickle_file = {"Llama 3.3 70b": llama_answers,
    #                "Claude sonnet 3.5": claude_answers,
    #                "Llama vs. groundtruth": compare_llama,
    #                "Claude vs. groundtruth": compare_claude
    #                }
    st.session_state.processed_df = process_df
    insert_to_df(df=st.session_state.processed_df,
                claude_answers=st.session_state.claude_answers,
                llama_answers=st.session_state.llama_answers,
                compare_claude=st.session_state.compare_claude,
                compare_llama=st.session_state.compare_llama)
    
    with open("llama_answers.pkl", 'wb') as f:
        pickle.dump(st.session_state.llama_answers, f)
        f.close()
    
    with open("claude_answers.pkl", "wb") as f:
        pickle.dump(st.session_state.claude_answers, f)
        f.close()

    with open("compare_llama.pkl", "wb") as f:
        pickle.dump(st.session_state.compare_llama, f)
        f.close()
    
    with open("compare_claude.pkl", "wb") as f:
        pickle.dump(st.session_state.compare_claude, f)
        f.close()

    progress_bar.empty()
    st.session_state.file_processed = True

# if st.session_state.file_processed:
#     st.dataframe(st.session_state.processed_df)

#     options = st.selectbox("Choose observation", options = list(st.session_state.processed_df.index))
#     st.session_state.selectedSourceDoc = st.session_state.processed_df.loc[options,:]
#     st.header(":green[Question]")
#     with st.expander("Question", expanded=True):
#         st.text(st.session_state.selectedSourceDoc["Câu hỏi"])
#     claudeTab, llamaTab = st.tabs(["Claude", "Llama"])
#     with claudeTab:
#         groundTruthCol1, claudeCol, claudeComparisonCol = st.columns(3)
#         with groundTruthCol1:
#                 st.header(":green[Ground Truth]")
#                 with st.container(height=500):
#                     with st.expander("Ground truth", expanded=True):
#                         st.text(st.session_state.selectedSourceDoc["Câu trả lời sau rà soát"])

#         with claudeCol:
#                 st.header(":green[Claude answer]")
#                 with st.container(height=500):
#                     with st.expander("Answer", expanded=True):
#                         st.text(st.session_state.selectedSourceDoc["Claude sonnet 3.5"])

#         with claudeComparisonCol:
#                 st.header(":green[Claude vs. groundtruth]")
#                 with st.container(height=500):
#                     with st.expander("Answer", expanded=True):
#                         st.text(st.session_state.selectedSourceDoc["Claude vs. groundtruth"])

#     with llamaTab:
#         groundTruthCol2, llamaCol, llamaComparisonCol = st.columns(3)
#         with groundTruthCol2:
#                 st.header(":green[Ground Truth]")
#                 with st.container(height=500):
#                     with st.expander("Ground truth", expanded=True):
#                         st.text(st.session_state.selectedSourceDoc["Câu trả lời sau rà soát"])
#         with llamaCol:
#                 st.header(":green[Llama answer]")
#                 with st.container(height=500):
#                     with st.expander("Answer", expanded=True):
#                         st.text(st.session_state.selectedSourceDoc["Llama 3.3 70b"])

#         with llamaComparisonCol:
#                 st.header(":green[Llama vs. groundtruth]")
#                 with st.container(height=500):
#                     with st.expander("Answer", expanded=True):
#                         st.text(st.session_state.selectedSourceDoc["Llama vs. groundtruth"])


#     add_to_df_btn = st.button("Add to dataframe", use_container_width=True, on_click=add_to_df_callback)
#     reset_btn = st.button("Reset", use_container_width=True, on_click=reset_callback)
        

