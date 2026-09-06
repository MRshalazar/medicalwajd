import requests
import time
import threading
import itertools
import re
import os


LANGGRAPH_URL = os.getenv("LANGGRAPH_URL", "http://127.0.0.1:8007")


# Timings include automated work only; time spent waiting for doctor input is not
# part of the total process time.
ACTION_TIMES = []


def record_action(action, start_time):
    """Record and return an action's elapsed time in seconds."""
    elapsed = time.perf_counter() - start_time
    ACTION_TIMES.append((action, elapsed))
    return elapsed


def print_timing_summary():
    """Display all recorded timings and their active processing total."""
    if not ACTION_TIMES:
        return

    total_time = sum(elapsed for _, elapsed in ACTION_TIMES)

    print("\n====================================================")
    print(" PROCESS TIMING")
    print("====================================================")
    for action, elapsed in ACTION_TIMES:
        print(f"{action}: {elapsed:.3f} seconds")
    print("----------------------------------------------------")
    print(f"Total process time: {total_time:.3f} seconds")
    print("====================================================")


# ====================================================
# Spinner
# ====================================================

def spinner(message, stop_event):

    for c in itertools.cycle(["|", "/", "-", "\\"]):

        if stop_event.is_set():
            break

        print(
            f"\r[{c}] {message}",
            end="",
            flush=True
        )

        time.sleep(0.1)

    print("\r", end="")


def process_stage(message, duration=1.2):

    start_time = time.perf_counter()

    stop = threading.Event()

    t = threading.Thread(
        target=spinner,
        args=(message, stop)
    )

    t.start()

    time.sleep(duration)

    stop.set()
    t.join()

    record_action(message, start_time)

    print(f"[✓] {message}")


# ====================================================
# Get Patients
# ====================================================

def get_patients():

    start_time = time.perf_counter()

    # Temporary list
    # Later you can replace this with:
    #
    # requests.get(
    #   "http://127.0.0.1:8005/patients"
    # )

    patients = [
        "10007795",
        "10007928",
        "10009628",
        "10011398",

        
    ]

    record_action("Loading available patients", start_time)
    return patients


# ====================================================
# Main
# ====================================================

def main():

    ACTION_TIMES.clear()

    os.system(
        "cls" if os.name == "nt"
        else "clear"
    )

    print("""
====================================================
 Privacy Preserving CDSS - Doctor Console
====================================================
""")

    process_stage(
        "Connecting to hospital system..."
    )

    patients = get_patients()

    print("\nAvailable Patients:")
    print("-----------------------------")

    for p in patients:
        print("-", p)

    print("-----------------------------")

    query = input(
        "\nDoctor query:\n> "
    )

    # extract patient id
    patient_id_start_time = time.perf_counter()
    match = re.search(
        r"\d+",
        query
    )
    record_action("Extracting patient ID", patient_id_start_time)

    if not match:

        print(
            "\nNo patient ID detected."
        )

        return

    patient_id = match.group()

    print()

    # ====================================================
    # Visual pipeline
    # ====================================================

    process_stage(
        "Checking patient information..."
    )

    process_stage(
        "Searching medical knowledge base (RAG)..."
    )

    process_stage(
        "Generating personalized clinical ranges..."
    )

    process_stage(
        "Sending policy to IoMT device..."
    )

    process_stage(
        "Generating Zero-Knowledge Proof..."
    )

    process_stage(
        "Verifying Bulletproof proof..."
    )

    process_stage(
        "Generating clinical decision..."
    )

# ====================================================
# Call LangGraph
# ====================================================

    try:

        print("\n[DEBUG] Sending request to LangGraph...")
        print(
            f"[DEBUG] URL: "
            f"{LANGGRAPH_URL}/run/{patient_id}"
        )

        request_start_time = time.perf_counter()
        try:
            response = requests.get(
                f"{LANGGRAPH_URL}/run/{patient_id}",
                timeout=240
            )
        finally:
            record_action("LangGraph request", request_start_time)

        print("\n==============================")
        print("LANGGRAPH RESPONSE")
        print("==============================")

        print("Status Code:")
        print(response.status_code)

        print("\nHeaders:")
        print(response.headers)

        print("\nRaw Content:")
        print(response.text)

        if response.status_code != 200:

            print("\n❌ LANGGRAPH FAILED")

            print(
                "\nGo check these terminals:"
            )

            print(
                "1) LangGraph Coordinator :8007"
            )

            print(
                "2) Patient MCP :8005"
            )

            print(
                "3) Rule Engine :8004"
            )

            print(
                "4) Knowledge MCP :8010"
            )

            print(
                "5) Privacy MCP :8003"
            )

            return

        try:

            response_parse_start_time = time.perf_counter()
            result = response.json()
            record_action(
                "Parsing LangGraph response",
                response_parse_start_time
            )

        except Exception as json_error:

            record_action(
                "Parsing LangGraph response",
                response_parse_start_time
            )

            print(
                "\n❌ JSON PARSE ERROR"
            )

            print(
                "Exception:"
            )

            print(json_error)

            print(
                "\nResponse text:"
            )

            print(response.text)

            return

    except requests.exceptions.ConnectionError as e:

        print(
            "\n❌ CONNECTION ERROR"
        )

        print(e)

        print(
            "\nLangGraph service may not be running."
        )

        return


    except requests.exceptions.Timeout as e:

        print(
            "\n❌ REQUEST TIMEOUT"
        )

        print(e)

        return


    except Exception as e:

        print(
            "\n❌ UNKNOWN ERROR"
        )

        print(type(e))

        print(e)

        return
    # ====================================================
    # Final Report
    # ====================================================

    report_start_time = time.perf_counter()

    patient = result.get(
        "patient",
        {}
    )

    policy = result.get(
        "policy",
        {}
    )

    proof = result.get(
        "proof",
        {}
    )

    decision = result.get(
        "decision",
        {}
    )

    print("""

====================================================
 CLINICAL DECISION REPORT
====================================================
""")

    print(
        "Patient ID:",
        result.get("patient_id")
    )

    print(
        "Gender:",
        patient.get("gender")
    )

    print(
        "Age:",
        patient.get("age")
    )

    print(
        "Condition:",
        patient.get("condition")
    )

    print("\nPersonalized Range:")

    print(
        f"{policy.get('min')} "
        f"- "
        f"{policy.get('max')} "
        f"{policy.get('parameter', '')}"
    )

    print("\nSensor Value:")
    print("🔒 PRIVATE")

    

    if proof.get("verified"):
        print("TRUE ✅")
    else:
        print("FALSE ❌")

    print("\nFinal Decision:")

    if decision.get("stable"):

        print(
            decision.get(
                "message",
                "Patient is clinically stable."
            ),
            "✅"
        )

    else:

        print(
            decision.get(
                "message",
                "Patient requires attention."
            ),
            "⚠️"
        )

    print("""
====================================================
""")

    record_action("Generating clinical decision report", report_start_time)


if __name__ == "__main__":
    try:
        main()
    finally:
        print_timing_summary()
