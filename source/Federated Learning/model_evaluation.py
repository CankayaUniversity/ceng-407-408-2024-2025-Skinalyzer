import tensorflow as tf
import tensorflow_addons as tfa
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np

# 1) Modeli yükle ve compile et
model = tf.keras.models.load_model(
    r"C:\Users\bilge\OneDrive\Masaüstü\Skinalyzer\saved_models\model_finetuned_v2.h5",
    custom_objects={"F1Score": tfa.metrics.F1Score},  # eğer F1 metriği kullandıysanız
    compile=False
)
model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# 2) Test veri generator’ünü oluştur
test_dir = r"C:\Users\bilge\OneDrive\Masaüstü\ISIC2019\train"   # kendi test klasörünüzü verin
test_datagen = ImageDataGenerator(rescale=1./255)
wanted = ["AK","BCC","BKL","DF","MEL","NV","SCC","VASC"]
test_generator = test_datagen.flow_from_directory(
    test_dir,
    target_size=(128,128),
    batch_size=32,
    class_mode="categorical",
    shuffle=False,
    classes=wanted      # sadece bu alt klasörleri kullan
)

# 3) Hızlıca evaluate() ile accuracy, loss bakabilirsiniz
loss, acc = model.evaluate(test_generator)
print(f"Test loss: {loss:.4f}   Test accuracy: {acc:.4f}")

# 4) Tüm örnekleri bir kerede tahmin et, sonra sklearn raporla
y_pred_probs = model.predict(test_generator)      # (N,8)
y_pred = np.argmax(y_pred_probs, axis=1)          # (N,)
y_true = test_generator.classes                  # Keras’ın verdiği gerçek etiket dizisi

# class_indices: {'AK':0, 'BCC':1, …} -> sınıf adlarını al
labels = list(test_generator.class_indices.keys())

print("\nClassification Report:")
print(classification_report(y_true, y_pred, target_names=labels))

print("\nConfusion Matrix:")
print(confusion_matrix(y_true, y_pred))
