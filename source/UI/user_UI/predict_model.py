import cv2
import numpy as np
from tensorflow.keras.models import load_model
import tensorflow_addons as tfa

# Load the model (loaded only once)
model = load_model("saved_models/model_finetuned_v2.h5", custom_objects={
    "F1Score": tfa.metrics.F1Score
})


class_names = ["akiec", "bcc", "bkl", "df", "mel", "nv","scc", "vasc"]

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

       # Detailed lesion descriptions with more balanced language
    lesion_descriptions = {
        "nv": (
            "Melanocytic Nevus (Mole, nevus)\n"
            "What is it? A common skin marking formed by melanocyte cells.\n"
            "Appearance: Usually round, well-defined, brown or black spot.\n"
            "Medical assessment: Generally considered benign.\n"
            "Note: While most are harmless, any changing mole should be evaluated by a dermatologist "
            "as part of routine skin health monitoring."
        ),
        "mel": (
            "Melanoma\n"
            "What is it? A type of skin condition that originates from pigment-producing cells.\n"
            "Appearance: May appear asymmetrical with irregular borders and variable colors.\n"
            "Medical assessment: Requires immediate professional evaluation.\n"
            "Note: Early medical assessment is important. This AI prediction is not a diagnosis - "
            "please consult a dermatologist for proper evaluation."
        ),
        "bcc": (
            "Basal Cell Carcinoma\n"
            "What is it? A common skin condition originating from basal cells in the epidermis.\n"
            "Appearance: May appear as shiny nodules, sometimes with visible blood vessels.\n"
            "Medical assessment: Professional evaluation recommended.\n"
            "Note: This is a preliminary assessment only. A dermatologist can provide proper diagnosis "
            "and discuss appropriate treatment options if needed."
        ),
        "akiec": (
            "Actinic Keratosis / Bowen's Disease (Intraepidermal Carcinoma)\n"
            "What is it? A skin condition often associated with sun exposure.\n"
            "Appearance: Often appears as rough, reddish-brown, scaly patches.\n"
            "Medical assessment: Professional evaluation recommended.\n"
            "Note: This is a preliminary assessment. A dermatologist should examine this type of lesion "
            "to determine appropriate monitoring or treatment."
        ),
        "bkl": (
            "Benign Keratosis-Like Lesion\n"
            "What is it? Represents various types of skin growths (such as seborrheic keratosis).\n"
            "Appearance: Often appears as waxy, rough-surfaced, brown or dark marks.\n"
            "Medical assessment: Generally considered benign.\n"
            "Note: While the AI suggests this may be a benign condition, a dermatologist should confirm "
            "this assessment for peace of mind."
        ),
        "df": (
            "Dermatofibroma\n"
            "What is it? A type of skin growth that forms in the connective tissue under the skin.\n"
            "Appearance: Often appears as firm, raised, pink or brown bumps.\n"
            "Medical assessment: Generally considered benign.\n"
            "Note: This preliminary assessment suggests a common benign condition, but a dermatologist "
            "can provide a proper evaluation."
        ),
        "vasc": (
            "Vascular Lesion\n"
            "What is it? A skin marking related to blood vessels (e.g., hemangioma, port-wine stain).\n"
            "Appearance: Often appears as red, purple, or bluish spots.\n"
            "Medical assessment: Generally considered benign.\n"
            "Note: While most vascular lesions are harmless, a dermatologist can provide a proper evaluation "
            "and discuss any treatment options if desired."
        ),
        "scc": (
            "Squamous Cell Carcinoma\n"
            "What is it? A type of skin condition that affects squamous cells in the epidermis.\n"
            "Appearance: May appear as scaly patches, open sores, or wart-like growths.\n"
            "Medical assessment: Professional evaluation strongly recommended.\n"
            "Note: This is only a preliminary assessment. A dermatologist should examine this type of lesion "
            "to provide a proper diagnosis and discuss potential treatment options."
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
