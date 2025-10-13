import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

from config import CORPUS_PATH, DB_PATH, RETRIEVER_K, SYSTEM_PROMPT

class PLPSystem:
    def __init__(self):
        """
        Initializes the PLP system using the Gemini API.
        """
        load_dotenv()
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7, convert_system_message_to_human=True)
        self.gemini_db_path = f"{DB_PATH}_gemini"
        
        if not os.path.exists(self.gemini_db_path):
            print("Gemini vector store not found. Please run the ingest process.")
            self.vectordb = None
            self.rag_chain = None
        else:
            self.vectordb = Chroma(persist_directory=self.gemini_db_path, embedding_function=self.embeddings)
            self.rag_chain = self._create_rag_chain()

    def _create_rag_chain(self):
        """A private method to create the RAG chain."""
        retriever = self.vectordb.as_retriever(search_kwargs={"k": RETRIEVER_K})
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "{input}"),
        ])
        question_answer_chain = create_stuff_documents_chain(self.llm, prompt)
        return create_retrieval_chain(retriever, question_answer_chain)

    def ingest_data(self):
        """
        Processes source documents and builds the vector store using Gemini embeddings.
        """
        if os.path.exists(self.gemini_db_path):
            print(f"Gemini vector store already exists at '{self.gemini_db_path}'.")
            return

        print(f"Loading documents from {CORPUS_PATH}...")
        documents = []
        for file_name in os.listdir(CORPUS_PATH):
            if file_name.endswith(".pdf"):
                file_path = os.path.join(CORPUS_PATH, file_name)
                loader = PyMuPDFLoader(file_path)
                documents.extend(loader.load())
        
        print("Splitting documents into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)

        print(f"Creating and persisting Gemini vector store at '{self.gemini_db_path}'...")
        vectordb = Chroma.from_documents(
            documents=texts,
            embedding=self.embeddings,
            persist_directory=self.gemini_db_path
        )
        # vectordb.persist()
        print("Ingestion complete! Please restart the Streamlit app.")

    def ask(self, question: str):
        """
        Takes a user question, invokes the RAG chain, and returns the response.
        """
        if self.rag_chain is None:
            return {"answer": "The knowledge base is not loaded. Please run the data ingestion process."}
        
        return self.rag_chain.invoke({"input": question})