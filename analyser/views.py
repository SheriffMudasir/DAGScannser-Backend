"""
analyzer/views.py

API views for the 'analyzer' application.

"""

import os
import json
import joblib
import numpy as np

from web3 import Web3
from eth_account import Account
from eth_account.signers.local import LocalAccount
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ML_MODEL_PATH = os.path.join(BASE_DIR, 'trust_model.pkl')
SMART_CONTRACT_ABI_PATH = os.path.join(BASE_DIR, 'dag_scanner_abi.json')


ml_model = None
try:
    ml_model = joblib.load(ML_MODEL_PATH)
    print(f"✅ ML model loaded successfully from {ML_MODEL_PATH}")
except Exception as e:
    print(f"❌ ERROR loading ML model: {e}. Prediction will be mocked.")

contract_abi = None
try:
    with open(SMART_CONTRACT_ABI_PATH, 'r') as f:
        contract_abi = json.load(f)
    print(f"✅ Smart contract ABI loaded successfully from {SMART_CONTRACT_ABI_PATH}")
except Exception as e:
    print(f"❌ ERROR loading ABI: {e}. Some admin functionality may be disabled.")



def mock_features(address: str) -> dict:
    """
    Mocks feature extraction for a given contract address.
    Generates deterministic features based on the address for demonstration.
    
    We replace this with a robustly trained ai model in a real-world scenario.
    """
    
    try:
        last_digit = int(address[-1], 16)
    except (ValueError, IndexError):
        last_digit = 0

    return {
        "ownerTokens": 80 if last_digit % 2 == 0 else 10,
        "liquidityLocked": 1 if last_digit % 3 == 0 else 0,
        "ownershipRenounced": 1 if last_digit % 5 == 0 else 0,
        "suspiciousFunctions": 1 if last_digit % 7 == 0 else 0,
    }

def run_prediction(features: dict) -> tuple[int, str]:
    """
    Runs the ML model to predict a trust score and status.
    Falls back to a simple mock logic if the model is not loaded.
    
    
    same thing here. In real world, this would use a trained and fine-tuned production ready ai model.
    """
    if ml_model:
        X = np.array([[
            features["ownerTokens"], features["liquidityLocked"],
            features["ownershipRenounced"], features["suspiciousFunctions"]
        ]])
        proba_scam = ml_model.predict_proba(X)[0][1]
        score = int((1 - proba_scam) * 100)
    else:
        print("MOCK: Using fallback logic for prediction.")
        score = 65 + (features["ownerTokens"] // 4) if features["ownerTokens"] > 50 else 35

    if score > 70:
        status_msg = "Safe ✅"
    elif score > 40:
        status_msg = "Warning ⚠️"
    else:
        status_msg = "High Risk ❌"

    return score, status_msg



@api_view(["POST"])
def analyze(request):
    """
    This API endpoint performs off-chain analysis of a smart contract address.

    It receives an address, runs it through an ML model to generate a trust
    score and status, and returns this data to the client. The client is
    then responsible for initiating the on-chain transaction.
    """
    address = request.data.get("address")

    # 1. Validate the input address.
    if not address or not isinstance(address, str) or not address.startswith("0x"):
        return Response(
            {"error": "A valid contract address starting with '0x' is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 2. Perform the off-chain analysis.
    print(f"🔎 Analyzing address: {address}")
    features = mock_features(address)
    score, status_msg = run_prediction(features)
    print(f"📊 Prediction complete - Score: {score}, Status: {status_msg}")

    # 3. Return the analysis result to the client.
    # In a real-world scenario, we there will be lots of other data based on the ai mode and will also log this analysis to a database.
    return Response({
        "address": address,
        "score": score,
        "status": status_msg
    }, status=status.HTTP_200_OK)