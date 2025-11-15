import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pickle

# ================================
# 1) LOAD DATA FROM DIRECT LINKS
# ================================

# Dataset 1 – Disease symptom dataset (recommended)
url1 = "https://raw.githubusercontent.com/anujdutt9/Disease-Prediction-from-Symptoms/master/dataset/training_data.csv"

# Dataset 2 – Alternative dataset
url2 = "https://raw.githubusercontent.com/kaushik-rohit/Disease-Prediction-from-Symptoms/master/Training.csv"

print("Loading dataset from direct link...")
try:
    df = pd.read_csv(url1)
    print("Loaded Dataset 1 Successfully!")
except Exception as e:
    print(f"Failed to load Dataset 1: {e}")
    try:
        df = pd.read_csv(url2)
        print("Loaded Dataset 2 Successfully!")
    except Exception as e2:
        print(f"Failed to load Dataset 2: {e2}")
        raise Exception("Could not load any dataset!")

# Rename target column if needed
# Dataset 1 → target column = 'label'
# Dataset 2 → target column = 'prognosis'

if 'label' in df.columns:
    target_col = 'label'
elif 'prognosis' in df.columns:
    target_col = 'prognosis'
else:
    raise Exception("Could not identify target column!")

print(f"Using target column: {target_col}")

# ==================================
# 2) SPLIT FEATURES & TARGET
# ==================================
X = df.drop(target_col, axis=1)
y = df[target_col]

# ==================================
# 3) ENCODE DISEASE LABELS
# ==================================
le = LabelEncoder()
y = le.fit_transform(y)

# ==================================
# 4) TRAIN-TEST SPLIT
# ==================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ==================================
# 5) TRAIN MODEL
# ==================================
print("Training RandomForest model...")
model = RandomForestClassifier(
    n_estimators=350,
    max_depth=20,
    random_state=42
)
model.fit(X_train, y_train)

# ==================================
# 6) MODEL ACCURACY
# ==================================
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print("==========================================")
print(f"Symptom Model Accuracy: {accuracy*100:.2f}%")
print("==========================================")

# ==================================
# 7) SAVE MODEL
# ==================================
pickle.dump(model, open("symptom_model.pkl", "wb"))
pickle.dump(le, open("label_encoder.pkl", "wb"))

print("Model and label encoder saved successfully!")


def predict_from_symptoms(symptom_list):
    """
    Build a single-row feature vector from the given symptoms using the trained model's feature columns
    and return the predicted disease label (decoded with the label encoder).
    """
    def _normalize(name: str) -> str:
        return str(name).strip().lower().replace(' ', '_').replace('-', '_')

    if not isinstance(symptom_list, (list, tuple)):
        raise ValueError("symptom_list must be a list or tuple of symptom names.")

    # Map normalized column names to original columns for matching
    normalized_col_map = {_normalize(col): col for col in X.columns}

    # Create a zeroed feature row with the same columns and order as training data
    input_row = pd.DataFrame([0] * len(X.columns), index=X.columns).T  # index [0], columns = X.columns

    matched = 0
    for s in symptom_list:
        key = _normalize(s)
        if key in normalized_col_map:
            input_row.loc[0, normalized_col_map[key]] = 1
            matched += 1

    if matched == 0:
        raise ValueError("None of the provided symptoms matched the model feature columns.")

    pred_idx = model.predict(input_row)[0]
    pred_label = le.inverse_transform([pred_idx])[0]
    return str(pred_label)


# EXAMPLE:
symptoms = ["fever", "headache", "nausea"]
result = predict_from_symptoms(symptoms)

print("Predicted Disease:", result)