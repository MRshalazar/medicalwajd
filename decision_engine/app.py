from fastapi import FastAPI
from pydantic import BaseModel

from .engine import evaluate


app = FastAPI(
    title="Decision Engine"
)



class DecisionRequest(BaseModel):

    status: str




@app.post("/decision")
def decision(req: DecisionRequest):


    print("\n" + "=" * 70)
    print("DECISION ENGINE")
    print("=" * 70)



    print("\nDecision request received")


    print("Proof status:")

    print(
        req.status
    )



    print("\nPrivacy check:")

    print(
        "✓ No sensor value received"
    )

    print(
        "✓ Decision based only on ZKP result"
    )



    print("\nEvaluating clinical status...")



    try:


        result = evaluate(
            req.status
        )


    except Exception as e:


        print("\n❌ DECISION ENGINE ERROR")

        print(e)


        return {
            "error": str(e)
        }



    print("\n✅ Clinical decision generated")


    print(result)



    print("=" * 70)



    return result