from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf
import numpy as np
from PIL import Image
import io

app=FastAPI(
    title="Fish Disease Classification API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # if frontend added later localhost link should be written here instead of *.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CLASS_NAMES = [
    "Black Sea Sprat",
    "Gilt-Head Bream",
    "Hourse Mackerel",
    "Red Mullet",
    "Red Sea Bream",
    "Sea Bass",
    "Shrimp",
    "Striped Red Mullet",
    "Trout"
]
IMAGE_SIZE=(256,256)
MODEL_PATH="fish_species_model.keras"

model=tf.keras.models.load_model('fish_species_model.keras')

def preprocess_image(image_bytes):
    """Gelen byte verisini PIL Image'e çevirip modelin beklediği formata getirir."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize(IMAGE_SIZE)
    img_array = np.array(img) / 255.0  # Normalizasyon
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

@app.get("/")
def read_root():
    return {"message": "Welcome to Fish Species Classification API."}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        
        input_data = preprocess_image(image_bytes)
        
        predictions = model.predict(input_data, verbose=0)
        predicted_class_idx = np.argmax(predictions[0])
        predicted_class_name = CLASS_NAMES[predicted_class_idx]
        confidence = float(predictions[0][predicted_class_idx])
        
        all_probabilities = {
            name: float(prob) for name, prob in zip(CLASS_NAMES, predictions[0])
        }
        
        return {
            "success": True,
            "filename": file.filename,
            "prediction": predicted_class_name,
            "confidence": round(confidence * 100, 2),
            "all_predictions": all_probabilities
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)