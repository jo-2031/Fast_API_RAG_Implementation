# main.py
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
import os
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain.schema import Document
from .database import SessionLocal, engine, Base
from .models import UserResponse
from .auth import AuthService
from .rag import CustomEmbeddings, initialize_chain

# Initialize FastAPI app
app = FastAPI()
auth_service = AuthService()

# Create the database tables
Base.metadata.create_all(bind=engine)

# Set up data directory
folder_path = "/Users/jothikaravichandran/Library/CloudStorage/OneDrive-TalentshipGmbH/Learning Project/Sample API/data"
os.makedirs(folder_path, exist_ok=True)

# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Global variable for storing file data
documents = []

# API endpoint to register a new user
@app.post("/register", response_model=UserResponse)
async def register(username: str, password: str, db: Session = Depends(get_db)):
    user = auth_service.register(db, username, password)
    return UserResponse(message="User registered successfully", username=user.username)

# API endpoint to log in an existing user
@app.post("/login", response_model=UserResponse)
async def login(username: str, password: str, db: Session = Depends(get_db)):
    user = auth_service.login(db, username, password)
    if user:
        return UserResponse(message="Login successful", username=username)
    raise HTTPException(status_code=401, detail="Invalid username or password")

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    global documents  # Use the global documents list

    try:
        # Save the uploaded file
        file_location = os.path.join(folder_path, file.filename)
        with open(file_location, "wb") as f:
            f.write(await file.read())

        # Load the data and process documents into chunks
        loader = CSVLoader(file_path=file_location)
        docs = loader.load_and_split()
        documents = [Document(page_content=chunk.page_content) for chunk in docs]

        return JSONResponse(content={"message": "File uploaded and processed successfully", "num_documents": len(documents)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing failed: {e}")

# API endpoint to interact with the chatbot
@app.post("/query/")
async def query_bot(query: str):
    global documents

    # Ensure documents are loaded
    if not documents:
        raise HTTPException(status_code=500, detail="No documents available. Please upload a file first.")

    try:
        # Initialize the chain with the current documents
        chain = initialize_chain(documents)

        # Collect response from the chain
        res = ""
        for chunk in chain.stream(query):
            res += chunk  # Append each chunk to the response

        return JSONResponse(content={"response": res})   
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot query failed: {e}")
    
@app.get("/")
async def root():
    return {"message": "Welcome! Please log in using your username and password."}
