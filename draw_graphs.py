import os
import json
import matplotlib.pyplot as plt
import numpy as np

def read_scores(folder_path):
    scores = []

    for file_name in os.listdir(folder_path):
        if file_name.endswith(".json"):
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, "r") as file:
                data = json.load(file)
                scores.append(data)

    return scores

def normalize_scores(scores, metrics):
    for metric in metrics:
        values = np.array([score[metric] for score in scores])
        min_val, max_val = values.min(), values.max()
        if max_val - min_val != 0:
            normalized_values = (values - min_val) / (max_val - min_val)
        else:
            normalized_values = np.full_like(values, 0.5)  # Default to 0.5 if all values are the same
        for i, score in enumerate(scores):
            score[f"normalized_{metric}"] = normalized_values[i]
    return scores

def plot_scores(scores, metrics, output_folder):
    algorithms = [score["algorithm"] for score in scores]
    colors = ["blue", "green", "orange", "red"]

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for i, metric in enumerate(metrics):
        metric_label = metric.replace("_", " ").capitalize()
        if metric == "execution_time":
            metric_label += " (s)"
        elif metric == "usage_memory":
            metric_label += " (MB)"

        values = [score[metric] for score in scores]
        plt.figure()
        plt.bar(algorithms, values, color=colors[i % len(colors)])
        plt.title(f"Comparison of {metric}")
        plt.xlabel("Algorithm")
        plt.ylabel(metric_label)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        output_path = os.path.join(output_folder, f"{metric}_comparison.png")
        plt.savefig(output_path, bbox_inches="tight")
        plt.close()

def plot_radar_chart(scores, metrics, output_folder):
    algorithms = [score["algorithm"] for score in scores]
    num_metrics = len(metrics)
    angles = np.linspace(0, 2 * np.pi, num_metrics, endpoint=False).tolist()
    angles += angles[:1]

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    plt.figure(figsize=(8, 8))
    for score in scores:
        values = [score[f"normalized_{metric}"] for metric in metrics]
        values += values[:1]
        plt.polar(angles, values, label=score["algorithm"])

    metric_labels = [
        "Execution time",
        "Tc score",
        "Usage memory",
        "Sp score"
    ]

    for i, label in enumerate(metric_labels):
        if i == 0 or i == 2:  # Rotate labels for east and west positions
            metric_labels[i] = "\n".join(label.split())

    plt.xticks(angles[:-1], metric_labels)
    plt.title("Algorithm Feature Comparison (Radar Chart)", y=1.1)
    plt.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), title="Algorithms")
    output_path = os.path.join(output_folder, "radar_chart.png")
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()

def main():
    folder_path = "scores/"  # Change this if the folder is located elsewhere
    output_folder = "graphs/"
    metrics = ["sp_score", "tc_score", "execution_time", "usage_memory"]

    scores = read_scores(folder_path)
    normalized_scores = normalize_scores(scores, metrics)

    plot_scores(scores, metrics, output_folder)  # Plot original metrics
    plot_radar_chart(normalized_scores, metrics, output_folder)  # Plot radar chart with normalized metrics

if __name__ == "__main__":
    main()
