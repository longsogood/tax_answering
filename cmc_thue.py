import streamlit as st
import pandas as pd
from langfuse import Langfuse
import requests
from streamlit import secrets

LLAMA_API = secrets["LLAMA_API"]
CLAUDE_API = secrets["CLAUDE_API"]
LANGFUSE_PUBLIC_KEY = secrets["LANGFUSE_PUBLIC_KEY"]
LANGFUSE_SECRET_KEY = secrets["LANGFUSE_SECRET_KEY"]

langfuse = Langfuse(public_key=LANGFUSE_PUBLIC_KEY,
                    secret_key=LANGFUSE_SECRET_KEY,
                    host="https://us.cloud.langfuse.com")
def query(payload):
    response = requests.post(f"{API_URL_PREDICTION}/{GRADER_ID}", json=payload)
    return response.json()

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

st.title("CMC Grader")
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file:
    # st.session_state.df = pd.read_csv(uploaded_file)

    # st.write(f"**{uploaded_file.name}**")
    # st_df = st.dataframe(filter_dataframe(), on_select="rerun", selection_mode="multi-row", use_container_width=True)

    # selected_rows = st_df.selection.rows
    # st.session_state.selected_indices = st.session_state.filtered_df.iloc[selected_rows].index

    # st.write("**Selected rows**")
    # process_df = st.session_state.filtered_df.loc[st.session_state.selected_indices]
    # st.dataframe(process_df, use_container_width=True)

    process_btn = st.button("Process")
    if process_btn and not st.session_state.file_processed:
        # questions = process_df.loc[process_df["real_answer"].isna(), "question"].values
        # true_answers = process_df.loc[process_df["real_answer"].isna(), "true_answer"].values
        # condition = process_df["real_answer"].isna()

        # st.session_state.indices = process_df.index[condition].tolist()
        
        st.session_state.realAnswer_fill_values = {(index, "real_answer"): "" for index in st.session_state.indices}
        st.session_state.qualityScore_fill_values = {(index, "quality_score"): "" for index in st.session_state.indices}
        st.session_state.note_fill_values = {(index, "note"): "" for index in st.session_state.indices}

        progress_percent = 0
        progress_bar = st.progress(0.0, text="Processing...")
        
        for index, question, true_answer in zip(st.session_state.selected_indices, questions, true_answers):
            response = query({
                "question": f"""Question: {question}
            True answer: {true_answer}""",
            })
            
            result = response['agentReasoning'][1]['state']
            st.session_state.realAnswer_fill_values[index, "real_answer"] = result["real_answer"]
            st.session_state.qualityScore_fill_values[index, "quality_score"] = result["quality_score"]
            st.session_state.note_fill_values[index, "note"] = result["note"]

            progress_percent += 1/len(st.session_state.indices)
            progress_bar.progress(progress_percent, text="Processing...")
        
        progress_bar.empty()
        st.session_state.file_processed = True

if st.session_state.file_processed:
    processed_df = st.session_state.df.iloc[st.session_state.selected_indices]
    for (index, col), content in st.session_state.realAnswer_fill_values.items():
        processed_df.loc[index, col] = content

    for (index, col), content in st.session_state.qualityScore_fill_values.items():
        processed_df.loc[index, col] = content

    for (index, col), content in st.session_state.note_fill_values.items():
        processed_df.loc[index, col] = content
    st.dataframe(processed_df)
    selected_index = st.selectbox(label="Choose record to show:",
                                    options=st.session_state.indices,)
    selected_record = processed_df.loc[selected_index, :]
    display_record(selected_record)
