import streamlit as st
from plp_engine import PLPSystem
from plp_agent import create_agent_executor # Import the agent creator
from config import LEARNING_QUESTIONS, FINAL_DISCLAIMER

# --- UI CONFIGURATION ---
st.set_page_config(page_title="Science of Weight Loss PLP", layout="wide")
st.title("The Science of Weight Loss PLP")
st.write("Ask a question below, or select a topic from the learning path on the left.")

# --- INITIALIZE SESSION STATE ---
if 'completed_topics' not in st.session_state:
    st.session_state.completed_topics = []
if 'question_input' not in st.session_state:
    st.session_state.question_input = ""

# --- LOAD THE SYSTEMS ---
@st.cache_resource
def load_plp_system():
    return PLPSystem()

@st.cache_resource
def load_agent_executor():
    return create_agent_executor()

plp = load_plp_system()
agent_executor = load_agent_executor()

# --- SIDEBAR FOR GUIDED LEARNING PATH ---
st.sidebar.title("Your Learning Path")
st.sidebar.write("Click a topic to explore it. Your progress will be saved for this session.")

for topic in LEARNING_QUESTIONS:
    status_icon = "✅" if topic in st.session_state.completed_topics else "⬜️"
    if st.sidebar.button(f"{status_icon} {topic}", use_container_width=True):
        st.session_state.question_input = topic
        if topic not in st.session_state.completed_topics:
            st.session_state.completed_topics.append(topic)

# --- MAIN APP INTERFACE & USER INTERACTION ---
use_reasoning_agent = st.checkbox("Enable Reasoning Agent (Bonus Feature)")

question = st.text_input(
    "Ask your question:",
    placeholder="Select a topic from the sidebar or type your own question...",
    key="question_input"
)

if st.button("Get Answer"):
    if question:
        if question in LEARNING_QUESTIONS and question not in st.session_state.completed_topics:
            st.session_state.completed_topics.append(question)
            st.rerun()

        with st.spinner("Thinking..."):
            answer = ""
            sources_to_display = []
            
            if use_reasoning_agent:
                st.info("Using Reasoning Agent...")
                response = agent_executor.invoke({"input": question})
                answer = response.get("output", "I could not find an answer.")
            else:
                st.info("Using Standard RAG...")
                response = plp.ask(question)
                answer = response.get("answer", "I could not find an answer.")
                if "context" in response:
                    for doc in response["context"]:
                        source_file = doc.metadata.get('source', 'Unknown').split('/')[-1]
                        page = doc.metadata.get('page', 'N/A')
                        source_info = f"- **{source_file}** (Page: {page})"
                        if source_info not in sources_to_display:
                            sources_to_display.append(source_info)
            
            # --- Display the results ---
            st.subheader("Answer:")
            st.write(answer)
            st.write(FINAL_DISCLAIMER)
            
            if sources_to_display:
                st.subheader("Sources Used:")
                for source in sources_to_display:
                    st.write(source)
            elif use_reasoning_agent:
                st.subheader("Sources Used:")
                st.write("The agent accessed the 'Weight_Loss_Science_Knowledge_Base' tool to formulate its answer. The detailed thought process and source access are visible in the terminal logs.")

    else:
        st.warning("Please enter a question.")