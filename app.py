import streamlit as st
from plp_engine import PLPSystem
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

# --- LOAD THE PLP SYSTEM ---
@st.cache_resource
def load_plp_system():
    return PLPSystem()

plp = load_plp_system()

# --- SIDEBAR FOR GUIDED LEARNING PATH ---
st.sidebar.title("Your Learning Path")
st.sidebar.write("Click a topic to explore it. Your progress will be saved for this session.")

for topic in LEARNING_QUESTIONS:
    # Determine the status icon based on completion
    status_icon = "✅" if topic in st.session_state.completed_topics else "⬜️"

    # Create a button for each topic
    if st.sidebar.button(f"{status_icon} {topic}", use_container_width=True):
        # When a button is clicked, update the main text input
        st.session_state.question_input = topic
        # And mark the topic as completed
        if topic not in st.session_state.completed_topics:
            st.session_state.completed_topics.append(topic)

# --- MAIN APP INTERFACE & USER INTERACTION ---
question = st.text_input(
    "Ask your question:",
    placeholder="Select a topic from the sidebar or type your own question...",
    key="question_input" # This key links the text box to the sidebar buttons
)

if st.button("Get Answer"):
    if question:
        # Mark the topic as completed if a custom question is asked that matches a learning question
        if question in LEARNING_QUESTIONS and question not in st.session_state.completed_topics:
            st.session_state.completed_topics.append(question)
            st.rerun() # Rerun to update the sidebar icon immediately

        with st.spinner("Thinking..."):
            response = plp.ask(question)
            
            st.subheader("Answer:")
            st.write(response["answer"])
            st.write(FINAL_DISCLAIMER)
            
            if "context" in response:
                st.subheader("Sources Used:")
                sources = []
                for doc in response["context"]:
                    source_file = doc.metadata.get('source', 'Unknown').split('/')[-1]
                    page = doc.metadata.get('page', 'N/A')
                    source_info = f"- **{source_file}** (Page: {page})"
                    if source_info not in sources:
                        sources.append(source_info)
                for source in sources:
                    st.write(source)
    else:
        st.warning("Please enter a question.")