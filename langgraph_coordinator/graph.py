import os
from typing import TypedDict
import requests

PATIENT_MCP_URL = os.getenv("PATIENT_MCP_URL", "http://127.0.0.1:8005")
RULE_ENGINE_URL = os.getenv("RULE_ENGINE_URL", "http://127.0.0.1:8004")
PRIVACY_MCP_URL = os.getenv("PRIVACY_MCP_URL", "http://127.0.0.1:8003")
DECISION_ENGINE_URL = os.getenv("DECISION_ENGINE_URL", "http://127.0.0.1:8002")


class State(TypedDict):

    patient_id: str
    patient: dict
    policy: dict
    proof: dict
    decision: dict




def get_patient(state):


    print("\n")
    print("=" * 70)
    print("PATIENT NODE")
    print("=" * 70)



    print("Requesting patient data from Patient MCP")


    url = (
        f"{PATIENT_MCP_URL}/patient/{state['patient_id']}"
    )


    print("URL:")
    print(url)



    response = requests.get(
        url,
        timeout=10
    )

    response.raise_for_status()
    patient = response.json()



    print("\nPatient received:")

    print(patient)



    return {

        "patient": patient

    }




def get_policy(state):


    print("\n")
    print("=" * 70)
    print("POLICY NODE")
    print("=" * 70)



    print("Sending patient to Rule Engine")


    print(state["patient"])



    response = requests.post(

        f"{RULE_ENGINE_URL}/policy",

        json=state["patient"],

        timeout=180

    )
    response.raise_for_status()
    policy = response.json()


    if "error" in policy:
        raise RuntimeError(f"Rule Engine error: {policy['error']}")



    print("\nPersonalized policy received:")

    print(policy)



    return {

        "policy": policy

    }





def get_proof(state):


    print("\n")
    print("=" * 70)
    print("PROOF NODE")
    print("=" * 70)



    bounds = {

        "min": state["policy"]["min"],

        "max": state["policy"]["max"]

    }



    print("Sending ONLY bounds to Privacy MCP:")

    print(bounds)



    print(
        "Sensor value is NOT included 🔒"
    )



    response = requests.post(

        f"{PRIVACY_MCP_URL}/request-proof",

        json={

            "bounds": bounds

        },

        timeout=30

    )



    proof = response.json()



    print("\nProof received:")

    print(proof)



    return {

        "proof": proof

    }





def get_decision(state):


    print("\n")
    print("=" * 70)
    print("DECISION NODE")
    print("=" * 70)



    print("Sending proof status:")

    print(
        state["proof"]["status"]
    )



    response = requests.post(

        f"{DECISION_ENGINE_URL}/decision",

        json={

            "status": state["proof"]["status"]

        },

        timeout=10

    )



    decision = response.json()



    print("\nDecision received:")

    print(decision)



    return {

        "decision": decision

    }