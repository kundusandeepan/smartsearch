from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import faiss
import numpy as np
import requests
import redis
from sentence_transformers import SentenceTransformer
import os


# Sample diagnostic test data in JSON format
diagnostic_tests = [
    {"id": 1, "name": "Complete Blood Count (CBC)", "description": "Measures different components of blood.", "related_conditions": ["Anemia", "Infection", "Leukemia"]},
    {"id": 2, "name": "Liver Function Test", "description": "Checks liver enzyme levels and function.", "related_conditions": ["Hepatitis", "Liver Cirrhosis", "Jaundice"]},
    {"id": 3, "name": "MRI Scan", "description": "Uses magnetic fields to create detailed images of organs.", "related_conditions": ["Brain Tumor", "Stroke", "Spinal Cord Injury"]},
    {"id": 4, "name": "Electrocardiogram (ECG)", "description": "Records the electrical activity of the heart.", "related_conditions": ["Heart Attack", "Arrhythmia", "Coronary Artery Disease"]},
    {"id": 5, "name": "Blood Glucose Test", "description": "Measures blood sugar levels.", "related_conditions": ["Diabetes", "Hypoglycemia"]},
    {"id": 6, "name": "X-Ray", "description": "Uses radiation to capture images of bones and organs.", "related_conditions": ["Fractures", "Pneumonia", "Lung Cancer"]},
    {"id": 7, "name": "Thyroid Function Test", "description": "Measures thyroid hormone levels.", "related_conditions": ["Hyperthyroidism", "Hypothyroidism", "Goiter"]},
    {"id": 8, "name": "Urinalysis", "description": "Examines urine for signs of disease.", "related_conditions": ["Urinary Tract Infection", "Kidney Disease", "Diabetes"]},
    {"id": 9, "name": "CT Scan", "description": "Combines X-ray images for detailed cross-sectional views.", "related_conditions": ["Brain Hemorrhage", "Cancer", "Internal Injuries"]},
    {"id": 10, "name": "Cholesterol Test", "description": "Measures cholesterol levels in the blood.", "related_conditions": ["Heart Disease", "Stroke", "Atherosclerosis"]}
]

# Extract test descriptions for embeddings
test_descriptions = [test["description"] for test in diagnostic_tests]

# Initialize FastAPI app
app = FastAPI()

# Initialize FastAPI app
app = FastAPI()

# Enable CORS (replace "http://localhost:3000" with your frontend's URL if different)
origins = [
    "http://localhost:3000",  # Allow frontend to make requests
    "http://127.0.0.1:3000",  # You can also include other development URLs if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow only specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Load embedding model
# model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Sample test descriptions
# test_descriptions = [
#     "Liver Function Test for checking liver health.",
#     "Blood Test for diabetes diagnosis.",
#     "MRI scan for brain tumor detection."
# ]

# Convert descriptions to vectors
vectors = model.encode(test_descriptions)

# Create FAISS index
dimension = vectors.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(vectors))

# MeiliSearch setup
MEILI_HOST = os.getenv("MEILI_HOST", "http://127.0.0.1:7700")
MEILI_INDEX = "tests"

# Redis cache setup
redis_client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, decode_responses=True)

# @app.get("/search")
# def search_tests(query: str):
#     # Check cache
#     cached_result = redis_client.get(query)
#     if cached_result:
#         return {"cached_result": cached_result}

#     # Convert query to vector
#     query_vector = model.encode([query])
#     D, I = index.search(np.array(query_vector), k=3)
#     results = [test_descriptions[i] for i in I[0]]

#     # Keyword search using MeiliSearch
#     meili_response = requests.get(f"{MEILI_HOST}/indexes/{MEILI_INDEX}/search", params={"q": query}).json()
#     keyword_results = [doc["name"] for doc in meili_response.get("hits", [])]

#     # Merge results
#     final_results = list(set(results + keyword_results))

#     # Cache result
#     redis_client.set(query, str(final_results), ex=3600)

#     return {"recommendations": final_results}

@app.get("/search")
def search_tests(query: str):
    # Convert query to vector
    query_vector = model.encode([query])
    
    # Search FAISS index for nearest results
    D, I = index.search(np.array(query_vector), k=3)
    
    # Extract relevant matches
    results = [test_descriptions[i] for i in I[0] if i < len(test_descriptions)]

    # Check MeiliSearch for keyword-based results
    meili_response = requests.get(f"{MEILI_HOST}/indexes/{MEILI_INDEX}/search", params={"q": query}).json()
    keyword_results = [doc["name"] for doc in meili_response.get("hits", [])]

    # Merge FAISS & MeiliSearch results
    final_results = list(set(results + keyword_results))

    return {"recommendations": final_results}
