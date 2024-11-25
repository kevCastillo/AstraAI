# streamlit_app.py
import os
import tempfile
import streamlit as st
from astra_ai import AstraAI


def initialize_session_state():
    """Initialize or reset session state variables"""
    if 'astra' not in st.session_state:
        st.session_state.astra = AstraAI()
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = "chat"
    if 'document_loaded' not in st.session_state:
        st.session_state.document_loaded = False


def handle_file_upload(uploaded_file):
    """
    Handle document upload with improved error handling and validation
    """
    if uploaded_file is None:
        return False

    try:
        # Check file size
        file_size = uploaded_file.size
        if file_size == 0:
            st.error("❌ The uploaded file is empty")
            return False

        # Create temp directory if it doesn't exist
        temp_dir = tempfile.mkdtemp()

        try:
            # Save uploaded file to temp location
            temp_file_path = os.path.join(temp_dir, uploaded_file.name)

            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getvalue())

            # Attempt to load document
            with st.spinner("Processing document..."):
                content = st.session_state.astra.load_document(temp_file_path)

            # Clean up temp file
            os.unlink(temp_file_path)
            os.rmdir(temp_dir)

            if not content:
                if st.session_state.astra.last_error:
                    st.error(f"❌ Error processing document: {st.session_state.astra.last_error}")
                else:
                    st.error("❌ Could not extract content from the document")
                return False

            # Update session state
            st.session_state.astra.context = content
            st.session_state.document_loaded = True

            # Show success message with document details
            st.success(f"""✅ Document loaded successfully!
                         \nFile: {uploaded_file.name}
                         \nSize: {format_file_size(file_size)}
                         \nContent length: {len(content)} characters""")
            return True

        finally:
            # Ensure cleanup of temp files
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)

    except Exception as e:
        st.error(f"❌ Error uploading document: {str(e)}")
        return False


def format_file_size(size_in_bytes):
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.1f} {unit}"
        size_in_bytes /= 1024
    return f"{size_in_bytes:.1f} TB"

def render_chat_interface():
    """Render the chat interface"""
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input(
            "Ask me anything about your document..." if st.session_state.astra.conversation_active
            else "Conversation ended. Start new session to continue."):

        if not st.session_state.astra.conversation_active:
            st.info("Please start a new session to continue.")
            return

        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.astra.ask_question(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

        # Check conversation state
        if not st.session_state.astra.conversation_active:
            st.info("Conversation ended. Start new session to continue.")


def render_quiz_interface():
    """Render the quiz interface with streak tracking and enhanced metrics"""
    if not st.session_state.document_loaded:
        st.warning("📚 Please upload a document first to start a quiz!")
        return

    # Quiz generation interface
    if not st.session_state.astra.quiz_active:
        st.write("### 📝 Generate a New Quiz")

        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            num_questions = st.slider(
                "Number of questions",
                min_value=3,
                max_value=10,
                value=5,
                help="Choose how many questions you want in your quiz"
            )

        with col2:
            if st.button("Start Quiz", type="primary", use_container_width=True):
                with st.spinner("🎯 Generating quiz questions..."):
                    if st.session_state.astra.generate_quiz(num_questions):
                        st.success("Quiz generated successfully! Good luck! 🍀")
                    else:
                        st.error("Failed to generate quiz. Please try again.")
                        if st.session_state.astra.last_error:
                            st.error(f"Error: {st.session_state.astra.last_error}")

        with col3:
            if st.button("Help", use_container_width=True):
                st.info("""
                    📌 Quiz Tips:
                    - Questions are based on your document
                    - Build your streak by getting consecutive answers correct
                    - Review explanations to learn more
                    - Track your progress with detailed metrics
                """)

    # Active quiz interface
    if st.session_state.astra.quiz_active:
        status = st.session_state.astra.get_quiz_status()

        # Progress bar and detailed statistics
        st.progress(status['progress'] / status['total_questions'])

        # Stats dashboard
        cols = st.columns(4)
        with cols[0]:
            st.metric("Score", f"{status['score']}/{status['total_questions']}")
        with cols[1]:
            st.metric("Progress", f"{status['progress'] + 1}/{status['total_questions']}")
        with cols[2]:
            st.metric("Percentage", f"{status['percentage']}%")
        with cols[3]:
            if status.get('current_streak', 0) > 0:
                st.metric("🔥 Streak", str(status['current_streak']))
                if status['current_streak'] >= 3:
                    st.markdown("🎯 You're on fire!")

        # Current question
        question = st.session_state.astra.get_current_question()
        if question:
            # Question container
            with st.container():
                st.subheader(f"Question {status['progress'] + 1}")
                st.write(question['question'])

                # Options with improved visual formatting
                option_cols = st.columns(2)
                for i, (key, value) in enumerate(question['options'].items()):
                    with option_cols[i // 2]:
                        if st.button(
                                f"{key}) {value}",
                                key=f"option_{key}",
                                use_container_width=True,
                                # Add some CSS styling for better button appearance
                                help=f"Select option {key}"
                        ):
                            # Handle answer submission
                            is_correct, explanation = st.session_state.astra.submit_answer(key)

                            if is_correct:
                                st.success("✅ Correct! 🎉")
                                if status.get('current_streak', 0) >= 2:
                                    st.balloons()
                            else:
                                st.error("❌ Incorrect!")

                            # Show explanation in an expander
                            with st.expander("📝 Explanation", expanded=True):
                                st.write(explanation)

                            # Quiz completion
                            if not st.session_state.astra.quiz_active:
                                st.balloons()
                                st.success("🎓 Quiz completed!")

                                # Final score card
                                score_cols = st.columns(3)
                                with score_cols[0]:
                                    st.metric("Final Score", f"{status['score']}/{status['total_questions']}")
                                with score_cols[1]:
                                    st.metric("Final Percentage", f"{status['percentage']}%")
                                with score_cols[2]:
                                    if status.get('current_streak', 0) > 0:
                                        st.metric("Final Streak", str(status['current_streak']))

                                # Achievement messages
                                if status['percentage'] == 100:
                                    st.success("🏆 Perfect Score! Excellent work!")
                                elif status['percentage'] >= 80:
                                    st.success("🌟 Great job! You've mastered this material!")
                                elif status['percentage'] >= 60:
                                    st.info("👍 Good effort! Keep practicing to improve!")

                                # Option to start new quiz
                                if st.button("Start New Quiz", type="primary"):
                                    st.rerun()
                            else:
                                # Continue to next question
                                st.write("---")
                                if st.button("Next Question ➡️", type="primary"):
                                    st.rerun()

        # Show streak milestone messages
        if status.get('current_streak', 0) == 3:
            st.success("🎯 Three in a row! Keep it up!")
        elif status.get('current_streak', 0) == 5:
            st.success("🔥 Five streak! You're unstoppable!")
        elif status.get('current_streak', 0) >= 7:
            st.success("⚡ Incredible streak! You're a quiz master!")


def main():
    """Main application function"""
    # Page configuration
    st.set_page_config(
        page_title="ASTRA AI",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize session state
    initialize_session_state()

    # Title and description
    st.title("ASTRA AI - Your Study Assistant 📚")

    # Sidebar
    with st.sidebar:
        st.header("Study Tools")

        # Mode selection
        mode = st.radio("Mode", ["Chat", "Quiz"], key="mode_select")
        st.session_state.current_mode = mode.lower()

        # Document upload section
        st.header("Document Upload")
        uploaded_file = st.file_uploader(
            "Upload your study material",
            type=['txt', 'pdf', 'docx'],
            help="""Supported formats:
                     \n- Text files (.txt)
                     \n- PDF documents (.pdf)
                     \n- Word documents (.docx)
                     \n\nEnsure your document contains readable text content."""
        )

        if uploaded_file:
            file_details = {
                "Filename": uploaded_file.name,
                "File size": format_file_size(uploaded_file.size),
                "File type": uploaded_file.type
            }

            # Show file details before processing
            st.write("File details:")
            for key, value in file_details.items():
                st.write(f"- {key}: {value}")

            if handle_file_upload(uploaded_file):
                st.success("Document ready for use!")
            else:
                st.error("Please try uploading a different document")

        # Session management
        st.header("Session Management")
        if st.button("Start New Session"):
            st.session_state.astra.reset_conversation()
            st.session_state.messages = []
            st.session_state.document_loaded = False
            st.success("Started new session! 🔄")

    # Main content area
    if st.session_state.current_mode == "chat":
        render_chat_interface()
    else:
        render_quiz_interface()

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>ASTRA AI - Your Personal Study Assistant</p>
            <p style='font-size: small'>Powered by Local LLM Technology</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()