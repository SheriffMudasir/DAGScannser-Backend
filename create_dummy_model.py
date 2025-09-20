# create_dummy_model.py (run this once)
import joblib
from sklearn.ensemble import RandomForestClassifier
import numpy as np

# Create a simple dummy model
model = RandomForestClassifier(random_state=42)
X = np.array([[10,0,0,0], [80,1,1,1], [50,0,1,0], [20,1,0,1]])
y = np.array([0, 1, 0, 1]) # 0 = low trust, 1 = high trust
model.fit(X, y)

# Save it
joblib.dump(model, 'analyser/trust_model.pkl')
print("Dummy trust_model.pkl created in analyser/ directory.")