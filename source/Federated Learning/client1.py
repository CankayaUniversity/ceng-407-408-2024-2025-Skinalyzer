import os
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GlobalAveragePooling2D, BatchNormalization, Dropout, Dense, Input
from tensorflow.keras.preprocessing.image import load_img, img_to_array, ImageDataGenerator
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder
import flwr as fl
import argparse
from collections import Counter
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.models import Model
from tensorflow.keras.metrics import Recall


def augment_minority_classes(images, labels):
    class_counts = Counter(np.argmax(labels, axis=1))
    max_samples = max(class_counts.values())

    datagen = ImageDataGenerator(
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode="nearest"
    )

    augmented_images = []
    augmented_labels = []

    for class_label, count in class_counts.items():
        if count < max_samples:
            class_indices = np.where(np.argmax(labels, axis=1) == class_label)[0]
            samples_needed = max_samples - count
            multiplier = (samples_needed // len(class_indices)) + 1

            for idx in class_indices:
                img = images[idx].reshape((1,) + images[idx].shape)
                label = labels[idx]

                it = datagen.flow(img, batch_size=1)
                for _ in range(multiplier):
                    if len(augmented_images) >= samples_needed:
                        break
                    aug_img = next(it)[0]
                    augmented_images.append(aug_img)
                    augmented_labels.append(label)

    return np.array(augmented_images), np.array(augmented_labels)


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


def preprocess_ham10000(client_id=0, total_clients=3):
    metadata_path = r"C:\Users\Dell\Desktop\ham10000_dataset\HAM10000_metadata.csv"
    folder1 = r"C:\Users\Dell\Desktop\ham10000_dataset\HAM10000_images_part_1"
    folder2 = r"C:\Users\Dell\Desktop\ham10000_dataset\HAM10000_images_part_2"

    metadata = pd.read_csv(metadata_path)
    metadata["image_path"] = metadata["image_id"].apply(lambda x: get_image_path(x, folder1, folder2))

    if metadata["image_path"].isnull().any():
        print("Eksik görüntü yolları var:")
        print(metadata[metadata["image_path"].isnull()])

    le = LabelEncoder()
    metadata["dx"] = le.fit_transform(metadata["dx"])

    metadata_shuffled = metadata.sample(frac=1, random_state=42).reset_index(drop=True)
    client_dfs = np.array_split(metadata_shuffled, total_clients)
    client_metadata = client_dfs[client_id]

    train_val_metadata = client_metadata.sample(frac=0.8, random_state=42)
    test_metadata = client_metadata.drop(train_val_metadata.index)

    val_metadata = train_val_metadata.sample(frac=0.2, random_state=42)
    train_metadata = train_val_metadata.drop(val_metadata.index)

    train_data, train_labels = load_images(train_metadata)
    val_data, val_labels = load_images(val_metadata)
    test_data, test_labels = load_images(test_metadata)

    print("Veri artırma uygulanıyor...")

    augmented_data, augmented_labels = augment_minority_classes(train_data, train_labels)
    train_data = np.concatenate((train_data, augmented_data), axis=0)
    train_labels = np.concatenate((train_labels, augmented_labels), axis=0)

    #  Validation seti için gerçek zamanlı augmentation
    val_datagen = ImageDataGenerator(
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode="nearest"
    )

    val_generator = val_datagen.flow(val_data, val_labels, batch_size=16, shuffle=False)

    print("Yeni eğitim sınıf dağılımı:", Counter(np.argmax(train_labels, axis=1)))

    return (train_data, train_labels), (val_data, val_labels), (test_data, test_labels)


def create_client_model():
    base_model = ResNet50(weights="imagenet", include_top=False, input_shape=(128, 128, 3))

    # Tüm katmanları eğitilebilir hale getir
    base_model.trainable = True

    x = GlobalAveragePooling2D()(base_model.output)
    x = Dense(128, activation="relu")(x)
    x = Dropout(0.5)(x)
    x = Dense(64, activation="relu")(x)
    x = Dropout(0.5)(x)
    output_layer = Dense(7, activation="softmax")(x)

    model = Model(inputs=base_model.input, outputs=output_layer)

    model.compile(optimizer=Adam(learning_rate=0.0001), loss="categorical_crossentropy",
                  metrics=["accuracy"])
    return model


class HAM10000Client(fl.client.NumPyClient):
    def __init__(self, model, train_data, val_data, test_data, cid):
        self.model = model
        self.train_data = train_data
        self.val_data = val_data
        self.test_data = test_data
        self.cid = cid

    def get_parameters(self, config):
        print(f"Client {self.cid}: Parametreler gönderiliyor.")
        return self.model.get_weights()

    def fit(self, parameters, config):
        print(f"Client {self.cid}: Eğitim başlatılıyor...")
        self.model.set_weights(parameters)

        callbacks = [
            EarlyStopping(monitor="val_loss", patience=3, restore_best_weights=True),
            ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=2, verbose=1)
        ]

        history = self.model.fit(
            self.train_data[0],
            self.train_data[1],
            validation_data=self.val_data,
            epochs=20,
            batch_size=16,
            callbacks=callbacks,
            verbose=1,
        )

        print(f"Client {self.cid}: Eğitim tamamlandı.")
        for i, (rec, val_rec) in enumerate(zip(history.history["accuracy"], history.history["val_accuracy"])):
            print(f"Epoch {i + 1} - accuracy: {rec:.4f}, validation accuracy: {val_rec:.4f}")
        return self.model.get_weights(), len(self.train_data[0]), {}

    def evaluate(self, parameters, config):
        print(f"Client {self.cid}: Değerlendirme yapılıyor...")
        self.model.set_weights(parameters)
        # Modelin genel loss ve accuracy değerlerini hesaplayın
        loss, accuracy = self.model.evaluate(self.test_data[0], self.test_data[1], verbose=0)

        # Test verileri üzerinde tahminleri hesaplayın
        predictions = self.model.predict(self.test_data[0])
        y_pred = np.argmax(predictions, axis=1)
        y_true = np.argmax(self.test_data[1], axis=1)

        # Classification report oluşturun ve yazdırın
        report = classification_report(y_true, y_pred, digits=4)
        print("Classification Report:\n", report)

        print(f"Değerlendirme tamamlandı: Loss={loss:.4f}, accuracy={accuracy:.4f}")
        return loss, len(self.test_data[0]), {"accuracy": accuracy}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-id", type=int, default=1, help="Client ID (0, 1 veya 2)")
    parser.add_argument("--model", type=str, default="mobilenet",
                        help="Kullanılacak model tipi: mobilenet, densenet, resnet, vgg, inception")
    args = parser.parse_args()

    print("Client: Veri yükleniyor...")
    (train_data, train_labels), (val_data, val_labels), (test_data, test_labels) = preprocess_ham10000(
        client_id=args.client_id, total_clients=3)

    print(f"Client: {args.model} tabanlı model oluşturuluyor...")
    model = create_client_model()

    print("Client: Flower server'a bağlanılıyor...")
    client = HAM10000Client(model, (train_data, train_labels), (val_data, val_labels), (test_data, test_labels),
                            f"Client-{args.client_id}")

    fl.client.start_numpy_client(
        server_address="127.0.0.1:8080",
        client=client
    )

    print("Client: Tüm işlemler tamamlandı.")