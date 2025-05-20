import flwr as fl
from flwr.server import start_server
from flwr.server.strategy import FedAvg
from flwr.common import parameters_to_ndarrays, ndarrays_to_parameters
import numpy as np
import tensorflow as tf
import tensorflow_addons as tfa
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.models import Model
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout, Input
from tensorflow.keras.optimizers import Adam
import os


def create_initial_model(num_classes: int = 7):
    base = ResNet50(weights="imagenet", include_top=False, input_shape=(128,128,3))
    base.trainable = True
    x = GlobalAveragePooling2D()(base.output)
    x = Dense(256, activation="relu")(x)
    x = Dropout(0.4)(x)
    x = Dense(128, activation="relu")(x)
    x = Dropout(0.4)(x)
    out = Dense(num_classes, activation="softmax")(x)
    model = Model(inputs=base.input, outputs=out)
    model.compile(
        optimizer=Adam(learning_rate=1e-4),
        loss="categorical_crossentropy",
        metrics=[
            tf.keras.metrics.CategoricalAccuracy(name="accuracy"),
            tf.keras.metrics.AUC(name="auc"),
            tf.keras.metrics.Precision(name="precision"),
            tf.keras.metrics.Recall(name="recall"),
            tfa.metrics.F1Score(num_classes=num_classes, average="macro", name="f1_score"),
        ],
    )
    return model



def expand_model(model, new_classes=8):
    print(f"Genişletiliyor: {model.layers[-1].output_shape[-1]} -> {new_classes}")
    base = ResNet50(weights="imagenet", include_top=False, input_shape=(128,128,3))
    base.trainable = True
    inp = Input(shape=(128,128,3))
    x = base(inp)
    x = GlobalAveragePooling2D()(x)
    x = Dense(256, activation='relu')(x)
    x = Dropout(0.4)(x)
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.4)(x)
    out = Dense(new_classes, activation='softmax')(x)
    new_model = Model(inp, out)
    new_model.compile(
        optimizer=Adam(learning_rate=5e-5),
        loss="categorical_crossentropy",
        metrics=[
            tf.keras.metrics.CategoricalAccuracy(name="accuracy"),
            tf.keras.metrics.AUC(name="auc"),
            tf.keras.metrics.Precision(name="precision"),
            tf.keras.metrics.Recall(name="recall"),
            tfa.metrics.F1Score(num_classes=new_classes, average="macro", name="f1_score"),
        ],
    )
    

    for i in range(len(model.layers)-1):
        if i < len(new_model.layers):
            if model.layers[i].name == new_model.layers[i].name:
                try:
                    new_model.layers[i].set_weights(model.layers[i].get_weights())
                except Exception as e:
                    print(f"Katman {i} ağırlıkları kopyalanamadı: {str(e)}")
    

    old_dense = model.layers[-1]
    old_weights = old_dense.get_weights()
    old_w, old_b = old_weights
    
  
    new_w = np.zeros((old_w.shape[0], new_classes))
    new_w[:, :old_w.shape[1]] = old_w
    
 
    w_mean = np.mean(old_w, axis=1, keepdims=True)
    w_std = np.std(old_w, axis=1, keepdims=True) * 0.1
    
    for i in range(old_w.shape[1], new_classes):
        new_w[:, i] = w_mean.flatten() + np.random.randn(old_w.shape[0]) * w_std.flatten()
    
  
    new_b = np.zeros(new_classes)
    new_b[:old_b.shape[0]] = old_b
    b_mean = np.mean(old_b)
    b_std = np.std(old_b) * 0.1
    new_b[old_b.shape[0]:] = b_mean + np.random.randn(new_classes - old_b.shape[0]) * b_std
    
  
    new_model.layers[-1].set_weights([new_w, new_b])
    
    return new_model


THRESHOLD = 4
INCREMENT_ROUND = THRESHOLD + 1
HAM_CLASSES = 7
ISIC_CLASSES = 8

def on_fit_config(server_round: int):
    lr = 1e-4 if server_round < THRESHOLD else 5e-5
    return {"round": server_round, "base_lr": lr}

def on_evaluate_config(server_round: int):
    return {"round": server_round}

def aggregate_evaluate_metrics(metrics_list):
    accuracies, aucs, precisions, recalls, f1_scores = [], [], [], [], []
    for _, metrics in metrics_list:
        accuracies.append(metrics.get("accuracy", 0.0))
        aucs.append(metrics.get("auc", 0.0))
        precisions.append(metrics.get("precision", 0.0))
        recalls.append(metrics.get("recall", 0.0))
        f1_scores.append(metrics.get("f1_score", 0.0))

    print(f"\n--- Global Evaluation ---")
    print(f"Accuracy: {np.mean(accuracies):.4f} | AUC: {np.mean(aucs):.4f} | Precision: {np.mean(precisions):.4f} | Recall: {np.mean(recalls):.4f} | F1-Score: {np.mean(f1_scores):.4f}\n")

    return {
        "accuracy": float(np.mean(accuracies)),
        "auc": float(np.mean(aucs)),
        "precision": float(np.mean(precisions)),
        "recall": float(np.mean(recalls)),
        "f1_score": float(np.mean(f1_scores)),
    }


def save_model(parameters, round_num):
    try:
        weights = parameters_to_ndarrays(parameters)
        if not weights:
            raise ValueError(f"⚠️ Round {round_num}: weights boş geldi, model kaydedilemiyor.")
        
        
        output_dim = weights[-2].shape[1]
        print(f"Round {round_num}: Model çıkış boyutu: {output_dim}")
        
       
        model = create_initial_model(num_classes=output_dim)
        model.set_weights(weights)
        
        
        os.makedirs("saved_models", exist_ok=True)
        path = os.path.join("saved_models", f"global_incremental_fl_model_r{round_num}.h5")
        
        model.save(path)
        print(f"✅ Round {round_num}: Model başarıyla kaydedildi: {path}")
        return True
    except Exception as e:
        print(f"❌ Round {round_num}: Model kaydedilemedi: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


class CustomFedAvg(FedAvg):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.latest_parameters = None
        self.current_model_classes = HAM_CLASSES
    
    def aggregate_fit(self, server_round, results, failures):
        print(f"\n🔄 Round {server_round} agregasyonu başladı...")
        print(f"Results: {len(results)} clients, Failures: {len(failures)} clients")
        
       
        if not results:
            print("⚠️ Hiçbir client sonucu yok! Mevcut parametreleri kullanıyoruz.")
            return self.latest_parameters or self.initial_parameters, {}
        
        
        if server_round == INCREMENT_ROUND and self.current_model_classes == HAM_CLASSES:
            print(f"🚀 THRESHOLD aşıldı! Model {HAM_CLASSES} sınıftan {ISIC_CLASSES} sınıfa genişletiliyor...")
            
        
            if self.latest_parameters is not None:
                weights = parameters_to_ndarrays(self.latest_parameters)
                model = create_initial_model(num_classes=HAM_CLASSES)
                model.set_weights(weights)
                expanded_model = expand_model(model, new_classes=ISIC_CLASSES)
                expanded_parameters = ndarrays_to_parameters([np.array(w) for w in expanded_model.get_weights()])
                self.latest_parameters = expanded_parameters
                self.current_model_classes = ISIC_CLASSES
                
                print(f"✅ Model başarıyla {ISIC_CLASSES} sınıfa genişletildi!")
                
             
                save_model(expanded_parameters, f"{server_round}_expanded")
                
                aggregated_parameters, aggregated_metrics = super().aggregate_fit(server_round, results, failures)
                
                if aggregated_parameters is None:
                    print("⚠️ Agregasyon başarısız oldu, genişletilmiş parametreleri kullanıyoruz.")
                    return expanded_parameters, {}
                
                agg_weights = parameters_to_ndarrays(aggregated_parameters)
                if agg_weights[-2].shape[1] < ISIC_CLASSES:
                    print(f"⚠️ Aggregated parametreler hala {agg_weights[-2].shape[1]} sınıf boyutunda. Genişletilmiş parametreleri kullanıyoruz.")
                    self.latest_parameters = expanded_parameters
                    return expanded_parameters, aggregated_metrics
                else:
                    self.latest_parameters = aggregated_parameters
                    return aggregated_parameters, aggregated_metrics
        
       
        try:
            aggregated_parameters, aggregated_metrics = super().aggregate_fit(server_round, results, failures)
            
           
            if aggregated_parameters is None:
                print(f"⚠️ Round {server_round}: Agregasyon başarısız oldu, son parametreler kullanılıyor.")
                if self.latest_parameters is not None:
                    return self.latest_parameters, {}
                else:
                    print("⚠️ Mevcut parametre olmadığından başlangıç parametreleri kullanılıyor.")
                    return self.initial_parameters, {}
            
           
            agg_weights = parameters_to_ndarrays(aggregated_parameters)
            output_dim = agg_weights[-2].shape[1]
            
           
            if output_dim != self.current_model_classes:
                print(f"⚠️ Server model boyutu ({self.current_model_classes}) ile agregasyon sonucu ({output_dim}) uyumsuz!")
                self.current_model_classes = output_dim
                
            print(f"📏 Round {server_round} sonrası model çıkış boyutu: {output_dim}")
            self.latest_parameters = aggregated_parameters
            
           
            print(f"💾 Round {server_round} modeli kaydediliyor...")
            save_model(aggregated_parameters, server_round)
            
            return aggregated_parameters, aggregated_metrics
        
        except Exception as e:
            print(f"❌ Agregasyon sırasında hata oluştu: {str(e)}")
            import traceback
            traceback.print_exc()
            if self.latest_parameters is not None:
                print("⚠️ Hata oluştu, son parametreler kullanılıyor.")
                return self.latest_parameters, {}
            else:
                print("⚠️ Mevcut parametre olmadığından başlangıç parametreleri kullanılıyor.")
                return self.initial_parameters, {}
    
    def get_latest_parameters(self):
        return self.latest_parameters if self.latest_parameters is not None else self.initial_parameters

    def aggregate_evaluate(self, server_round, results, failures):
        aggregated_metrics = super().aggregate_evaluate(server_round, results, failures)
        print(f"📊 Round {server_round} değerlendirmesi tamamlandı, yedek model kaydediliyor...")
        if self.latest_parameters:
            weights = parameters_to_ndarrays(self.latest_parameters)
            output_dim = weights[-2].shape[1]
            print(f"📏 Evaluation sonrası model çıkış boyutu: {output_dim}")
            save_model(self.latest_parameters, f"{server_round}_eval")
        
        return aggregated_metrics


if __name__ == "__main__":
    NUM_ROUNDS = 8
    initial_model = create_initial_model(num_classes=HAM_CLASSES)
    initial_parameters = fl.common.ndarrays_to_parameters([np.array(w) for w in initial_model.get_weights()])

    strategy = CustomFedAvg(
        min_fit_clients=3,
        min_available_clients=3,
        min_evaluate_clients=3,
        initial_parameters=initial_parameters,
        on_fit_config_fn=on_fit_config,
        on_evaluate_config_fn=on_evaluate_config,
        evaluate_metrics_aggregation_fn=aggregate_evaluate_metrics,
    )

    print("🚀 Federated Learning Server Başlatılıyor...")
    print("💾 Başlangıç modeli kaydediliyor...")
    save_model(initial_parameters, 0)
    
    history = start_server(
        server_address="25.58.175.200:8080",
        config=fl.server.ServerConfig(num_rounds=NUM_ROUNDS),
        strategy=strategy
    )

    print("🌐 Final global model kaydediliyor...")
    try:
        final_params = strategy.get_latest_parameters()
        if final_params is None:
            print("⚠️ Son parametreler alınamadı, başlangıç parametreleri kullanılacak.")
            final_params = strategy.initial_parameters

        save_model(final_params, f"final_{NUM_ROUNDS}")
    except Exception as e:
        print(f"❌ Final model kaydedilemedi: {str(e)}")
        import traceback
        traceback.print_exc()