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
import traceback  # Added for detailed error reporting

# Kaçıncı turdan sonra ISIC2019'a geçilsin
THRESHOLD = 4


# HAM10000 veri seti için sınıf sayısı
HAM_CLASSES = 7

# ISIC2019 veri seti için sınıf sayısı
ISIC_CLASSES = 8

# ---------------- Veri Artırma ----------------
def augment_minority_classes(images, labels, max_augment_factor=1.0):
    class_counts = Counter(np.argmax(labels, axis=1))
    max_samples = max(class_counts.values())
    
    datagen = ImageDataGenerator(
        rotation_range=30,  # Daha fazla rotasyon
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.3,   # Artırıldı
        zoom_range=0.3,    # Artırıldı
        horizontal_flip=True,
        vertical_flip=True,  # Dikey çevirme eklendi
        fill_mode="nearest",
        brightness_range=[0.8, 1.2]  # Parlaklık değişimleri eklendi
    )
    
    augmented_images = []
    augmented_labels = []
    
    for cls, count in class_counts.items():
        if count < max_samples:
            # Sınırlandırılmış artırma - her sınıf için en fazla max_augment_factor kadar çoğalt
            target_count = min(max_samples, int(count * max_augment_factor))
            needed = target_count - count
            
            if needed <= 0:
                continue
                
            idxs = np.where(np.argmax(labels, axis=1) == cls)[0]
            
            # Rastgele seçim, tüm örnekleri kullan ancak maksimum 100 ile sınırla
            np.random.shuffle(idxs)
            subset_idxs = idxs[:min(len(idxs), 100)]  # 50'den 100'e çıkarıldı
            
            subset_x = images[subset_idxs]
            subset_y = labels[subset_idxs]
            
            flow = datagen.flow(subset_x, subset_y, batch_size=1)
            
            for _ in range(needed):
                x_batch, y_batch = next(flow)  # (1,H,W,3), (1,num_classes)
                augmented_images.append(x_batch)
                augmented_labels.append(y_batch)
    
    if augmented_images:
        aug_x = np.concatenate(augmented_images, axis=0)
        aug_y = np.concatenate(augmented_labels, axis=0)
        return aug_x, aug_y
    
    # Eğer augment yoksa boş döndür
    return np.empty((0,) + images.shape[1:], dtype=images.dtype), np.empty((0, labels.shape[1]), dtype=labels.dtype)

# ------------ HAM10000 Ön İşleme -------------
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
<<<<<<< HEAD
    meta = pd.read_csv(r"C:\Users\user\OneDrive\Masaüstü\ham10000_dataset\HAM10000_metadata.csv")
    folder1 = r"C:\Users\user\OneDrive\Masaüstü\ham10000_dataset\HAM10000_images_part_1"
    folder2 = r"C:\Users\user\OneDrive\Masaüstü\ham10000_dataset\HAM10000_images_part_2"
=======
    meta = pd.read_csv(r"C:\Users\Emrehan\Desktop\ham10000_dataset\HAM10000_metadata.csv")
    folder1 = r"C:\Users\Emrehan\Desktop\ham10000_dataset\HAM10000_images_part_1"
    folder2 = r"C:\Users\Emrehan\Desktop\ham10000_dataset\HAM10000_images_part_2"
>>>>>>> e528ab0a933671c4198cd81a5d26630c0db4e086
    meta["image_path"] = meta["image_id"].apply(lambda x: get_image_path(x, folder1, folder2))
    le = LabelEncoder()
    meta["dx"] = le.fit_transform(meta["dx"])
    df_shuf = meta.sample(frac=1, random_state=42).reset_index(drop=True)
    client_df = np.array_split(df_shuf, total_clients)[client_id]
    
    # Stratified sampling ile daha dengeli bir veri bölünmesi
    train_val = client_df.sample(frac=0.8, random_state=42)
    test_df = client_df.drop(train_val.index)
    val_df = train_val.sample(frac=0.2, random_state=42)
    train_df = train_val.drop(val_df.index)
    
    x_tr, y_tr = load_images_from_df(train_df, HAM_CLASSES)
    x_val, y_val = load_images_from_df(val_df, HAM_CLASSES)
    x_ts, y_ts = load_images_from_df(test_df, HAM_CLASSES)
    
    # Genişletilmiş augmentation uygula
    print("HAM10000 verisi için azınlık sınıflarına augmentation uygulanıyor...")
    ax, ay = augment_minority_classes(x_tr, y_tr, max_augment_factor=3.0)
    if ax.size:
        x_tr = np.concatenate([x_tr, ax], axis=0)
        y_tr = np.concatenate([y_tr, ay], axis=0)
        print(f"Augmentation sonrası veri boyutu: {x_tr.shape}")
    
    return (x_tr, y_tr), (x_val, y_val), (x_ts, y_ts)

# ------------ ISIC2019 Ön İşleme ------------
def preprocess_isic2019(client_id=0, total_clients=3):
<<<<<<< HEAD
    base = r"C:\Users\user\OneDrive\Masaüstü\ISIC2019\data"
=======
    base = r"C:\Users\Emrehan\Desktop\ISIC2019\data"
>>>>>>> e528ab0a933671c4198cd81a5d26630c0db4e086
    splits = ["train", "valid", "test"]
    dfs = {}

    # Her split için ayrı DataFrame oluştur
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

    # Label Encoder’ı yalnızca 'train' sınıfları üzerinden eğit
    le = LabelEncoder().fit(dfs["train"]["dx"].unique())

    # Split’leri client_id’ye göre böl
    data_splits = {}
    for split in splits:
        df_split = dfs[split]
        df_split["dx"] = le.transform(df_split["dx"])
        df_shuf = df_split.sample(frac=1, random_state=42).reset_index(drop=True)
        client_partition = np.array_split(df_shuf, total_clients)[client_id]
        data_splits[split] = client_partition

    # Görüntüleri yükle
    x_tr, y_tr = load_images_from_df(data_splits["train"], ISIC_CLASSES)
    x_val, y_val = load_images_from_df(data_splits["valid"], ISIC_CLASSES)
    x_ts, y_ts = load_images_from_df(data_splits["test"], ISIC_CLASSES)

    # Azınlık sınıflarına augmentasyon uygula (isterseniz isic için azaltabilirsiniz)
    print("ISIC2019 verisi için azınlık sınıflarına augmentation uygulanıyor…")
    ax, ay = augment_minority_classes(x_tr, y_tr)
    if ax.size:
        x_tr = np.concatenate([x_tr, ax], axis=0)
        y_tr = np.concatenate([y_tr, ay], axis=0)
        print(f"Augmentation sonrası ISIC2019 eğitim veri boyutu: {x_tr.shape}")

    return (x_tr, y_tr), (x_val, y_val), (x_ts, y_ts)

# --------- Model Oluşturma ---------
def create_client_model(num_classes):
    base = ResNet50(weights="imagenet", include_top=False, input_shape=(128,128,3))
    base.trainable = True
    inp = Input(shape=(128,128,3))
    x = base(inp)
    x = GlobalAveragePooling2D()(x)
    x = Dense(256, activation='relu')(x)  # 128'den 256'ya çıkarıldı
    x = Dropout(0.4)(x)  # 0.5'ten 0.4'e düşürüldü
    x = Dense(128, activation='relu')(x)  # 64'ten 128'e çıkarıldı
    x = Dropout(0.4)(x)  # 0.5'ten 0.4'e düşürüldü
    out = Dense(num_classes, activation='softmax')(x)
    model = Model(inp, out)
    model.compile(
        optimizer=Adam(1e-4), 
        loss='categorical_crossentropy', 
        metrics=['accuracy',
                tf.keras.metrics.AUC(name='auc'),  # AUC metriği eklendi
                tf.keras.metrics.Precision(name='precision'),  # Precision metriği eklendi
                tf.keras.metrics.Recall(name='recall')]  # Recall metriği eklendi
    )
    return model

# Modeli genişlet fonksiyonu - geliştirilmiş versiyonu
def expand_model_output(model, new_classes):
    """
    Modeli yeni sınıf sayısına genişletirken önceki ağırlıkları korur
    ve yeni sınıflar için daha yumuşak bir geçiş sağlar
    """
    # ÖNEMLİ FİX: Modeli genişletmeden önce orijinal ağırlıkları kaydedelim
    original_weights = model.get_weights()
    
    # Modelin mimarisini kontrol et
    print("Genişletme öncesi model katmanları:")
    for i, layer in enumerate(model.layers):
        print(f"Katman {i}: {layer.name}, Çıkış şekli: {layer.output_shape}")
    
    # Modelin son katmanını hariç bütün katmanları al
    x = model.layers[-3].output  # Son dropout katmanının çıkışı
    
    # Yeni çıkış katmanı için eski son katman ağırlıklarını al
    old_dense = model.layers[-1]
    old_weights = old_dense.get_weights()
    
    # Ağırlıkları kontrol et
    if len(old_weights) != 2:
        print(f"UYARI: Eski ağırlıklar beklenen boyutta değil: {len(old_weights)}")
        if len(old_weights) == 0:
            print("Son katman ağırlıkları boş! Önceki ağırlıkları kullanmaya çalışıyoruz.")
            # Eğer son katman ağırlıkları boşsa, orijinal model ağırlıklarını kullan
            if len(original_weights) > 0:
                old_w = original_weights[-2]
                old_b = original_weights[-1]
            else:
                # Eğer hala ağırlık bulamazsak, sıfırdan başla
                last_layer_input_dim = model.layers[-3].output_shape[-1]
                old_w = np.random.normal(0, 0.05, (last_layer_input_dim, HAM_CLASSES))
                old_b = np.zeros(HAM_CLASSES)
                print(f"Rastgele ağırlıklar oluşturuldu: {old_w.shape}, {old_b.shape}")
        else:
            # Bu durumda muhtemelen ya sadece weights ya da sadece biases var
            print("Uyumsuz ağırlık yapısı. Yeni model oluşturmaya başlıyoruz.")
            return create_client_model(new_classes)
    else:
        old_w, old_b = old_weights
    
    # Yeni çıkış katmanını oluştur
    out = Dense(new_classes, activation='softmax', name='new_dense_output')(x)
    
    # Yeni modeli oluştur
    new_model = Model(model.input, out)
    
    # Eski ağırlıkları kopyala (son katman hariç)
    for i in range(len(model.layers)-1):
        if i < len(new_model.layers):  # Eşleşen katmanlar için
            try:
                new_model.layers[i].set_weights(model.layers[i].get_weights())
            except Exception as e:
                print(f"Katman {i} ağırlıkları kopyalanamadı: {str(e)}")
    
    # Son katman ağırlıklarını genişlet
    # İlk HAM_CLASSES sınıf için eski ağırlıkları kopyala
    new_w = np.zeros((old_w.shape[0], new_classes))
    new_w[:, :HAM_CLASSES] = old_w
    
    # Yeni sınıflar için ortalama değerler ile başlat (daha iyi genelleme)
    w_mean = np.mean(old_w, axis=1, keepdims=True)
    w_std = np.std(old_w, axis=1, keepdims=True) * 0.1  # Düşük std ile başlat
    
    for i in range(HAM_CLASSES, new_classes):
        new_w[:, i] = w_mean.flatten() + np.random.randn(old_w.shape[0]) * w_std.flatten()
    
    # Yeni bias değerleri
    new_b = np.zeros(new_classes)
    new_b[:HAM_CLASSES] = old_b
    b_mean = np.mean(old_b)
    b_std = np.std(old_b) * 0.1
    new_b[HAM_CLASSES:] = b_mean + np.random.randn(new_classes - HAM_CLASSES) * b_std
    
    # Yeni ağırlıkları yükle
    try:
        # Yeni son katmanı bul
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
            # Son katmanı dizinle bul
            new_model.layers[-1].set_weights([new_w, new_b])
    except Exception as e:
        print(f"Yeni ağırlık yükleme hatası: {str(e)}")
        print("Tam hata bilgisi:")
        traceback.print_exc()
    
    # Yeni modeli derle
    new_model.compile(
        optimizer=Adam(1e-5),  # Daha düşük öğrenme oranı ile başla
        loss='categorical_crossentropy', 
        metrics=['accuracy',
                tf.keras.metrics.AUC(name='auc'),
                tf.keras.metrics.Precision(name='precision'),
                tf.keras.metrics.Recall(name='recall')]
    )
    
    print("Genişletme sonrası model katmanları:")
    for i, layer in enumerate(new_model.layers):
<<<<<<< HEAD

        print(f"Katman {i}: {layer.name}, Çıkış şekli: {layer.output_shape}")

    new_model.build(input_shape=(None, 128,128,3))
    return new_model

=======
        print(f"Katman {i}: {layer.name}, Çıkış şekli: {layer.output_shape}")
    
    return new_model

>>>>>>> e528ab0a933671c4198cd81a5d26630c0db4e086
# ------------ Federated Client ------------
class IncrementalHAMClient(fl.client.NumPyClient):
    def __init__(self, client_id=0, total_clients=3):
        self.client_id = client_id
        self.total_clients = total_clients
        self.model = create_client_model(num_classes=HAM_CLASSES)
        print(f"Client-{self.client_id}: HAM10000 verisi yükleniyor...")
        (self.x_h, self.y_h), (self.x_v, self.y_v), (self.x_t, self.y_t) = preprocess_ham10000(client_id, total_clients)
        self.isic_loaded = False
        self.model_expanded = False
        
        # Eğitim parametreleri
        self.use_early_stopping = True
<<<<<<< HEAD
        self.batch_size = 8  # 32'den 16'ya düşürüldü - daha iyi genelleme için
=======
        self.batch_size = 16  # 32'den 16'ya düşürüldü - daha iyi genelleme için
>>>>>>> e528ab0a933671c4198cd81a5d26630c0db4e086
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
        
        # Önce parametre boyutunu kontrol et
        try:
            param_model_shape = parameters[-2].shape[1]  # Output layer weights shape
            print(f"Client-{self.client_id}: Alınan parametre çıkış boyutu: {param_model_shape}")
        except Exception as e:
            print(f"Client-{self.client_id}: Parametre boyut kontrolü başarısız: {str(e)}")
            # Eğer parametre boyut kontrolü başarısız olursa varsayılan olarak HAM_CLASSES kullan
            param_model_shape = HAM_CLASSES
        
        # ISIC verisini yükle ve model genişletme
        if self.current_round >= THRESHOLD and not self.model_expanded:
            print(f"Client-{self.client_id}: ISIC entegrasyonu için THRESHOLD değeri aşıldı.")
            
            # ISIC verilerini yükle
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
            
            # Modeli genişlet
            if self.isic_loaded and not self.model_expanded:
                print(f"Client-{self.client_id}: Model genişletiliyor (7 -> 8 sınıf)...")
                try:
                    # Önce parametreleri yükle - bu kritik
                    self.model.set_weights(parameters)
                    
                    # Sonra modeli genişlet
                    self.model = expand_model_output(self.model, ISIC_CLASSES)
                    self.model_expanded = True
                    self.current_model_classes = ISIC_CLASSES
                    print(f"Client-{self.client_id}: Model genişletildi.")
                except Exception as e:
                    print(f"Client-{self.client_id}: Model genişletme hatası: {str(e)}")
                    traceback.print_exc()
        
        # Parametreleri yükleme
        try:
            # Eğer model genişletilmişse ve parametreler küçük boyutluysa
            if self.model_expanded and param_model_shape < self.current_model_classes:
                print(f"Client-{self.client_id}: Küçük -> büyük parametre uyarlaması yapılıyor: {param_model_shape} -> {self.current_model_classes}")
                
                # Parametre boyutlarını ayarla
                old_weights = [np.array(param) for param in parameters]
                
                # Son katman ağırlıklarını genişlet
                old_last_layer_weights = old_weights[-2]
                old_last_layer_bias = old_weights[-1]
                
                # Yeni ağırlıklar oluştur
                new_last_layer_weights = np.zeros((old_last_layer_weights.shape[0], ISIC_CLASSES))
                new_last_layer_weights[:, :param_model_shape] = old_last_layer_weights
                
                # Yeni sınıflar için ortalama değerlerle başlat
                w_mean = np.mean(old_last_layer_weights, axis=1, keepdims=True)
                w_std = np.std(old_last_layer_weights, axis=1, keepdims=True) * 0.1
                
                for i in range(param_model_shape, ISIC_CLASSES):
                    new_last_layer_weights[:, i] = w_mean.flatten() + np.random.randn(old_last_layer_weights.shape[0]) * w_std.flatten()
                
                # Yeni bias değerleri
                new_last_layer_bias = np.zeros((ISIC_CLASSES,))
                new_last_layer_bias[:param_model_shape] = old_last_layer_bias
                b_mean = np.mean(old_last_layer_bias)
                b_std = np.std(old_last_layer_bias) * 0.1
                new_last_layer_bias[param_model_shape:] = b_mean + np.random.randn(ISIC_CLASSES - param_model_shape) * b_std
                
                # Parametreleri güncelle
                old_weights[-2] = new_last_layer_weights
                old_weights[-1] = new_last_layer_bias
                
                # Kontrol et ve yükle
                try:
                    self.model.set_weights(old_weights)
                    print(f"Client-{self.client_id}: Genişletilmiş parametreler başarıyla yüklendi.")
                except Exception as e:
                    print(f"Client-{self.client_id}: Genişletilmiş parametre yükleme hatası: {str(e)}")
                    print("Modeli yeniden oluşturuyor...")
                    # Modeli yeniden oluştur
                    self.model = create_client_model(num_classes=ISIC_CLASSES)
                    self.current_model_classes = ISIC_CLASSES
            else:
                # Normal durumda direkt yükle
                try:
                    # Eğer modeli genişlettiysek ve parametreler 8 sınıf için geldiyse
                    if param_model_shape == self.current_model_classes:
                        print(f"Client-{self.client_id}: Parametreler doğrudan yükleniyor, boyut uyumlu: {param_model_shape}")
                        self.model.set_weights(parameters)
                    else:
                        print(f"Client-{self.client_id}: Parametre boyutu uyumsuzluğu: Model({self.current_model_classes}) != Parametre({param_model_shape})")
                        if self.model_expanded and param_model_shape > self.current_model_classes:
                            # Bu durumda modeli yeniden genişletmek gerekebilir
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

        # Eğitim için veri seçimi
        if self.model_expanded:
            # HAM ve ISIC verilerini birleştir
            x_train = np.concatenate([self.x_h, self.x_i], axis=0)
            y_train = np.concatenate([
                np.pad(self.y_h, ((0, 0), (0, ISIC_CLASSES - HAM_CLASSES))),  # HAM etiketlerini genişlet
                self.y_i  # ISIC etiketleri zaten doğru boyutta
            ], axis=0)
            
            x_val = np.concatenate([self.x_v, self.x_vi], axis=0)
            y_val = np.concatenate([
                np.pad(self.y_v, ((0, 0), (0, ISIC_CLASSES - HAM_CLASSES))),
                self.y_vi
            ], axis=0)
            
            print(f"Client-{self.client_id}: Birleştirilmiş eğitim verisi: {x_train.shape}, {y_train.shape}")
        else:
            # Sadece HAM verilerini kullan
            x_train, y_train = self.x_h, self.y_h
            x_val, y_val = self.x_v, self.y_v
            print(f"Client-{self.client_id}: HAM eğitim verisi: {x_train.shape}, {y_train.shape}")
        
        # Öğrenme oranını ayarla - ileri turlarda daha düşük öğrenme oranı
        if self.current_round > THRESHOLD + 2:
            lr *= 0.5  # İleri turlar için öğrenme oranını azalt
        
        # Model optimize edici güncelleme
        self.model.optimizer.lr = lr
        print(f"Client-{self.client_id}: Öğrenme oranı: {lr}")
        
        # Early stopping ayarları
        callbacks = []
        if self.use_early_stopping:
            callbacks.append(
                tf.keras.callbacks.EarlyStopping(
                    monitor='val_accuracy',
                    patience=5,
                    restore_best_weights=True
                )
            )
        
        # Model eğitimi
        history = self.model.fit(
            x_train, y_train,
            validation_data=(x_val, y_val),
            epochs=10,  # Maksimum epoch sayısı
            batch_size=self.batch_size,
            callbacks=callbacks,
<<<<<<< HEAD
            verbose=1,
            shuffle="batch",
=======
            verbose=1
>>>>>>> e528ab0a933671c4198cd81a5d26630c0db4e086
        )
        
        # Son validation metrikleri
        val_metrics = history.history['val_accuracy'][-1]
        
        # Test verisi ile değerlendirme
        if self.model_expanded:
            # Test verilerini birleştir
            x_test = np.concatenate([self.x_t, self.x_ti], axis=0)
            y_test = np.concatenate([
                np.pad(self.y_t, ((0, 0), (0, ISIC_CLASSES - HAM_CLASSES))),
                self.y_ti
            ], axis=0)
            
            test_loss, test_acc, test_auc, test_prec, test_rec = self.model.evaluate(x_test, y_test, verbose=0)
            print(f"Client-{self.client_id}: Test sonuçları - Acc: {test_acc:.4f}, AUC: {test_auc:.4f}, Precision: {test_prec:.4f}, Recall: {test_rec:.4f}")
        
        return self.model.get_weights(), len(x_train), {"accuracy": float(val_metrics)}

    def evaluate(self, parameters, config):
        # Parametreleri yükle
        try:
            param_model_shape = parameters[-2].shape[1]
            print(f"Client-{self.client_id}: Evaluate için parametre boyutu: {param_model_shape}")
            
            if param_model_shape != self.current_model_classes:
                print(f"Client-{self.client_id}: Evaluate için model yeniden düzenleniyor ({self.current_model_classes} -> {param_model_shape})")
                # Modeli yeniden oluştur
                self.model = create_client_model(num_classes=param_model_shape)
                self.current_model_classes = param_model_shape
            
            self.model.set_weights(parameters)
        except Exception as e:
            print(f"Client-{self.client_id}: Evaluate parametreleri yükleme hatası: {str(e)}")
            traceback.print_exc()
        
        # Doğru test verisi seçimi
        if self.model_expanded:
            # Test verilerini birleştir
            x_test = np.concatenate([self.x_t, self.x_ti], axis=0)
            y_test = np.concatenate([
                np.pad(self.y_t, ((0, 0), (0, ISIC_CLASSES - HAM_CLASSES))),
                self.y_ti
            ], axis=0)
        else:
            # Sadece HAM test verisi
            x_test, y_test = self.x_t, self.y_t
        
        # Değerlendirme
        loss, accuracy, auc, precision, recall = self.model.evaluate(x_test, y_test, verbose=0)
        return loss, len(x_test), {"accuracy": float(accuracy), "auc": float(auc), 
                                  "precision": float(precision), "recall": float(recall)}

# ------------ Ana Uygulama ------------
def main():
    parser = argparse.ArgumentParser(description="Federated Learning Client")
<<<<<<< HEAD
    parser.add_argument("--client_id", type=int, default=2, help="Client ID (0, 1, 2, ...)")
    parser.add_argument("--total_clients", type=int, default=3, help="Total number of clients")
    parser.add_argument("--server", type=str, default="25.58.175.200:8080", help="Server address")
=======
    parser.add_argument("--client_id", type=int, default=1, help="Client ID (0, 1, 2, ...)")
    parser.add_argument("--total_clients", type=int, default=3, help="Total number of clients")
    parser.add_argument("--server", type=str, default="25.58.175.200:8080", help="Server address") # localhost:8080
>>>>>>> e528ab0a933671c4198cd81a5d26630c0db4e086
    args = parser.parse_args()
    
    print(f"Client {args.client_id} başlatılıyor...")
    
    # Federated client oluştur
    fl.client.start_numpy_client(
        server_address=args.server,
        client=IncrementalHAMClient(args.client_id, args.total_clients)
    )

if __name__ == "__main__":
    # GPU bellek kullanımını sınırla
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            print(f"{len(gpus)} GPU bulundu ve bellek büyümesi sınırlandı.")
        except RuntimeError as e:
            print(f"GPU ayarlanırken hata: {str(e)}")
    
    # Uygulama başlat
    main()