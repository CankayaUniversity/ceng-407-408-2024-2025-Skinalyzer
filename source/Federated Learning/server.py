import flwr as fl
from flwr.server.strategy import FedAvg
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras import Input
import numpy as np
import tensorflow as tf

def create_initial_model():
    model = Sequential([
        Input(shape=(128,128,3)),
        Conv2D(32, (3,3), activation="relu"),
        MaxPooling2D(pool_size=(2,2)),
        Dropout(0.25),
        Conv2D(32, (3,3), activation="relu"),
        Conv2D(64, (3,3), activation="relu"),
        MaxPooling2D(pool_size=(2,2)),
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

initial_model = create_initial_model()
initial_parameters = [np.array(layer) for layer in initial_model.get_weights()]

def aggregate_evaluate_metrics(metrics_list):
    accuracies = []
    f1_scores = []

    print(" Gelen Metrikler:", metrics_list)

    for _, m in metrics_list:
        if "accuracy" in m:
            accuracies.append(m["accuracy"])
        if "f1_score" in m:
            f1_scores.append(m["f1_score"])

    avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0.0
    avg_f1_score = sum(f1_scores) / len(f1_scores) if f1_scores else 0.0

    print("\n Global Model Evaluation ")
    print(f" Average Accuracy: {avg_accuracy:.4f}")
    print(f" Average F1-Score: {avg_f1_score:.4f}\n")

    return {"accuracy": avg_accuracy, "f1_score": avg_f1_score}

strategy = FedAvg(
    min_fit_clients=1,
    min_available_clients=1,
    min_evaluate_clients=1,
    initial_parameters=fl.common.ndarrays_to_parameters(initial_parameters),
    evaluate_metrics_aggregation_fn=aggregate_evaluate_metrics
)

if __name__ == "__main__":
    print(" Federated Learning Server Başlatılıyor...\n")
    fl.server.start_server(
        server_address="0.0.0.0:8080",
        config=fl.server.ServerConfig(num_rounds=5),
        strategy=strategy
    )
