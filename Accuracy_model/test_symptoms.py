import pickle
import pandas as pd

# Load the trained model and label encoder
model = pickle.load(open("symptom_model.pkl", "rb"))
le = pickle.load(open("label_encoder.pkl", "rb"))

# Load dataset to get feature columns
url = "https://raw.githubusercontent.com/anujdutt9/Disease-Prediction-from-Symptoms/master/dataset/training_data.csv"
try:
    df = pd.read_csv(url)
except:
    url = "https://raw.githubusercontent.com/kaushik-rohit/Disease-Prediction-from-Symptoms/master/Training.csv"
    df = pd.read_csv(url)

if 'label' in df.columns:
    target_col = 'label'
elif 'prognosis' in df.columns:
    target_col = 'prognosis'

X = df.drop(target_col, axis=1)

def predict_disease(symptom_list):
    """Predict disease from list of symptoms"""
    def normalize(name):
        return str(name).strip().lower().replace(' ', '_').replace('-', '_')
    
    # Create feature mapping
    normalized_col_map = {normalize(col): col for col in X.columns}
    
    # Create input row
    input_row = pd.DataFrame([0] * len(X.columns), index=X.columns).T
    
    matched = 0
    for s in symptom_list:
        key = normalize(s)
        if key in normalized_col_map:
            input_row.loc[0, normalized_col_map[key]] = 1
            matched += 1
    
    if matched == 0:
        return "ERROR: None of the symptoms matched!"
    
    # Predict
    pred_idx = model.predict(input_row)[0]
    pred_proba = model.predict_proba(input_row)[0]
    pred_label = le.inverse_transform([pred_idx])[0]
    confidence = pred_proba[pred_idx] * 100
    
    return pred_label, confidence, matched

# ==============================================
# TEST DIFFERENT SYMPTOM COMBINATIONS
# ==============================================

print("=" * 60)
print("SYMPTOM-BASED DISEASE PREDICTION TESTER")
print("=" * 60)

# Test cases
test_cases = [
    ["fever", "cough", "fatigue"],
    ["itching", "skin_rash", "dischromic_patches"],
    ["joint_pain", "vomiting", "fatigue"],
    ["chest_pain", "breathlessness", "sweating"],
    ["stomach_pain", "acidity", "vomiting"],
    ["headache", "back_pain", "weakness_in_limbs"],
    ["chills", "vomiting", "high_fever"],
    ["continuous_sneezing", "watering_from_eyes", "runny_nose"]
]

print("\nTesting different symptom combinations:\n")

for i, symptoms in enumerate(test_cases, 1):
    print(f"Test {i}: {symptoms}")
    disease, confidence, matched = predict_disease(symptoms)
    print(f"   → Predicted Disease: {disease}")
    print(f"   → Confidence: {confidence:.2f}%")
    print(f"   → Matched Symptoms: {matched}/{len(symptoms)}")
    print()

# Interactive mode
print("=" * 60)
print("INTERACTIVE MODE - Enter your own symptoms!")
print("=" * 60)
print("\nAvailable symptoms (sample):")
sample_symptoms = list(X.columns[:20])
for i, sym in enumerate(sample_symptoms, 1):
    print(f"{i}. {sym}")
print("... and more\n")

while True:
    print("\nEnter symptoms separated by commas (or 'quit' to exit):")
    user_input = input("Symptoms: ").strip()
    
    if user_input.lower() in ['quit', 'exit', 'q']:
        print("Exiting...")
        break
    
    if not user_input:
        continue
    
    symptoms = [s.strip() for s in user_input.split(',')]
    disease, confidence, matched = predict_disease(symptoms)
    
    print(f"\n✓ Predicted Disease: {disease}")
    print(f"✓ Confidence: {confidence:.2f}%")
    print(f"✓ Matched Symptoms: {matched}/{len(symptoms)}")
