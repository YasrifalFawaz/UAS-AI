import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib

# Load dataset
data = pd.read_csv("data/dataset.csv", sep=";")

# Encode level (mudah, normal, sulit)
le_level = LabelEncoder()
data["level_encoded"] = le_level.fit_transform(data["level"])

# Encode label target
le_label = LabelEncoder()
data["label_encoded"] = le_label.fit_transform(data["label"])

# Feature & target
X = data[["skor", "waktu", "level_encoded"]]
y = data["label_encoded"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# Train Decision Tree
model = DecisionTreeClassifier(max_depth=3)
model.fit(X_train, y_train)

# Simpan model dan encoder
joblib.dump(model, "model/decision_tree.pkl")
joblib.dump(le_level, "model/level_encoder.pkl")
joblib.dump(le_label, "model/label_encoder.pkl")

print("Model berhasil dilatih dan disimpan.")
