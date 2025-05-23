import os, collections, math
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# ----------------- Yollar -----------------
TRAIN_DIR  = r"C:\Users\bilge\OneDrive\Masaüstü\ISIC2019\train"
MODEL_IN   = r"C:\Users\bilge\OneDrive\Masaüstü\model_finetuned.h5"
MODEL_OUT  = r"saved_models/model_finetuned_v2.h5"

CLASSES = ['AK','BCC','BKL','DF','MEL','NV','SCC','VASC']  # sıralama sabit

# ----------------- Model ------------------
model = tf.keras.models.load_model(MODEL_IN, compile=False)
for layer in model.layers[:-1]:
    layer.trainable = False           # sadece son Dense öğreniyor
model.layers[-1].trainable = True

model.compile(
    optimizer=tf.keras.optimizers.Adam(1e-4),
    loss="categorical_crossentropy",
    metrics=["accuracy"],
)

# ------------- Data & class_weight ----------
datagen = ImageDataGenerator(
    rescale            = 1./255,
    rotation_range     = 25,
    width_shift_range  = 0.1,
    height_shift_range = 0.1,
    horizontal_flip    = True,
    vertical_flip      = True,
    validation_split   = 0.10,     # %10 validation
)

train_gen = datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=(128,128),
    batch_size = 32,
    class_mode = "categorical",
    classes    = CLASSES,
    subset     = "training",
    shuffle    = True,
)

val_gen = datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=(128,128),
    batch_size = 32,
    class_mode = "categorical",
    classes    = CLASSES,
    subset     = "validation",
    shuffle    = False,
)

# class_weight (karekök yumuşatma + SCC/VASC boost)
counter = collections.Counter(train_gen.classes)
max_n   = max(counter.values())
cw = {i: math.sqrt(max_n/num) for i, num in counter.items()}
cw[6] *= 1.3        # SCC
cw[7] *= 1.2        # VASC
print("class_weight:", cw)

# ----------------- Callbacks -----------------
early_stop = tf.keras.callbacks.EarlyStopping(
    monitor              = "val_loss",   # val_loss izle
    patience             = 3,            # 3 epoch iyileşmezse dur
    restore_best_weights = True,
    verbose              = 1,
)

# ----------------- Fine-tune -----------------
model.fit(
    train_gen,
    epochs           = 12,          # üst sınır (erken durdurma var)
    steps_per_epoch  = len(train_gen),
    validation_data  = val_gen,
    class_weight     = cw,
    callbacks        = [early_stop],
)

os.makedirs(os.path.dirname(MODEL_OUT), exist_ok=True)
model.save(MODEL_OUT)
print("Fine-tune tamamlandı →", MODEL_OUT)
