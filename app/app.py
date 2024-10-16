from fastapi import FastAPI
from pydantic import BaseModel
from model import classify_text
import os

from database import init_db, update_or_insert_user


app = FastAPI()

init_db()

class CommentRequest(BaseModel):
    comment: str
    ip: str
    mac_address: str
    phone_number: str

@app.post("/predict")
async def predict_toxicity(request: CommentRequest):
    comment = request.comment
    ip = request.ip
    mac_address = request.mac_address
    phone_number = request.phone_number
    classification_result  = classify_text(comment)

    if classification_result:
        # Si des catégories sont au-dessus du seuil, mettre à jour la base de données
        update_or_insert_user(ip, mac_address, phone_number, classification_result)

    return {
        "text": comment,
        "toxic_reasons": [category for category in classification_result]
    }

@app.get("/")
async def root():
    return {"message": "Bienvenue dans l'API de classification de sentiment des messages"}


port = os.getenv("PORT", 8000)
print(f"Starting FastAPI on port {port}")