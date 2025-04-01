import cv2
import numpy as np
from tensorflow.keras.models import load_model
import tensorflow_addons as tfa

# Load the model (loaded only once)
model = load_model(r"C:\Program Files\saved_models\final_global_model", custom_objects={
    "F1Score": tfa.metrics.F1Score
})

# Class labels (example: HAM10000)
class_names = ["akiec", "bcc", "bkl", "df", "mel", "nv", "vasc"]

def predict_model(image_path):
    # Load, resize, and normalize the image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Failed to load image: " + image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (128, 128))
    img = img.astype("float32") / 255.0
    img = np.expand_dims(img, axis=0)

    # Make prediction
    prediction = model.predict(img)
    predicted_index = int(np.argmax(prediction, axis=1)[0])
    # Convert confidence value to percentage
    confidence = float(np.max(prediction)) * 100  
    predicted_class = class_names[predicted_index]

    # Determine risk level based on confidence score
    if confidence < 50:
        risk_level = "Low Risk"
    elif 50 <= confidence <= 75:
        risk_level = "Medium Risk"
    else:
        risk_level = "High Risk"

    # Detailed lesion descriptions in English with additional details
    lesion_descriptions = {
        "nv": (
            "Melanocytic Nevus (Mole, nevus)\n"
            "What is it? A benign skin lesion formed by melanocyte cells.\n"
            "Appearance: Round, well-defined, brown or black spot.\n"
            "Dangerous? No.\n"
            "Cancerous? No.\n"
            "Note: The most common type of skin lesion in humans. However, some moles may transform "
            "into malignant melanoma over time and should be monitored."
        ),
        "mel": (
            "Melanoma\n"
            "What is it? An aggressive type of skin cancer that originates from melanocytes (pigment cells).\n"
            "Appearance: Asymmetrical, irregular borders, multi-colored, and growing lesion.\n"
            "Dangerous? Yes!\n"
            "Cancerous? Yes, malignant.\n"
            "Note: Early detection is critical. It is treatable in early stages but can be fatal if diagnosed late."
        ),
        "bcc": (
            "Basal Cell Carcinoma\n"
            "What is it? The most common type of skin cancer, originating from basal cells in the epidermis.\n"
            "Appearance: Shiny, pearl-like raised nodules; sometimes with visible blood vessels.\n"
            "Dangerous? Locally invasive but usually does not metastasize.\n"
            "Cancerous? Yes, malignant.\n"
            "Note: Generally not life-threatening but can grow and damage surrounding tissues if untreated."
        ),
        "akiec": (
            "Actinic Keratosis / Bowen's Disease (Intraepidermal Carcinoma)\n"
            "What is it? A precancerous or early-stage skin cancer caused by prolonged sun exposure.\n"
            "Appearance: Rough, reddish-brown, scaly lesions.\n"
            "Dangerous? Potentially dangerous.\n"
            "Cancerous? Precancerous (may evolve into cancer).\n"
            "Note: If left untreated, it may progress to squamous cell carcinoma."
        ),
        "bkl": (
            "Benign Keratosis-Like Lesion\n"
            "What is it? Represents various types of benign epidermal growths (Seborrheic keratosis, solar lentigo, lichen planus-like keratosis).\n"
            "Appearance: Waxy, rough-surfaced, brown or dark lesions.\n"
            "Dangerous? Generally not.\n"
            "Cancerous? No.\n"
            "Note: Sometimes confused with melanoma, so differential diagnosis is important."
        ),
        "df": (
            "Dermatofibroma\n"
            "What is it? A benign connective tissue tumor that forms under the skin.\n"
            "Appearance: Firm, raised, pink or brown nodules.\n"
            "Dangerous? No.\n"
            "Cancerous? No.\n"
            "Note: Usually harmless; may cause itching but typically requires no treatment."
        ),
        "vasc": (
            "Vascular Lesion\n"
            "What is it? Benign skin lesions formed from blood vessels (e.g., Hemangioma, angiokeratoma, port-wine stain).\n"
            "Appearance: Red, purple, or bluish spots resembling blood vessels.\n"
            "Dangerous? No.\n"
            "Cancerous? No.\n"
            "Note: Often congenital; sometimes treated for cosmetic reasons."
        )
    }
    lesion_description = lesion_descriptions.get(predicted_class, "Description not available.")

    # Add doctor recommendation if risk is High
    if risk_level == "High Risk":
        lesion_description += "\nIt is strongly recommended to consult a doctor immediately."

    return {
        "predicted_class": predicted_class,
        "confidence": confidence,
        "risk_level": risk_level,
        "lesion_description": lesion_description
    }
