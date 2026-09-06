import os
import requests
import ollama
import json
import re

KNOWLEDGE_MCP_URL = os.getenv("KNOWLEDGE_MCP_URL", "http://127.0.0.1:8010")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "180"))
OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "128"))


def generate_policy(patient, use_rag=True):


    print("\n" + "=" * 70)
    print("POLICY GENERATOR")
    print("=" * 70)


    condition = patient["condition"]
    age = patient["age"]

    if not use_rag:
        return generate_policy_without_rag(patient)


    print("\nPatient information:")
    print(patient)


    # ============================================
    # RAG retrieval
    # ============================================

    print("\nCalling Knowledge MCP (RAG)...")

    rag_url = (
        f"{KNOWLEDGE_MCP_URL}/guidelines/{condition}"
    )


    print("RAG URL:")
    print(rag_url)


    try:

        rag_response = requests.get(
            rag_url,
            timeout=30
        )


        print(
            "\nKnowledge MCP status:",
            rag_response.status_code
        )


        data = rag_response.json()

        print("\nKnowledge MCP response:")
        print(data)

        if "guidelines" not in data:

            print("\n❌ KNOWLEDGE MCP ERROR")
            print(data)

            raise Exception(
                f"Knowledge MCP Error:\n{data}"
            )

        docs = data["guidelines"]

    except Exception as e:

        print("\n❌ RAG ERROR")
        print(e)

        raise e



    print("\n✅ Guidelines retrieved from RAG")

    print(
        "Number of documents:",
        len(docs)
    )


    for i, doc in enumerate(docs):

        print("\n-----------------------------")
        print(
            "Guideline",
            i + 1
        )

        print(
            doc[:300]
        )



    context = "\n\n".join(docs)



    # ============================================
    # Ollama prompt
    # ============================================

    prompt = f"""
Patient:

Age: {age}
Condition: {condition}

Medical Guidelines:

{context}


Based on the medical guidelines,
generate personalized safe limits.

Return ONLY JSON.

Example:

{{
   "parameter":"systolic_bp",
   "min":110,
   "max":135
}}
"""


    print("\n" + "=" * 70)
    print("SENDING REQUEST TO OLLAMA")
    print("=" * 70)


    print("Model:")
    print("llama3")


    print("\nPrompt:")
    print(prompt)



    # ============================================
    # Ollama call
    # ============================================

    try:

        client = ollama.Client(
            host=OLLAMA_HOST,
            timeout=OLLAMA_TIMEOUT
        )

        response = client.chat(

            model="llama3",

            format="json",

            messages=[
                {
                    "role":"user",
                    "content":prompt
                }
            ],
            options={
                "temperature": 0,
                "num_predict": OLLAMA_NUM_PREDICT
            }

        )


    except Exception as e:

        print("\n❌ OLLAMA ERROR")
        print(e)

        raise e



    text = response["message"]["content"]



    print("\n" + "=" * 70)
    print("OLLAMA RESPONSE")
    print("=" * 70)

    print(text)



    # ============================================
    # JSON extraction
    # ============================================

    match = re.search(
        r"\{.*\}",
        text,
        re.S
    )


    if not match:

        print("\n❌ NO JSON FOUND")

        raise Exception(
            f"No JSON found:\n{text}"
        )


    policy = json.loads(
        match.group()
    )


    print("\n" + "=" * 70)
    print("GENERATED PERSONALIZED POLICY")
    print("=" * 70)

    print(policy)

    print("=" * 70)



    return policy


def generate_policy_without_rag(patient):
    """Generate the evaluation baseline without retrieving guideline context."""
    prompt = f"""
Patient:

Age: {patient['age']}
Condition: {patient['condition']}

No retrieved medical guidelines are available. Generate personalized safe limits.
Return ONLY JSON.

Example:

{{
   "parameter":"systolic_bp",
   "min":110,
   "max":135
}}
"""
    client = ollama.Client(
        host=OLLAMA_HOST,
        timeout=OLLAMA_TIMEOUT
    )
    response = client.chat(
        model="llama3",
        format="json",
        messages=[{"role": "user", "content": prompt}],
        options={
            "temperature": 0,
            "num_predict": OLLAMA_NUM_PREDICT
        },
    )
    match = re.search(r"\{.*\}", response["message"]["content"], re.S)
    if not match:
        raise ValueError("No JSON found in no-RAG baseline response")
    return json.loads(match.group())
