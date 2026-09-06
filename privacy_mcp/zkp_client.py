import json
import os
import subprocess
from pathlib import Path


DEFAULT_ENGINE_NAME = "zkp_engine.exe" if os.name == "nt" else "zkp_engine"
ENGINE_PATH_OVERRIDE = os.getenv("ZKP_ENGINE_PATH")

if ENGINE_PATH_OVERRIDE:
    ENGINE = Path(ENGINE_PATH_OVERRIDE).expanduser().resolve()
else:
    ENGINE = (
        Path(__file__).resolve().parent.parent
        / "zkp_engine"
        / "target"
        / "release"
        / DEFAULT_ENGINE_NAME
    )



def generate_and_verify_proof(bounds):


    print("\n" + "=" * 70)
    print("DEVICE ZKP CLIENT")
    print("=" * 70)



    print("\nRust ZKP Engine:")

    print(
        ENGINE
    )



    if not ENGINE.exists():

        print("\n❌ Rust engine not found")

        raise FileNotFoundError(
            ENGINE
        )


    print("✓ Rust engine found")



    # ==================================================
    # Device side sensor simulation
    # ==================================================

    print("\nDEVICE SENSOR")


    print(
        "Reading sensor value locally..."
    )


    device_value = 190

    print("\n" + "=" * 60)
    print("LOCAL SENSOR READING (DEBUG ONLY)")
    print("=" * 60)
    print(f"Sensor Value = {device_value}")
    print(
        f"Expected Range = "
        f"{bounds['min']} - {bounds['max']}"
    )
    print("=" * 60)



    print(
        "Sensor value generated locally:"
    )


    print(
        device_value
    )



    print(
        "\nPrivacy boundary:"
    )


    print(
        "✓ This value never leaves the device"
    )



    # ==================================================
    # ZKP generation
    # ==================================================


    print("\nPreparing Zero-Knowledge proof...")


    request = {

        "value": device_value,

        "min": bounds["min"],

        "max": bounds["max"]

    }



    print("\nProof parameters:")

    print({

        "min": bounds["min"],

        "max": bounds["max"]

    })


    print(
        "Sensor value hidden from external components 🔒"
    )



    print("\nCalling Rust Bulletproof Engine...")



    try:


        result = subprocess.run(

            [str(ENGINE)],

            input=json.dumps(request),

            capture_output=True,

            text=True,

            check=True,

        )


    except subprocess.CalledProcessError as e:


        print("\n❌ Rust execution failed")

        print(e.stderr)

        raise e



    print("\nRust response:")

    print(
        result.stdout
    )



    proof = json.loads(
        result.stdout
    )



    print("\n✅ Proof generated")


    print(proof)


    print("=" * 70)



    return proof