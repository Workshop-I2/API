import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

model_name = "unitary/toxic-bert"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

def classify_text(text: str):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits

    # applique la fonction sigmoïde pour obtenir des probas entre 0 et 1
    probabilities = torch.sigmoid(logits)
    
    # Catégories de classification du modèle
    categories = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']
    
    result = []
    for j, category in enumerate(categories):
        if probabilities[0][j] > 0.7:
            result.append(category)

    return result

