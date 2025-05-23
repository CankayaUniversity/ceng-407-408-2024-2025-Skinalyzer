import os
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout, Input
from tensorflow.keras.preprocessing.image import load_img, img_to_array, ImageDataGenerator
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.applications import ResNet50
from sklearn.preprocessing import LabelEncoder
from collections import Counter
import flwr as fl
import argparse
import traceback  


THRESHOLD = 4
HAM_CLASSES = 7
ISIC_CLASSES = 8


def augment_minority_classes(images, labels, max_augment_factor=1.0):
    class_counts = Counter(np.argmax(labels, axis=1))
    max_samples = max(class_counts.values())
    
    datagen = ImageDataGenerator(
        rotation_range=30, 
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.3,   
        zoom_range=0.3,   
        horizontal_flip=True,
        vertical_flip=True,  
        fill_mode="nearest",
        brightness_range=[0.8, 1.2]  
    )
    
    augmented_images = []
    augmented_labels = []
    
    for cls, count in class_counts.items():
        if count < max_samples:
            target_count = min(max_samples, int(count * max_augment_factor))
            needed = target_count - count
            
            if needed <= 0:
                continue
                
            idxs = np.where(np.argmax(labels, axis=1) == cls)[0]
            np.random.shuffle(idxs)
            subset_idxs = idxs[:min(len(idxs), 100)]  
            
            subset_x = images[subset_idxs]
            subset_y = labels[subset_idxs]
            
            flow = datagen.flow(subset_x, subset_y, batch_size=1)
            
            for _ in range(needed):
                x_batch, y_batch = next(flow) 
                augmented_images.append(x_batch)
                augmented_labels.append(y_batch)
    
    if augmented_images:
        aug_x = np.concatenate(augmented_images, axis=0)
        aug_y = np.concatenate(augmented_labels, axis=0)
        return aug_x, aug_y
    

    return np.empty((0,) + images.shape[1:], dtype=images.dtype), np.empty((0, labels.shape[1]), dtype=labels.dtype)


def get_image_path(image_id, folder1, folder2):
    p1 = os.path.join(folder1, image_id + ".jpg")
    p2 = os.path.join(folder2, image_id + ".jpg")
    return p1 if os.path.exists(p1) else (p2 if os.path.exists(p2) else None)

def load_images_from_df(df, num_classes):
    imgs, labels = [], []
    for _, r in df.iterrows():
        path = r.get("image_path")
        if isinstance(path, str) and os.path.exists(path):
            img = load_img(path, target_size=(128,128))
            imgs.append(img_to_array(img) / 255.0)
            labels.append(r["dx"])
    return np.array(imgs), to_categorical(labels, num_classes=num_classes)

def preprocess_ham10000(client_id=0, total_clients=3):
    meta = pd.read_csv(r"C:\Users\Emrehan\Desktop\ham10000_dataset\HAM10000_metadata.csv")
    folder1 = r"C:\Users\Emrehan\Desktop\ham10000_dataset\HAM10000_images_part_1"
    folder2 = r"C:\Users\Emrehan\Desktop\ham10000_dataset\HAM10000_images_part_2"
    meta["image_path"] = meta["image_id"].apply(lambda x: get_image_path(x, folder1, folder2))
    le = LabelEncoder()
    meta["dx"] = le.fit_transform(meta["dx"])
    df_shuf = meta.sample(frac=1, random_state=42).reset_index(drop=True)
    client_df = np.array_split(df_shuf, total_clients)[client_id]
    
   
    train_val = client_df.sample(frac=0.8, random_state=42)
    test_df = client_df.drop(train_val.index)
    val_df = train_val.sample(frac=0.2, random_state=42)
    train_df = train_val.drop(val_df.index)
    
    x_tr, y_tr = load_images_from_df(train_df, HAM_CLASSES)
    x_val, y_val = load_images_from_df(val_df, HAM_CLASSES)
    x_ts, y_ts = load_images_from_df(test_df, HAM_CLASSES)
    
   
    print("HAM10000 verisi için azınlık sınıflarına augmentation uygulanıyor...")
    ax, ay = augment_minority_classes(x_tr, y_tr, max_augment_factor=3.0)
    if ax.size:
        x_tr = np.concatenate([x_tr, ax], axis=0)
        y_tr = np.concatenate([y_tr, ay], axis=0)
        print(f"Augmentation sonrası veri boyutu: {x_tr.shape}")
    
    return (x_tr, y_tr), (x_val, y_val), (x_ts, y_ts)


def preprocess_isic2019(client_id=0, total_clients=3):
    base = r"C:\Users\Emrehan\Desktop\ISIC2019\data"
    splits = ["train", "valid", "test"]
    dfs = {}

  
    for split in splits:
        records = []
        split_dir = os.path.join(base, split)
        if not os.path.isdir(split_dir):
            raise ValueError(f"ISIC2019 '{split}' dizini bulunamadı: {split_dir}")
        for cls in os.listdir(split_dir):
            cls_dir = os.path.join(split_dir, cls)
            if os.path.isdir(cls_dir):
                for fname in os.listdir(cls_dir):
                    if fname.lower().endswith(('.jpg', '.png')):
                        records.append({
                            "image_path": os.path.join(cls_dir, fname),
                            "dx": cls.lower()  # Küçük harf
                        })
        dfs[split] = pd.DataFrame(records)

  
    le = LabelEncoder().fit(dfs["train"]["dx"].unique())

    # Split’leri client_id’ye göre böl
    data_splits = {}
    for split in splits:
        df_split = dfs[split]
        df_split["dx"] = le.transform(df_split["dx"])
        df_shuf = df_split.sample(frac=1, random_state=42).reset_index(drop=True)
        client_partition = np.array_split(df_shuf, total_clients)[client_id]
        data_splits[split] = client_partition

 
    x_tr, y_tr = load_images_from_df(data_splits["train"], ISIC_CLASSES)
    x_val, y_val = load_images_from_df(data_splits["valid"], ISIC_CLASSES)
    x_ts, y_ts = load_images_from_df(data_splits["test"], ISIC_CLASSES)


    print("ISIC2019 verisi için azınlık sınıflarına augmentation uygulanıyor…")
    ax, ay = augment_minority_classes(x_tr, y_tr)
    if ax.size:
        x_tr = np.concatenate([x_tr, ax], axis=0)
        y_tr = np.concatenate([y_tr, ay], axis=0)
        print(f"Augmentation sonrası ISIC2019 eğitim veri boyutu: {x_tr.shape}")

    return (x_tr, y_tr), (x_val, y_val), (x_ts, y_ts)


def create_client_model(num_classes):
    base = ResNet50(weights="imagenet", include_top=False, input_shape=(128,128,3))
    base.trainable = True
    inp = Input(shape=(128,128,3))
    x = base(inp)
    x = GlobalAveragePooling2D()(x)
    x = Dense(256, activation='relu')(x) 
    x = Dropout(0.4)(x)  
    x = Dense(128, activation='relu')(x)  
    x = Dropout(0.4)(x)  
    out = Dense(num_classes, activation='softmax')(x)
    model = Model(inp, out)
    model.compile(
        optimizer=Adam(1e-4), 
        loss='categorical_crossentropy', 
        metrics=['accuracy',
                tf.keras.metrics.AUC(name='auc'),  
                tf.keras.metrics.Precision(name='precision'),  
                tf.keras.metrics.Recall(name='recall')] 
    )
    return model


def expand_model_output(model, new_classes):
    original_weights = model.get_weights()
    
    print("Genişletme öncesi model katmanları:")
    for i, layer in enumerate(model.layers):
        print(f"Katman {i}: {layer.name}, Çıkış şekli: {layer.output_shape}")
    
    x = model.layers[-3].output  
    
  
    old_dense = model.layers[-1]
    old_weights = old_dense.get_weights()
    
 
    if len(old_weights) != 2:
        print(f"UYARI: Eski ağırlıklar beklenen boyutta değil: {len(old_weights)}")
        if len(old_weights) == 0:
            print("Son katman ağırlıkları boş! Önceki ağırlıkları kullanmaya çalışıyoruz.")
            if len(original_weights) > 0:
                old_w = original_weights[-2]
                old_b = original_weights[-1]
            else:
                last_layer_input_dim = model.layers[-3].output_shape[-1]
                old_w = np.random.normal(0, 0.05, (last_layer_input_dim, HAM_CLASSES))
                old_b = np.zeros(HAM_CLASSES)
                print(f"Rastgele ağırlıklar oluşturuldu: {old_w.shape}, {old_b.shape}")
        else:
            print("Uyumsuz ağırlık yapısı. Yeni model oluşturmaya başlıyoruz.")
            return create_client_model(new_classes)
    else:
        old_w, old_b = old_weights
    
    out = Dense(new_classes, activation='softmax', name='new_dense_output')(x)
    new_model = Model(model.input, out)
    
  
    for i in range(len(model.layers)-1):
        if i < len(new_model.layers): 
            try:
                new_model.layers[i].set_weights(model.layers[i].get_weights())
            except Exception as e:
                print(f"Katman {i} ağırlıkları kopyalanamadı: {str(e)}")
    
 
    new_w = np.zeros((old_w.shape[0], new_classes))
    new_w[:, :HAM_CLASSES] = old_w
    
  
    w_mean = np.mean(old_w, axis=1, keepdims=True)
    w_std = np.std(old_w, axis=1, keepdims=True) * 0.1  
    
    for i in range(HAM_CLASSES, new_classes):
        new_w[:, i] = w_mean.flatten() + np.random.randn(old_w.shape[0]) * w_std.flatten()
    
  
    new_b = np.zeros(new_classes)
    new_b[:HAM_CLASSES] = old_b
    b_mean = np.mean(old_b)
    b_std = np.std(old_b) * 0.1
    new_b[HAM_CLASSES:] = b_mean + np.random.randn(new_classes - HAM_CLASSES) * b_std
    
  
    try:
        output_layer = None
        for layer in new_model.layers:
            if layer.name == 'new_dense_output':
                output_layer = layer
                break
        
        if output_layer is not None:
            print(f"Yeni son katman bulundu: {output_layer.name}, ağırlık boyutları: {new_w.shape}, {new_b.shape}")
            output_layer.set_weights([new_w, new_b])
        else:
            print("Yeni son katman bulunamadı! Alternatif yöntem deneniyor...")
            new_model.layers[-1].set_weights([new_w, new_b])
    except Exception as e:
        print(f"Yeni ağırlık yükleme hatası: {str(e)}")
        print("Tam hata bilgisi:")
        traceback.print_exc()
    
    new_model.compile(
        optimizer=Adam(1e-5),  
        loss='categorical_crossentropy', 
        metrics=['accuracy',
                tf.keras.metrics.AUC(name='auc'),
                tf.keras.metrics.Precision(name='precision'),
                tf.keras.metrics.Recall(name='recall')]
    )
    
    print("Genişletme sonrası model katmanları:")
    for i, layer in enumerate(new_model.layers):
        print(f"Katman {i}: {layer.name}, Çıkış şekli: {layer.output_shape}")
    
    return new_model


class IncrementalHAMClient(fl.client.NumPyClient):
    def __init__(self, client_id=0, total_clients=3):
        self.client_id = client_id
        self.total_clients = total_clients
        self.model = create_client_model(num_classes=HAM_CLASSES)
        print(f"Client-{self.client_id}: HAM10000 verisi yükleniyor...")
        (self.x_h, self.y_h), (self.x_v, self.y_v), (self.x_t, self.y_t) = preprocess_ham10000(client_id, total_clients)
        self.isic_loaded = False
        self.model_expanded = False
        
      
        self.use_early_stopping = True
        self.batch_size = 16  
        self.current_round = 0
        
        # Model boyutu takibi
        self.current_model_classes = HAM_CLASSES

    def get_parameters(self, config):
        print(f"Client-{self.client_id}: Parametreler gönderiliyor. Model sınıf sayısı: {self.current_model_classes}")
        model_weights = self.model.get_weights()
        if not model_weights:
            print(f"UYARI: Client-{self.client_id}: Model ağırlıkları boş!")
        return model_weights

    def fit(self, parameters, config):
        self.current_round = config.get("round", 1)
        lr = config.get("base_lr", 1e-4)
        
        print(f"Client-{self.client_id}: Round {self.current_round} başlıyor.")
        
       
        try:
            param_model_shape = parameters[-2].shape[1]  # Output layer weights shape
            print(f"Client-{self.client_id}: Alınan parametre çıkış boyutu: {param_model_shape}")
        except Exception as e:
            print(f"Client-{self.client_id}: Parametre boyut kontrolü başarısız: {str(e)}")
            param_model_shape = HAM_CLASSES
        
        if self.current_round > THRESHOLD and not self.model_expanded:
            print(f"Client-{self.client_id}: ISIC entegrasyonu için THRESHOLD değeri aşıldı.")
            
            if not self.isic_loaded:
                print(f"Client-{self.client_id}: ISIC verisi yükleniyor...")
                try:
                    (self.x_i, self.y_i), (self.x_vi, self.y_vi), (self.x_ti, self.y_ti) = preprocess_isic2019(
                        self.client_id, self.total_clients
                    )
                    self.isic_loaded = True
                    print(f"Client-{self.client_id}: ISIC verisi yüklendi.")
                except Exception as e:
                    print(f"Client-{self.client_id} ISIC veri yükleme hatası: {str(e)}")
                    traceback.print_exc()
            
            if self.isic_loaded and not self.model_expanded:
                print(f"Client-{self.client_id}: Model genişletiliyor (7 -> 8 sınıf)...")
                try:
                    self.model.set_weights(parameters)
                    self.model = expand_model_output(self.model, ISIC_CLASSES)
                    self.model_expanded = True
                    self.current_model_classes = ISIC_CLASSES
                    print(f"Client-{self.client_id}: Model genişletildi.")
                except Exception as e:
                    print(f"Client-{self.client_id}: Model genişletme hatası: {str(e)}")
                    traceback.print_exc()
        
      
        try:
            if self.model_expanded and param_model_shape < self.current_model_classes:
                print(f"Client-{self.client_id}: Küçük -> büyük parametre uyarlaması yapılıyor: {param_model_shape} -> {self.current_model_classes}")
                
                old_weights = [np.array(param) for param in parameters]
                old_last_layer_weights = old_weights[-2]
                old_last_layer_bias = old_weights[-1]
                
              
                new_last_layer_weights = np.zeros((old_last_layer_weights.shape[0], ISIC_CLASSES))
                new_last_layer_weights[:, :param_model_shape] = old_last_layer_weights
                
               
                w_mean = np.mean(old_last_layer_weights, axis=1, keepdims=True)
                w_std = np.std(old_last_layer_weights, axis=1, keepdims=True) * 0.1
                
                for i in range(param_model_shape, ISIC_CLASSES):
                    new_last_layer_weights[:, i] = w_mean.flatten() + np.random.randn(old_last_layer_weights.shape[0]) * w_std.flatten()
                
            
                new_last_layer_bias = np.zeros((ISIC_CLASSES,))
                new_last_layer_bias[:param_model_shape] = old_last_layer_bias
                b_mean = np.mean(old_last_layer_bias)
                b_std = np.std(old_last_layer_bias) * 0.1
                new_last_layer_bias[param_model_shape:] = b_mean + np.random.randn(ISIC_CLASSES - param_model_shape) * b_std
                
           
                old_weights[-2] = new_last_layer_weights
                old_weights[-1] = new_last_layer_bias
                
                
                try:
                    self.model.set_weights(old_weights)
                    print(f"Client-{self.client_id}: Genişletilmiş parametreler başarıyla yüklendi.")
                except Exception as e:
                    print(f"Client-{self.client_id}: Genişletilmiş parametre yükleme hatası: {str(e)}")
                    print("Modeli yeniden oluşturuyor...")
                    self.model = create_client_model(num_classes=ISIC_CLASSES)
                    self.current_model_classes = ISIC_CLASSES
            else:
                try:
                    if param_model_shape == self.current_model_classes:
                        print(f"Client-{self.client_id}: Parametreler doğrudan yükleniyor, boyut uyumlu: {param_model_shape}")
                        self.model.set_weights(parameters)
                    else:
                        print(f"Client-{self.client_id}: Parametre boyutu uyumsuzluğu: Model({self.current_model_classes}) != Parametre({param_model_shape})")
                        if self.model_expanded and param_model_shape > self.current_model_classes:
                            print(f"Client-{self.client_id}: Model yeniden oluşturuluyor...")
                            self.model = create_client_model(num_classes=param_model_shape)
                            self.current_model_classes = param_model_shape
                            self.model.set_weights(parameters)
                except Exception as e:
                    print(f"Client-{self.client_id}: Parametre yükleme hatası: {str(e)}")
                    traceback.print_exc()
        except Exception as e:
            print(f"Client-{self.client_id}: Genel parametre yükleme hatası: {str(e)}")
            traceback.print_exc()

       
        if self.model_expanded:
            x_train = np.concatenate([self.x_h, self.x_i], axis=0)
            padded_y_h = np.zeros((self.y_h.shape[0], ISIC_CLASSES))
            padded_y_h[:, :HAM_CLASSES] = self.y_h
            y_train = np.concatenate([padded_y_h, self.y_i], axis=0)
            x_val = np.concatenate([self.x_v, self.x_vi], axis=0)
            y_val = np.concatenate([
                np.pad(self.y_v, ((0, 0), (0, ISIC_CLASSES - HAM_CLASSES))),
                self.y_vi
            ], axis=0)
            
            print(f"Client-{self.client_id}: Birleştirilmiş eğitim verisi: {x_train.shape}, {y_train.shape}")
        else:
            x_train, y_train = self.x_h, self.y_h
            x_val, y_val = self.x_v, self.y_v
            print(f"Client-{self.client_id}: HAM eğitim verisi: {x_train.shape}, {y_train.shape}")
        
        if self.current_round > THRESHOLD + 2:
            lr *= 0.5  
        
        self.model.optimizer.lr = lr
        print(f"Client-{self.client_id}: Öğrenme oranı: {lr}")
        
      
        callbacks = []
        if self.use_early_stopping:
            callbacks.append(
                tf.keras.callbacks.EarlyStopping(
                    monitor='val_accuracy',
                    patience=5,
                    restore_best_weights=True
                )
            )
        
  
        history = self.model.fit(
            x_train, y_train,
            validation_data=(x_val, y_val),
            epochs=10, 
            batch_size=self.batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
       
        val_metrics = history.history['val_accuracy'][-1]
       
        if self.model_expanded:
            x_test = np.concatenate([self.x_t, self.x_ti], axis=0)
            y_test = np.concatenate([
                np.pad(self.y_t, ((0, 0), (0, ISIC_CLASSES - HAM_CLASSES))),
                self.y_ti
            ], axis=0)
            
            test_loss, test_acc, test_auc, test_prec, test_rec = self.model.evaluate(x_test, y_test, verbose=0)
            print(f"Client-{self.client_id}: Test sonuçları - Acc: {test_acc:.4f}, AUC: {test_auc:.4f}, Precision: {test_prec:.4f}, Recall: {test_rec:.4f}")
        
        return self.model.get_weights(), len(x_train), {"accuracy": float(val_metrics)}

    def evaluate(self, parameters, config):
        try:
            param_model_shape = parameters[-2].shape[1]
            print(f"Client-{self.client_id}: Evaluate için parametre boyutu: {param_model_shape}")
            
            if param_model_shape != self.current_model_classes:
                print(f"Client-{self.client_id}: Evaluate için model yeniden düzenleniyor ({self.current_model_classes} -> {param_model_shape})")
                self.model = create_client_model(num_classes=param_model_shape)
                self.current_model_classes = param_model_shape
            
            self.model.set_weights(parameters)
        except Exception as e:
            print(f"Client-{self.client_id}: Evaluate parametreleri yükleme hatası: {str(e)}")
            traceback.print_exc()
        
      
        if self.model_expanded:
        
            x_test = np.concatenate([self.x_t, self.x_ti], axis=0)
            padded_y_t = np.zeros((self.y_t.shape[0], ISIC_CLASSES))
            padded_y_t[:, :HAM_CLASSES] = self.y_t
            y_test = np.concatenate([padded_y_t, self.y_ti], axis=0)
        else:
            x_test, y_test = self.x_t, self.y_t
        
        # Evaluation
        loss, accuracy, auc, precision, recall = self.model.evaluate(x_test, y_test, verbose=0)
        return loss, len(x_test), {"accuracy": float(accuracy), "auc": float(auc), 
                                  "precision": float(precision), "recall": float(recall)}


def main():
    parser = argparse.ArgumentParser(description="Federated Learning Client")
    parser.add_argument("--client_id", type=int, default=1, help="Client ID (0, 1, 2, ...)")
    parser.add_argument("--total_clients", type=int, default=3, help="Total number of clients")
    parser.add_argument("--server", type=str, default="25.58.175.200:8080", help="Server address") # localhost:8080
    args = parser.parse_args()
    
    print(f"Client {args.client_id} başlatılıyor...")
    
  
    fl.client.start_numpy_client(
        server_address=args.server,
        client=IncrementalHAMClient(args.client_id, args.total_clients)
    )

if __name__ == "__main__":
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            print(f"{len(gpus)} GPU bulundu ve bellek büyümesi sınırlandı.")
        except RuntimeError as e:
            print(f"GPU ayarlanırken hata: {str(e)}")
    
    main()