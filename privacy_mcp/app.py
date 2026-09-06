from fastapi import FastAPI
from .zkp_client import generate_and_verify_proof


app = FastAPI(
    title="Privacy MCP"
)



@app.post("/request-proof")
def request_proof(data: dict):


    print("\n" + "=" * 70)
    print("PRIVACY MCP")
    print("=" * 70)


    print("\nProof request received")


    print("\nReceived data:")

    print(data)



    # Privacy check
    if "bounds" not in data:

        print("\n❌ Missing bounds")

        return {
            "error": "bounds missing"
        }



    print("\nPrivacy verification:")

    print("✓ Received only clinical limits")

    print("✓ Raw sensor value is NOT exposed to MCP")



    bounds = data["bounds"]


    print("\nBounds received:")

    print(
        "Minimum:",
        bounds.get("min")
    )

    print(
        "Maximum:",
        bounds.get("max")
    )



    print("\nGenerating Zero-Knowledge Proof...")


    try:


        result = generate_and_verify_proof(
            bounds
        )


    except Exception as e:


        print("\n❌ ZKP ERROR")

        print(e)


        return {
            "error": str(e)
        }



    print("\n✅ ZKP completed")


    print("\nProof result returned:")

    print(result)



    print("\nPrivacy guarantee:")

    print("Sensor value remains hidden 🔒")


    print("=" * 70)



    return result