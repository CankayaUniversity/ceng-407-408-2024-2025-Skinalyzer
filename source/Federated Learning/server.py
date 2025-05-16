import flwr as fl
from flwr.server import start_server
from flwr.server.strategy import FedAvg
from flwr.common import parameters_to_ndarrays
import numpy as np
import tensorflow as tf
import tensorflow_addons as tfa
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.models import Model
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
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


THRESHOLD = 4
INCREMENT_ROUND = THRESHOLD + 1

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

# Custom Strategy
class CustomFedAvg(FedAvg):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.latest_parameters = None
    
    def aggregate_fit(self, server_round, results, failures):
        aggregated_parameters, aggregated_metrics = super().aggregate_fit(server_round, results, failures)
        self.latest_parameters = aggregated_parameters
        
        
        print(f"🔄 Round {server_round} tamamlandı, model kaydediliyor...")
        save_model(aggregated_parameters, server_round)
        
        return aggregated_parameters, aggregated_metrics
    
    def get_latest_parameters(self):
        return self.latest_parameters if self.latest_parameters is not None else self.initial_parameters

    def aggregate_evaluate(self, server_round, results, failures):
       
        aggregated_metrics = super().aggregate_evaluate(server_round, results, failures)
        
        
        print(f"📊 Round {server_round} değerlendirmesi tamamlandı, yedek model kaydediliyor...")
        if self.latest_parameters:
            save_model(self.latest_parameters, f"{server_round}_eval")
        
        return aggregated_metrics


if __name__ == "__main__":
    NUM_ROUNDS = 8
    initial_model = create_initial_model(num_classes=7)
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