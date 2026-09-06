from fastapi import FastAPI
from .database import get_patient_by_id

app = FastAPI(
    title="Patient MCP"
)


@app.get("/patient/{patient_id}")
def get_patient(patient_id: str):

    print("\n" + "=" * 70)
    print("PATIENT MCP")
    print("=" * 70)

    print("Patient request received:")
    print("Patient ID:", patient_id)


    print("\nSearching patient database...")

    patient = get_patient_by_id(patient_id)


    if patient is None:

        print("\n❌ Patient not found")

        print("=" * 70)

        return {
            "error": "patient not found"
        }


    print("\n✅ Patient found")

    print("Patient information:")
    print(patient)

    print("=" * 70)


    return patient