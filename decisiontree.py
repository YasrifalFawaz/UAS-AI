import joblib
import matplotlib.pyplot as plt
from sklearn.tree import plot_tree

# Load model dan encoder
model = joblib.load("model/decision_tree.pkl")
label_encoder = joblib.load("model/label_encoder.pkl")

# Nama fitur
feature_names = ["skor", "waktu", "level_encoded"]

# Nama kelas (hasil klasifikasi)
class_names = label_encoder.classes_

plt.figure(figsize=(22, 14))

plot_tree(
    model,
    feature_names=feature_names,
    class_names=class_names,
    filled=True,
    rounded=True,
    fontsize=11
)

plt.title("Decision Tree – Adaptive Learning Feedback Model", fontsize=18)
plt.show()
