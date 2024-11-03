import os
from typing import List
from sentence_transformers import SentenceTransformer
from langchain.schema import Document
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from dotenv import load_dotenv
load_dotenv()
hf_api_key = os.getenv("HF_TOKEN")
# hf_api_key = "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"
class CustomEmbeddings:
    def __init__(self, model_name: str, batch_size: int = 32):
        self.model = SentenceTransformer(model_name)
        self.batch_size = batch_size

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        embeddings = []
        for i in range(0, len(documents), self.batch_size):
            batch = documents[i:i + self.batch_size]
            embeddings.extend(self.model.encode(batch, convert_to_numpy=True).tolist())
        return embeddings

    def embed_query(self, query: str) -> List[float]:
        return self.model.encode([query], convert_to_numpy=True)[0].tolist()
    
# Load documents from a CSV file and split into chunks
def load_documents(file_path: str) -> List[Document]:
    loader = CSVLoader(file_path=file_path)
    docs = loader.load_and_split()
    return [Document(page_content=chunk.page_content) for chunk in docs]

# Create vector store for document storage and retrieval
def create_vector_store(documents: List[Document], model_name: str, persist_directory: str) -> Chroma:
    embedding_model = HuggingFaceInferenceAPIEmbeddings(api_key=hf_api_key, model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(documents=documents, embedding=embedding_model, persist_directory=persist_directory)
    return vectorstore

def initialize_chain(documents):
    try:
        # Set up vector store for embeddings
        persist_directory = os.path.expanduser("~/chromadb")
        vectorstore = create_vector_store(documents=documents, persist_directory=persist_directory, model_name='sentence-transformers/all-MiniLM-L6-v2')

        # Define individual retrievers
        vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
        keyword_retriever = BM25Retriever.from_documents(documents)
        keyword_retriever.k = 2

        # Combine retrievers in an ensemble
        retriever = EnsembleRetriever(retrievers=[vector_retriever, keyword_retriever], weights=[0.5, 0.5])

        # Initialize the chatbot with the configured chain
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set.")

        # Set up ChatGroq with the required parameters
        chat = ChatGroq(temperature=0, groq_api_key=api_key, model_name="Llama3-70b-8192")

        # Define the prompt template
        template = """
        User: You are an AI Assistant that follows instructions extremely well.
        Please be truthful and give direct answers. Please tell 'I don't know' if user query is not in CONTEXT

        Keep in mind, you will lose the job, if you answer out of CONTEXT questions

        CONTEXT: {context}
        Query: {question}

        Remember only return AI answer
        Assistant:
        """
        prompt = ChatPromptTemplate.from_template(template)
        output_parser = StrOutputParser()

        chain = (
            {
                "context": retriever.with_config(run_name="Docs"),
                "question": RunnablePassthrough(),
            }
            | prompt
            | chat
            | output_parser
        )

        return chain
    except Exception as e:
        raise Exception(f"Chain initialization failed: {e}")

# Global retriever variable
retriever = None
