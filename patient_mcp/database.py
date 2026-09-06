import json
from pathlib import Path
from datetime import date


DATA = (
    Path(__file__).parent.parent
    / "datasets"
    / "samples_10"
    / "patients_sample_10.json"
)


def calculate_age(birth_date):
    """Calculate age from FHIR birthDate."""

    if not birth_date:
        return None

    try:
        birth = date.fromisoformat(birth_date)
        today = date.today()

        age = today.year - birth.year

        if (today.month, today.day) < (birth.month, birth.day):
            age -= 1

        return age

    except Exception:
        return None


def get_patient_by_id(patient_id):

    print("\n" + "=" * 70)
    print("PATIENT DATABASE")
    print("=" * 70)

    print("Requested patient ID:")
    print(patient_id)

    print("\nDataset:")
    print(DATA)

    # ------------------------------------------------
    # Check dataset
    # ------------------------------------------------

    if not DATA.exists():

        print("\n❌ DATASET NOT FOUND")
        print(DATA)

        return None

    print("\n✓ Dataset found")

    # ------------------------------------------------
    # Load FHIR dataset
    # ------------------------------------------------

    try:

        with open(DATA, encoding="utf-8") as f:
            patients = json.load(f)

    except Exception as e:

        print("\n❌ DATASET READ ERROR")
        print(e)

        return None

    print("Number of FHIR patients:")
    print(len(patients))

    # ------------------------------------------------
    # Search patient
    # ------------------------------------------------

    for p in patients:

        identifiers = p.get("identifier", [])

        for identifier in identifiers:

            identifier_value = str(
                identifier.get("value", "")
            )

            if identifier_value == str(patient_id):

                print("\n✓ PATIENT FOUND")

                gender = p.get("gender")

                birth_date = p.get("birthDate")

                age = calculate_age(birth_date)

                # Your original system needs a condition.
                # For now we use hypertension for the
                # thesis demo patients.

                condition = "hypertension"

                patient = {
                    "id": identifier_value,
                    "gender": gender,
                    "age": age,
                    "condition": condition
                }

                print("\nPatient information:")

                print(patient)

                print("=" * 70)

                return patient

    # ------------------------------------------------
    # Patient not found
    # ------------------------------------------------

    print("\n❌ PATIENT NOT FOUND")

    print("Requested ID:")
    print(patient_id)

    print("=" * 70)

    return None