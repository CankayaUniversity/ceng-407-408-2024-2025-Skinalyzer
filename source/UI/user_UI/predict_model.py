import cv2
import numpy as np
from tensorflow.keras.models import load_model
import tensorflow_addons as tfa

# Load the model (loaded only once)
model = load_model(r"C:\Users\user\Desktop\skinalyzer\saved_models\model_finetuned_v2.h5", custom_objects={
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
            "<b>Melanocytic Nevus (Mole, nevus)</b><br>"
            "<b>What is it?</b> A common skin marking formed by melanocyte cells.<br>"
            "<b>Appearance:</b> Usually round, well-defined, brown or black spot.<br>"
            "<b>Medical assessment:</b> Generally considered benign.<br>"
            "<b>Note:</b> While most are harmless, any changing mole should be evaluated by a dermatologist "
            "as part of routine skin health monitoring."
        ),
        "mel": (
            "<b>Melanoma</b><br>"
            "<b>What is it?</b> A type of skin condition that originates from pigment-producing cells.<br>"
            "<b>Appearance:</b> May appear asymmetrical with irregular borders and variable colors.<br>"
            "<b>Medical assessment:</b> Requires immediate professional evaluation.<br>"
            "<b>Note:</b> Early medical assessment is important. This AI prediction is not a diagnosis - "
            "please consult a dermatologist for proper evaluation.<br>"
        ),
        "bcc": (
            "<b>Basal Cell Carcinoma</b><br>"
            "<b>What is it?</b> A common skin condition originating from basal cells in the epidermis.<br>"
            "<b>Appearance:</b> May appear as shiny nodules, sometimes with visible blood vessels.<br>"
            "<b>Medical assessment:</b> Professional evaluation recommended.<br>"
            "<b>Note:</b> This is a preliminary assessment only. A dermatologist can provide proper diagnosis "
            "and discuss appropriate treatment options if needed.<br>"
        ),
        "akiec": (
            "<b>Actinic Keratosis / Bowen's Disease (Intraepidermal Carcinoma)</b><br>"
            "<b>What is it?</b> A skin condition often associated with sun exposure.<br>"
            "<b>Appearance:</b> Often appears as rough, reddish-brown, scaly patches.<br>"
            "<b>Medical assessment:</b> Professional evaluation recommended.<br>"
            "<b>Note:</b> This is a preliminary assessment. A dermatologist should examine this type of lesion "
            "to determine appropriate monitoring or treatment.<br>"
        ),
        "bkl": (
            "<b>Benign Keratosis-Like Lesion</b><br>"
            "<b>What is it?</b> Represents various types of skin growths (such as seborrheic keratosis).<br>"
            "<b>Appearance:</b> Often appears as waxy, rough-surfaced, brown or dark marks.<br>"
            "<b>Medical assessment:</b> Generally considered benign.<br>"
            "<b>Note:</b> While the AI suggests this may be a benign condition, a dermatologist should confirm "
            "this assessment for peace of mind."
        ),
        "df": (
            "<b>Dermatofibroma</b><br>"
            "<b>What is it?</b> A type of skin growth that forms in the connective tissue under the skin.<br>"
            "<b>Appearance:</b> Often appears as firm, raised, pink or brown bumps.<br>"
            "<b>Medical assessment:</b> Generally considered benign.<br>"
            "<b>Note:</b> This preliminary assessment suggests a common benign condition, but a dermatologist "
            "can provide a proper evaluation."
        ),
        "vasc": (
            "<b>Vascular Lesion</b><br>"
            "<b>What is it?</b> A skin marking related to blood vessels (e.g., hemangioma, port-wine stain).<br>"
            "<b>Appearance:</b> Often appears as red, purple, or bluish spots.<br>"
            "<b>Medical assessment:</b> Generally considered benign.<br>"
            "<b>Note:</b> While most vascular lesions are harmless, a dermatologist can provide a proper evaluation "
            "and discuss any treatment options if desired."
        ),
        "scc": (
            "<b>Squamous Cell Carcinoma</b><br>"
            "<b>What is it?</b> A type of skin condition that affects squamous cells in the epidermis.<br>"
            "<b>Appearance:</b> May appear as scaly patches, open sores, or wart-like growths.<br>"
            "<b>Medical assessment:</b> Professional evaluation strongly recommended.<br>"
            "<b>Note:</b> This is only a preliminary assessment. A dermatologist should examine this type of lesion "
            "to provide a proper diagnosis and discuss potential treatment options.<br>"
        )
    }

    lesion_description = lesion_descriptions.get(predicted_class, "Description not available.")


    if risk_level == "High Risk":
        lesion_description += "<br><span style='color:red;'>It is strongly recommended to consult a doctor immediately.</span>"


    return {
        "predicted_class": predicted_class,
        "confidence": confidence,
        "risk_level": risk_level,
        "lesion_description": lesion_description
    }
