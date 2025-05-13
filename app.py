import streamlit as st
import pandas as pd

# --- Load data ---
@st.cache_data
def load_data():
    return pd.read_csv("Merchant Type Logic Build data.csv")

df = load_data()

# --- Initialize session state ---
if 'current_id' not in st.session_state:
    st.session_state.current_id = 1
if 'history' not in st.session_state:
    st.session_state.history = []
if 'comments' not in st.session_state:
    st.session_state.comments = []

# --- Get current row ---
def get_row_by_id(node_id):
    row = df[df["ID"] == node_id]
    return row.iloc[0] if not row.empty else None

# --- Reset everything ---
def reset():
    st.session_state.current_id = 1
    st.session_state.history = []
    st.session_state.comments = []

# --- Go back ---
def go_back():
    if st.session_state.history:
        last_step = st.session_state.history.pop()
        # Check if it's a comment
        if last_step[1] == 'Comment':
            # If it's a comment, we pop the last step and continue calling go_back until we find a question
            st.session_state.comments = [c for c in st.session_state.comments if c[0] != last_step[0]]
            go_back()
        else:
            # If it's a question, update current_id and go back to the previous question
            if st.session_state.history:
                st.session_state.current_id = last_step[0]
            else:
                # If history is empty, start again at the first question
                st.session_state.current_id = 1

# --- Show decision path ---
def show_path():
    st.subheader("🧭 Decision Path:")
    for node_id, answer in st.session_state.history:
        row = get_row_by_id(node_id)
        if row["Type"] == "C":
            st.markdown(f"💬 **Comment**: {row['Question']}")
        else:
            st.write(f"**Question:** {row['Question']} → **{answer}**")

# --- Main logic ---
row = get_row_by_id(st.session_state.current_id)

if row is None:
    st.error("Invalid node ID.")
    st.stop()

# Handle comments
if row["Type"] == "C":
    if st.session_state.current_id not in [c[0] for c in st.session_state.comments]:
        st.session_state.comments.append((st.session_state.current_id, row["Question"]))
    # Automatically go to next node (Yes path)
    st.session_state.history.append((st.session_state.current_id, "Comment"))
    st.session_state.current_id = row["Yes"]
    st.rerun()


# Display title and question
st.title("Merchant Type Decision Tree")
if row['Type'] == 'Q':
    st.markdown(f"<h2 style='font-size: 24px;'>{row['Question']}</h2>", unsafe_allow_html=True)


# End of tree
if row["Type"] in ["E", "A"]:

    if row['Type'] == 'E':
        st.success(f"🎯 **Merchant Type:** {row['Question']}")
    
    if row['Type'] == 'A':
        st.warning(f"🎯 **Action Required:** {row['Question']}")
        
    col1, col2, col3, col4 = st.columns(4)
    with col3:
        if st.button("🔙 Go Back"):
            go_back()
            st.rerun()
    with col4:
        if st.button("🔄 Restart"):
            reset()
            st.rerun()
else:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("✅ Yes"):
            st.session_state.history.append((st.session_state.current_id, "Yes"))
            st.session_state.current_id = row["Yes"]
            st.rerun()
    with col2:
        if st.button("❌ No"):
            st.session_state.history.append((st.session_state.current_id, "No"))
            st.session_state.current_id = row["No"]
            st.rerun()
    with col3:
        if st.button("🔙 Go Back"):
            go_back()
            st.rerun()
    with col4:
        if st.button("🔄 Restart"):
            reset()
            st.rerun()

# Display persistent comments

if st.session_state.comments:
    st.markdown("### 💬 Notes")
    for _, comment_text in st.session_state.comments:
        st.info(comment_text)

# Show decision path
with st.expander("", expanded=True):
    show_path()
