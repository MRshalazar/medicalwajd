from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .policy_generator import generate_policy


app = FastAPI(
    title="Rule Engine"
)


@app.post("/policy")
def policy(patient: dict, use_rag: bool = True):

    print("\n" + "=" * 70)
    print("RULE ENGINE")
    print("=" * 70)

    print("Policy generation request received")

    print("\nPatient data received:")
    print(patient)


    print("\nGenerating personalized clinical policy...")


    try:

        result = generate_policy(patient, use_rag=use_rag)


        print("\n✅ Policy generated")

        print("Generated policy:")
        print(result)


        print("=" * 70)


        return result


    except Exception as e:


        print("\n❌ RULE ENGINE ERROR")

        print(e)

        print("=" * 70)


        return JSONResponse(
            status_code=502,
            content={"error": str(e)}
        )
