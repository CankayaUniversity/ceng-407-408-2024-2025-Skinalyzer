import os
import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.utils import to_categorical
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras import Input
import flwr as fl
import argparse

def get_image_path(image_id, folder1, folder2):
    file1 = os.path.join(folder1, image_id + ".jpg")
    file2 = os.path.join(folder2, image_id + ".jpg")
    if os.path.exists(file1):
        return file1
    elif os.path.exists(file2):
        return file2
    else:
        return None

def load_images(df):
    images = []
    labels = []
    for _, row in df.iterrows():
        img_path = row["image_path"]
        label = row["dx"]
        if img_path is not None:
            img = load_img(img_path, target_size=(128, 128))
            img_array = img_to_array(img) / 255.0
            images.append(img_array)
            labels.append(label)
    return np.array(images), to_categorical(np.array(labels), num_classes=7)

def preprocess_ham10000(client_id=1, total_clients=3):
    metadata_path = r"C:\Users\Dell\Desktop\ham10000_dataset\HAM10000_metadata.csv"
    folder1 = r"C:\Users\Dell\Desktop\ham10000_dataset\HAM10000_images_part_1"
    folder2 = r"C:\Users\Dell\Desktop\ham10000_dataset\HAM10000_images_part_2"

    # Metadata’yı oku ve görüntü yollarını ekle
    metadata = pd.read_csv(metadata_path)
    metadata["image_path"] = metadata["image_id"].apply(lambda x: get_image_path(x, folder1, folder2))

    if metadata["image_path"].isnull().any():
        print("Eksik görüntü yolları var:")
        print(metadata[metadata["image_path"].isnull()])

    # Etiketleri sayısal hale dönüştür
    le = LabelEncoder()
    metadata["dx"] = le.fit_transform(metadata["dx"])

    # Veriyi karıştır ve client'lar arasında eşit böl
    metadata_shuffled = metadata.sample(frac=1, random_state=42).reset_index(drop=True)
    client_dfs = np.array_split(metadata_shuffled, total_clients)
    client_metadata = client_dfs[client_id]

    # Client'a ait veriyi %80 eğitim, %20 test olacak şekilde ayır
    train_metadata = client_metadata.sample(frac=0.8, random_state=42)
    test_metadata = client_metadata.drop(train_metadata.index)

    train_data, train_labels = load_images(train_metadata)
    test_data, test_labels = load_images(test_metadata)
    return (train_data, train_labels), (test_data, test_labels)

def create_client_model():
    model = Sequential([
        Input(shape=(128, 128, 3)),
        Conv2D(32, (3, 3), activation="relu"),
        MaxPooling2D(pool_size=(2, 2)),
        Dropout(0.25),
        Conv2D(32, (3, 3), activation="relu"),
        Conv2D(64, (3, 3), activation="relu"),
        MaxPooling2D(pool_size=(2, 2)),
        Dropout(0.25),
        Flatten(),
        Dense(64, activation="relu"),
        Dropout(0.5),
        Dense(32, activation="relu"),
        Dropout(0.5),
        Dense(7, activation="softmax")
    ])
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
    return model

class HAM10000Client(fl.client.NumPyClient):
    def __init__(self, model, train_data, test_data, cid):
        super().__init__()
        self.model = model
        self.train_data = train_data
        self.test_data = test_data
        self.cid = cid

    def get_parameters(self, config):
        print(f"Client {self.cid}: Parametreler gönderiliyor.")
        return self.model.get_weights()

    def fit(self, parameters, config):
        print(f"Client {self.cid}: Eğitim başlatılıyor...")
        self.model.set_weights(parameters)
        history = self.model.fit(
            self.train_data[0],
            self.train_data[1],
            epochs=50,  # EĞİTİM EPOCH SAYISI
            batch_size=16,
            verbose=1
        )
        print(f"Client {self.cid}: Eğitim tamamlandı.")
        for i, acc in enumerate(history.history["accuracy"]):
            print(f"Epoch {i+1} - accuracy: {acc:.4f}")
        return self.model.get_weights(), len(self.train_data[0]), {}

    def evaluate(self, parameters, config):
        print(f"Client {self.cid}: Değerlendirme yapılıyor...")
        self.model.set_weights(parameters)
        loss, accuracy = self.model.evaluate(self.test_data[0], self.test_data[1], verbose=0)
        print(f"Değerlendirme tamamlandı: Loss={loss:.4f}, Accuracy={accuracy:.4f}")
        return loss, len(self.test_data[0]), {"accuracy": accuracy}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-id", type=int, default=0, help="Client ID (0, 1 veya 2)")
    args = parser.parse_args()

    print("Client: Veri yükleniyor...")
    (train_data, train_labels), (test_data, test_labels) = preprocess_ham10000(client_id=args.client_id, total_clients=3)

    print("Client: Model oluşturuluyor...")
    model = create_client_model()

    print("Client: Bağlanılıyor...")
    client = HAM10000Client(model, (train_data, train_labels), (test_data, test_labels), f"Client-{args.client_id}")

    fl.client.start_numpy_client(
        server_address="192.168.1.110:8080",
        client=client
    )

    print("Client: Tüm işlem tamamlandı.")
