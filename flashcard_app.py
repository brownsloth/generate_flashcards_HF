# app.py
import streamlit as st
import pandas as pd
import time
import os
import gc

# Set low-memory environment vars
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['STREAMLIT_SERVER_WATCH_DIRS'] = '[]'

# Import flashcard generator
from flashcard_generator import generate_flashcards

# Streamlit page config
st.set_page_config(
    page_title="Flashcard Generator",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("Flashcard Generator")
st.write("Upload or paste text to generate study flashcards.")

# === Input Methods
tab1, tab2 = st.tabs(["📝 Paste Text", "📁 Upload File"])

input_text = ""
with tab1:
    input_text = st.text_area("Enter your content here:", height=200)

with tab2:
    uploaded_file = st.file_uploader("Upload a .txt file", type=['txt'])
    if uploaded_file:
        try:
            input_text = uploaded_file.read().decode("utf-8")
            st.success("✅ Text loaded from file.")
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")

# === Sidebar Config
st.sidebar.header("⚙️ Configuration")

max_chunk_length = st.sidebar.slider(
    "Max Chunk Length",
    min_value=50,
    max_value=400,
    value=150,
    step=10,
    help="Shorter chunks = less memory used"
)

answer_length = st.sidebar.selectbox(
    "Answer Detail Level",
    options=["SHORT", "MEDIUM", "LONG"],
    index=1
)

def dynamic_answer_len(answer_length: str):
    return {
        "SHORT": 200,
        "MEDIUM": 400,
        "LONG": 800
    }.get(answer_length, 400)

# === Flashcard Generation
if 'flashcards' not in st.session_state:
    st.session_state.flashcards = []

if st.button("🚀 Generate Flashcards") and input_text.strip():
    st.info("Generating flashcards... be patient 👇")
    start_time = time.time()

    try:
        flashcards = generate_flashcards(
            input_text,
            max_len=dynamic_answer_len(answer_length)
        )

        st.session_state.flashcards = flashcards
        st.session_state.review_flashcards = flashcards.copy()  # 🔥 THIS FIXES YOUR ISSUE

        elapsed = time.time() - start_time
        st.success(f"✅ Done! {len(flashcards)} flashcards generated in {elapsed:.1f} sec.")

        gc.collect()
    except Exception as e:
        pass

# === Review Mode
st.markdown("---")
# Setup state for review
if "review_index" not in st.session_state:
    st.session_state.review_index = 0
if "show_answer" not in st.session_state:
    st.session_state.show_answer = False
if "review_flashcards" not in st.session_state:
    st.session_state.review_flashcards = st.session_state.flashcards.copy()

cards = st.session_state.review_flashcards
if cards:
    st.subheader("Review Flashcards One at a Time")

    idx = st.session_state.review_index % len(cards)
    card = cards[idx]

    st.markdown(f"### Card {idx + 1} / {len(cards)}")
    st.markdown(f"**Q:** {card['question']}")

    if st.session_state.show_answer:
        st.success(f"{card['answer']}")
    else:
        st.info("Click 'Flip' to reveal the answer.")

    # Add button flags to track clicks
    # Initialize action trigger
    if "button_action" not in st.session_state:
        st.session_state.button_action = None

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("⬅️ Previous"):
            st.session_state.review_index = (st.session_state.review_index - 1) % len(cards)
            st.session_state.show_answer = False
            st.rerun()

    with col2:
        if st.button("🔁 Shuffle"):
            import random
            random.shuffle(st.session_state.review_flashcards)
            st.session_state.review_index = 0
            st.session_state.show_answer = False
            st.rerun()

    with col3:
        if st.button("🔄 Flip"):
            st.session_state.show_answer = not st.session_state.show_answer
            st.rerun()

    with col4:
        if st.button("➡️ Next"):
            st.session_state.review_index = (st.session_state.review_index + 1) % len(cards)
            st.session_state.show_answer = False
            st.rerun()

    # === Unified control row: Restart, Download, Show/Hide All
    st.markdown("---")
    df = pd.DataFrame(st.session_state.flashcards)
    control1, control2, control3 = st.columns([1, 2, 1])
    if "show_all_cards" not in st.session_state:
        st.session_state.show_all_cards = 0

    with control1:
        if st.button("🔃 Restart Review"):
            st.session_state.review_index = 0
            st.session_state.show_answer = False
            st.rerun()

    with control2:
        st.download_button(
            label="⬇️ Download as CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="flashcards.csv",
            mime="text/csv"
        )

    with control3:
        toggle_label = "Hide All" if st.session_state.show_all_cards else "Show All"
        if st.button(toggle_label, key="toggle_show_all_btn"):
            st.session_state.show_all_cards = not st.session_state.show_all_cards
            st.rerun()

    if st.session_state.show_all_cards:
        st.markdown("### 📚 All Flashcards")
        for i, card in enumerate(st.session_state.flashcards):
            with st.expander(f"Card {i+1}: {card['question']}"):
                st.markdown(f"**Answer:**\n{card['answer']}")

