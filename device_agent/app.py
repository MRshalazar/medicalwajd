from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import json

from .sensor import read_systolic_bp

app = FastAPI()


class Policy(BaseModel):
    min: int
    max: int


@app.post("/prove")
def prove(policy: Policy):

    value = read_systolic_bp()

    payload = {
        "value": value,
        "min": policy.min,
        "max": policy.max
    }

    print("Sensor value acquired locally.")
    print("Generating ZKP proof locally.")

    result = subprocess.run(
        [
            r"D:\9raya\memoire 2026\Privacy-Preserving-CDSS\zkp_engine\target\debug\zkp_engine.exe"
        ],
        input=json.dumps(payload),
        capture_output=True,
        text=True
    )

    print("RETURN CODE:", result.returncode)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)

    return json.loads(result.stdout)