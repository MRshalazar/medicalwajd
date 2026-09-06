from fastapi import FastAPI
from fastapi.responses import JSONResponse
from langgraph.graph import StateGraph, END

from .graph import (
    State,
    get_patient,
    get_policy,
    get_proof,
    get_decision
)


app = FastAPI(
    title="LangGraph Coordinator"
)



print("\n" + "=" * 70)
print("INITIALIZING LANGGRAPH COORDINATOR")
print("=" * 70)


builder = StateGraph(State)


builder.add_node(
    "patient",
    get_patient
)

builder.add_node(
    "policy",
    get_policy
)

builder.add_node(
    "proof",
    get_proof
)

builder.add_node(
    "decision",
    get_decision
)



builder.set_entry_point(
    "patient"
)


builder.add_edge(
    "patient",
    "policy"
)

builder.add_edge(
    "policy",
    "proof"
)

builder.add_edge(
    "proof",
    "decision"
)

builder.add_edge(
    "decision",
    END
)



graph = builder.compile()


print("✅ LangGraph workflow ready")

print(
"""
patient
   ↓
policy
   ↓
proof
   ↓
decision
"""
)

print("=" * 70)




@app.get("/run/{patient_id}")
def run(patient_id: str):


    print("\n" + "=" * 70)
    print("LANGGRAPH EXECUTION START")
    print("=" * 70)


    print("Patient requested:")
    print(patient_id)



    initial_state: State = {

        "patient_id": patient_id,

        "patient": {},

        "policy": {},

        "proof": {},

        "decision": {}

    }


    try:


        result = graph.invoke(
            initial_state
        )


        print("\n" + "=" * 70)
        print("LANGGRAPH EXECUTION COMPLETE")
        print("=" * 70)


        print("Final state:")
        print(result)


        print("=" * 70)



        return result



    except Exception as e:


        import traceback


        print("\n" + "=" * 70)

        print("❌ LANGGRAPH ERROR")

        print("=" * 70)


        traceback.print_exc()


        return JSONResponse(
            status_code=502,
            content={"error": str(e)}
        )