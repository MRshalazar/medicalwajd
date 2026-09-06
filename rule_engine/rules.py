import ollama

def build_policy(patient, guideline_text):

    prompt = f"""
    Patient:
    {patient}

    Guidelines:
    {guideline_text}

    Generate monitoring ranges for:
    - blood pressure
    - heart rate
    - spo2
    - temperature

    Return ONLY JSON.
    """

    response = ollama.chat(
        model="llama3",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response["message"]["content"]


def validate_policy(policy):

    return policy