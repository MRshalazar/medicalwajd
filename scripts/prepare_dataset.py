import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PATIENT_FILE = ROOT / "datasets/original/MimicPatient.ndjson"
CONDITION_FILE = ROOT / "datasets/original/MimicCondition.ndjson"
OBS_FILE = ROOT / "datasets/original/MimicObservationChartevents.ndjson"

OUTPUT = ROOT / "datasets/processed"
OUTPUT.mkdir(exist_ok=True)


# ------------------------
# Load first 100 patients
# ------------------------

patients = []

patient_ids = set()

with open(PATIENT_FILE, encoding="utf-8") as f:
    for line in f:
        patient = json.loads(line)

        patients.append(patient)

        patient_ids.add(patient["id"])

        if len(patients) == 100:
            break


# ------------------------
# Conditions
# ------------------------

conditions = []

with open(CONDITION_FILE, encoding="utf-8") as f:

    for line in f:

        obj = json.loads(line)

        ref = obj["subject"]["reference"].split("/")[-1]

        if ref in patient_ids:
            conditions.append(obj)


# ------------------------
# Observations
# ------------------------

observations = []

with open(OBS_FILE, encoding="utf-8") as f:

    for line in f:

        obj = json.loads(line)

        ref = obj["subject"]["reference"].split("/")[-1]

        if ref in patient_ids:
            observations.append(obj)


# ------------------------
# Save
# ------------------------

json.dump(
    patients,
    open(OUTPUT / "patients_100.json", "w", encoding="utf8"),
    indent=2,
)

json.dump(
    conditions,
    open(OUTPUT / "conditions_100.json", "w", encoding="utf8"),
    indent=2,
)

json.dump(
    observations,
    open(OUTPUT / "observations_100.json", "w", encoding="utf8"),
    indent=2,
)

print("Patients:", len(patients))
print("Conditions:", len(conditions))
print("Observations:", len(observations))