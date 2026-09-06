import os
import sys

import requests


def main() -> None:
    patient_id = sys.argv[1] if len(sys.argv) > 1 else "10009628"
    base_url = os.getenv("LANGGRAPH_URL", "http://127.0.0.1:8007")
    url = f"{base_url}/run/{patient_id}"

    response = requests.get(url, timeout=180)
    response.raise_for_status()

    print(response.json())


if __name__ == "__main__":
    main()