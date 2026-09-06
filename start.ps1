$root = "D:\9raya\memoire 2026\Privacy-Preserving-CDSS"

Start-Process powershell -ArgumentList "-NoExit","-Command",
"cd '$root'; .\backend\.venv\Scripts\Activate.ps1; uvicorn patient_mcp.app:app --reload --port 8005"

Start-Process powershell -ArgumentList "-NoExit","-Command",
"cd '$root'; .\backend\.venv\Scripts\activate; `$env:OLLAMA_HOST='http://127.0.0.1:11434'; uvicorn rule_engine.app:app --reload --port 8004"
Start-Process powershell -ArgumentList "-NoExit","-Command",
"cd '$root'; .\backend\.venv\Scripts\Activate.ps1; uvicorn privacy_mcp.app:app --reload --port 8003"

Start-Process powershell -ArgumentList "-NoExit","-Command",
"cd '$root'; .\backend\.venv\Scripts\Activate.ps1; uvicorn decision_engine.app:app --reload --port 8002"

Start-Process powershell -ArgumentList "-NoExit","-Command",
"cd '$root'; .\backend\.venv\Scripts\Activate.ps1; `$env:OLLAMA_HOST='http://127.0.0.1:11434'; uvicorn knowledge_mcp.app:app --reload --port 8010"

Start-Process powershell -ArgumentList "-NoExit","-Command",
"cd '$root'; .\backend\.venv\Scripts\Activate.ps1; uvicorn langgraph_coordinator.app:app --reload --port 8007"