import sys
import os

import certifi
ca = certifi.where()

from dotenv import load_dotenv
load_dotenv()
mongo_db_url = os.getenv("MONGO_DB_URL")
print(mongo_db_url)
import pymongo
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.pipeline.training_pipeline import TrainingPipeline

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, Request, Form, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse
from uvicorn import run as app_run
import secrets
from fastapi.responses import Response
from starlette.responses import RedirectResponse
import pandas as pd

from networksecurity.utils.main_utils.utils import load_object
from networksecurity.utils.ml_utils.feature_extractor import FeatureExtractor
from pydantic import BaseModel

from networksecurity.utils.ml_utils.model.estimator import NetworkModel


from networksecurity.constant.training_pipeline import DATA_INGESTION_COLLECTION_NAME
from networksecurity.constant.training_pipeline import DATA_INGESTION_DATABASE_NAME

try:
    client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)
    database = client[DATA_INGESTION_DATABASE_NAME]
    collection = database[DATA_INGESTION_COLLECTION_NAME]
    history_collection = database["prediction_history"]
    users_collection = database["users"]
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    client = None
    database = None
    collection = None
    history_collection = None
    users_collection = None

app = FastAPI()
# Secret key for session management - in production, get from .env
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "super-secret-key-123"))
app.mount("/static", StaticFiles(directory="static"), name="static")
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="./templates")


@app.get("/", tags=["authentication"])
async def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/login", tags=["authentication"])
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", tags=["authentication"])
async def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    if users_collection is None:
         return templates.TemplateResponse("login.html", {"request": request, "error": "Database error"})
         
    user = users_collection.find_one({"username": username})
    # Simple plain text check for demo purposes (In production use bcrypt)
    if not user or user["password"] != password:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    
    # Set session
    request.session["user"] = username
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/register", tags=["authentication"])
async def register(request: Request, username: str = Form(...), password: str = Form(...)):
    if users_collection is None:
         return {"error": "Database unavailable"}
         
    if users_collection.find_one({"username": username}):
        return templates.TemplateResponse("login.html", {"request": request, "error": "User already exists"})
        
    users_collection.insert_one({"username": username, "password": password})
    request.session["user"] = username
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/logout", tags=["authentication"])
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login")

@app.get("/dashboard", tags=["authentication"])
async def index(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

@app.get("/api/history")
async def get_history(request: Request):
    user = request.session.get("user")
    if not user:
        return [] # Or 401
        
    if history_collection is None:
        return []
    # Optionally filter by user if we stored it
    cursor = history_collection.find().sort("timestamp", -1).limit(10)
    history = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        history.append(doc)
    return history

@app.get("/train")
async def train_route():
    try:
        train_pipeline=TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response("Training is successful")
    except Exception as e:
        raise NetworkSecurityException(e,sys)
    
@app.post("/predict")
async def predict_route(request: Request,file: UploadFile = File(...)):
    try:
        df=pd.read_csv(file.file)
        #print(df)
        preprocesor=load_object("final_model/preprocessor.pkl")
        final_model=load_object("final_model/model.pkl")
        network_model = NetworkModel(preprocessor=preprocesor,model=final_model)
        print(df.iloc[0])
        y_pred = network_model.predict(df)
        print(y_pred)
        df['predicted_column'] = y_pred
        print(df['predicted_column'])
        #df['predicted_column'].replace(-1, 0)
        #return df.to_json()
        df.to_csv('prediction_output/output.csv')
        table_html = df.to_html(classes='table table-striped')
        
        # Save to history
        import datetime
        if history_collection is not None:
             history_collection.insert_one({
                "type": "file",
                "name": file.filename,
                "prediction": "Batch Analysis",
                "timestamp": datetime.datetime.now()
            })

        return templates.TemplateResponse("table.html", {"request": request, "table": table_html})
        
    except Exception as e:
            raise NetworkSecurityException(e,sys)

class URLRequest(BaseModel):
    url: str

# Simple in-memory cache for URL scans
url_cache = {}

@app.post("/predict_url")
async def predict_url_route(request: URLRequest):
    try:
        url = request.url
        print(f"Scanning URL: {url}")
        
        # Check Cache
        if url in url_cache:
            print(f"URL Scan Cache HIT: {url}")
            return url_cache[url]
        
        # Extract features
        extractor = FeatureExtractor()
        df = extractor.extract_features(url)
        
        # Load model and predict
        preprocesor = load_object("final_model/preprocessor.pkl")
        final_model = load_object("final_model/model.pkl")
        network_model = NetworkModel(preprocessor=preprocesor, model=final_model)
        
        # Phishing Override Check (API + Heuristics)
        phishtank_result = extractor.check_phishtank(url)
        
        if phishtank_result == -1:
            y_pred = [-1] # Confirm Phishing
            print("PhishTank Detected Phishing!")
        else:
            y_pred = network_model.predict(df)
        
        # Also check heuristics from extracted features if model says Legitimate but heuristics are suspicious
        # (This logic is partly inside FeatureExtractor but we need to respect the ML Model generally, 
        # unless API is certain. Here we trust the API override.)

        result = "Phishing" if y_pred[0] == 1 else "Legitimate" # Assuming 1 is phishing based on typical datasets, or verify labels.
        # Actually in many datasets -1 is Phishing, 1 is Legitimate. Let's check Utils or just return the raw prediction and map logic in frontend if unsure, but usually -1 is anomaly.
        # Wait, in the schema Result is int64. Let's rely on the model output. 
        # Typically Phishing websites dataset: 1=Legitimate, -1=Phishing. 
        # Let's map it safely:
        prediction_label = "Legitimate" if y_pred[0] == 1 else "Phishing"
        
        # Save to history
        import datetime
        if history_collection is not None:
            history_collection.insert_one({
                "type": "url",
                "name": url,
                "prediction": prediction_label,
                "timestamp": datetime.datetime.now()
            })

        response_payload = {"url": url, "prediction": prediction_label, "raw_result": int(y_pred[0])}
        
        # Update Cache (Max 1000 items)
        if len(url_cache) >= 1000:
            url_cache.pop(next(iter(url_cache)))
        url_cache[url] = response_payload
        
        return response_payload

    except Exception as e:
        raise NetworkSecurityException(e, sys)

# --- RAG CHATBOT INTEGRATION ---
from networksecurity.chatbot.rag_factory import rag_system
from pydantic import BaseModel
import contextlib

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        print(f"Chat Request: {request.message}")
        response = rag_system.get_response(request.message)
        print(f"Chat Response: {response}")
        return {"response": response}
    except Exception as e:
        print(f"Chat Endpoint Error: {e}")
        return {"response": f"System Error: {str(e)}"}

@app.on_event("startup")
async def startup_event():
    # Simple Ingestion: Read README.md on startup
    try:
        docs = []
        if os.path.exists("README.md"):
            with open("README.md", "r") as f:
                docs.append(f.read())
        
        # Add manual context
        docs.append("This is the SecureNet Platform. Features: URL Phishing Detection, Batch CSV Analysis, Live Threat Map.")
        docs.append("To use the platform: 1. Login. 2. Use the Dashboard to scan URLs or upload files.")
        
        rag_system.ingest_data(docs)
        print("RAG Chatbot: Knowledge Base Initialized.")
    except Exception as e:
        print(f"RAG Authorization Warning: {e}")

    
if __name__=="__main__":
    app_run(app,host="0.0.0.0",port=8000)