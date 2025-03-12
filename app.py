import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template
from dotenv import load_dotenv
import time
from openai import OpenAIError
import emoji
import os

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

def preprocess_text(input_text):
    # Replace emojis with a special token
    processed_text = emoji.demojize(input_text, delimiters=("", ""))
    return processed_text

def extract_pdf_text(pdf_documents):
    text = ""
    for pdf in pdf_documents:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def textChunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def create_vectorStore(text_chunks):
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key) # type: ignore
    vector_store = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vector_store

def create_conversationChain(vector_store):
    language_model = ChatOpenAI(openai_api_key=openai_api_key) # type: ignore
    
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=language_model,
        retriever=vector_store.as_retriever(),
        memory=memory
    )
    return conversation_chain

def userInput(query):
    # Preprocess user input to handle emojis
    query = preprocess_text(query)

    try:
        start_time = time.time()
        response = st.session_state.conversation({'question': query})
        st.session_state.chat_history = response['chat_history']
        end_time = time.time()  # Record the end time
        response_time = end_time - start_time  # Calculate the response time in seconds

        for i, message in enumerate(st.session_state.chat_history):
            if i % 2 == 0:
                st.write(user_template.replace(
                    "{{MSG}}", message.content), unsafe_allow_html=True)
            else:
                st.write(bot_template.replace(
                    "{{MSG}}", message.content), unsafe_allow_html=True)

        # Display the response time
        st.write(f"Bot Response Time: {response_time:.2f} seconds")

    except OpenAIError as e:
        st.warning(f"OpenAI error: {e}")
        # Handle the error as needed, for example, by displaying a warning to the user

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        # Handle other unexpected errors


def main():
    try:
        st.set_page_config(page_title="PDFs Chatbot", page_icon=":robot_face:")
        st.write(css, unsafe_allow_html=True)

        if "conversation" not in st.session_state:
            st.session_state.conversation = None
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = None
        if "processing_done" not in st.session_state:
            st.session_state.processing_done = False

        st.markdown("<h1 style='text-align:center; color:#66ffcc;'>Chat with your PDFs</h1>", unsafe_allow_html=True)

        st.markdown("<h2 style='text-align:center; color:red;'>Upload Your PDFs Below 👇👇👇</h2>", unsafe_allow_html=True)

        pdf_documents = st.file_uploader("Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
    
        # Check if any file is uploaded and if it's a PDF
        if pdf_documents:
            # Check for duplicate filenames
            pdf_names = [pdf.name.lower() for pdf in pdf_documents]
            if len(pdf_names) != len(set(pdf_names)):
                st.error("Duplicate PDF are not allowed.")
                return

            if all(pdf.name.lower().endswith('.pdf') for pdf in pdf_documents):
                if st.button("Process"):
                    with st.spinner("Processing"):
                        file_process_start = time.time()
                    
                        # extract pdf text
                        raw_text = extract_pdf_text(pdf_documents)
                    
                        # split the text into chunks
                        text_chunks = textChunks(raw_text)

                        # create vector store
                        vector_store = create_vectorStore(text_chunks)

                        # create conversation chain
                        st.session_state.conversation = create_conversationChain(vector_store)
                    
                        file_process_end = time.time()
                        file_process_time = file_process_end - file_process_start
                        st.info(f"File processed in {file_process_time:.2f} seconds")
                    
                        # Set processing status to True
                        st.session_state.processing_done = True

                        # Ask for the summary after processing
                        query = "Summary of documents"
                        userInput(query)
            else:
                st.error("Please upload only PDF files.")
            
        st.markdown("<h3 style='text-align:center; color:White;'>Start Your Chat</h3>", unsafe_allow_html=True)

        # Check if processing is done and the user has asked a question
        if st.session_state.processing_done and st.session_state.chat_history:
            user_query = st.text_input("Ask a question about your documents:")
            if user_query:
                userInput(user_query)
        elif st.session_state.processing_done:
            st.info("You can now ask questions.")
        else:
            st.info("Please upload PDFs and wait until processing is done.")
            
    except OpenAIError as e:
        st.warning(f"OpenAI error: {e}")
        # Handle the error as needed, for example, by displaying a warning to the user

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        # Handle other unexpected errors

if __name__ == '__main__':
    main()
