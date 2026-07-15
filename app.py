import streamlit as st
from utils.pdf_reader import extract_text
from utils.text_splitter import split_text
from utils.vector_store import create_vector_store
from utils.chatbot import ask_pdf, generate_quiz

st.set_page_config(
    page_title="ChatPDF AI",
    page_icon="📄",
    layout="wide"
)

st.title("📄 ChatPDF AI")
st.write("Upload a PDF and chat with it.")

# Session State

if "quiz" not in st.session_state:
    st.session_state.quiz = None

if "current_question" not in st.session_state:
    st.session_state.current_question = 0

if "answers" not in st.session_state:
    st.session_state.answers = {}

# Upload PDF

uploaded_file = st.file_uploader(
    "Choose a PDF",
    type=["pdf"]
)

if uploaded_file is not None:

    st.success(f"✅ Uploaded: {uploaded_file.name}")

    try:
        # Extract text
        text = extract_text(uploaded_file)

        if not text.strip():
            st.error("No text found in the PDF.")
            st.stop()

        # Split text into chunks
        chunks = split_text(text)

        st.subheader("📊 Number of Chunks")
        st.write(len(chunks))

        # Create vector database
        with st.spinner("Creating AI database..."):
            vector_store = create_vector_store(chunks)

        st.success("✅ Vector Database Ready!")

        st.divider()

  
        # Ask AI

        st.subheader("💬 Ask Questions")

        question = st.text_input("Enter your question")

        col1, col2 = st.columns(2)

        with col1:
            ask_button = st.button(
                "💬 Ask AI",
                use_container_width=True
            )

        with col2:
            quiz_button = st.button(
                "📝 Generate Quiz",
                use_container_width=True
            )

        # Ask AI Logic

        if ask_button:

            if question.strip() == "":
                st.warning("Please enter a question.")

            else:

                with st.spinner("🤖 Gemini is thinking..."):
                    answer = ask_pdf(vector_store, question)

                st.success("Answer Generated!")

                st.markdown("## 🤖 Answer")
                st.markdown(answer)


        # Generate Quiz

        if quiz_button:

            with st.spinner("📝 Creating quiz..."):
                st.session_state.quiz = generate_quiz(vector_store)
                st.session_state.current_question = 0
                st.session_state.answers = {}

            st.success("✅ Quiz Generated!")

 
        # Show Quiz

        if (
            st.session_state.quiz is not None
            and isinstance(st.session_state.quiz, list)
            and len(st.session_state.quiz) > 0
        ):

            quiz = st.session_state.quiz
            index = st.session_state.current_question

            q = quiz[index]

            st.markdown("---")
            st.subheader(f"Question {index + 1} of {len(quiz)}")

            st.write(q["question"])

            # Remember previous answer
            previous_answer = st.session_state.answers.get(index)

            radio_index = None
            if previous_answer in q["options"]:
                radio_index = q["options"].index(previous_answer)

            selected = st.radio(
                "Choose your answer:",
                q["options"],
                index=radio_index,
                key=f"q{index}"
            )

            st.session_state.answers[index] = selected

            col_prev, col_next = st.columns(2)

            # Previous Button
            with col_prev:

                if index > 0:

                    if st.button(
                        "⬅ Previous",
                        use_container_width=True
                    ):
                        st.session_state.current_question -= 1
                        st.rerun()

            # Next / Submit
            with col_next:

                if index < len(quiz) - 1:

                    if st.button(
                        "Next ➜",
                        use_container_width=True
                    ):
                        st.session_state.current_question += 1
                        st.rerun()

                else:

                    if st.button(
                        "🏁 Submit Quiz",
                        use_container_width=True
                    ):

                        score = 0

                        for i, question in enumerate(quiz):

                            user_answer = st.session_state.answers.get(i)

                            if user_answer == question["answer"]:
                                score += 1

                        st.markdown("---")
                        st.header("🎉 Quiz Completed!")

                        st.success(
                            f"✅ Your Score: {score}/{len(quiz)}"
                        )

                        st.info(
                            f"✔ Correct Answers: {score}"
                        )

                        st.error(
                            f"❌ Wrong Answers: {len(quiz) - score}"
                        )

                        st.markdown("---")
                        st.subheader("📋 Review")

                        for i, question in enumerate(quiz):

                            user_answer = st.session_state.answers.get(i)

                            if user_answer == question["answer"]:

                                st.success(
                                    f"""
**Question {i+1}:**
{question['question']}

**Your Answer:** {user_answer}
✅ Correct
"""
                                )

                            else:

                                st.error(
                                    f"""
**Question {i+1}:**
{question['question']}

**Your Answer:** {user_answer}

**Correct Answer:** {question['answer']}
"""
                                )

    except Exception as e:
        st.error(f"❌ Error: {e}")