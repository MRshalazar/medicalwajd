#!/usr/bin/env bash
# filepath: /home/ladida/Downloads/A-secure-medical-monitoring-decision-support-system--main/run.sh

set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$ROOT/backend/.venv"
PYTHON="$VENV/bin/python"
LOG_DIR="$ROOT/logs"

echo "===================================================="
echo "  Privacy Preserving CDSS - System Startup"
echo "===================================================="

if [[ ! -d "$ROOT" ]]; then
    echo "[ERROR] Project folder not found: $ROOT"
    exit 1
fi

if [[ ! -x "$PYTHON" ]]; then
    echo "[ERROR] Python virtual environment not found."
    echo "Create it with:"
    echo "  cd \"$ROOT/backend\""
    echo "  python3 -m venv .venv"
    echo "  \"$VENV/bin/pip\" install -r \"$ROOT/requirements-linux.txt\""
    exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
    echo "[ERROR] curl is required. Install it with:"
    echo "  sudo apt install curl"
    exit 1
fi

mkdir -p "$LOG_DIR"

echo "[OK] Project found"
echo "[OK] Python virtual environment found"

echo
echo "Checking Ollama..."

if curl -fsS --max-time 3 http://127.0.0.1:11434/api/tags >/dev/null; then
    echo "[OK] Ollama is running"
else
    if ! command -v ollama >/dev/null 2>&1; then
        echo "[ERROR] Ollama is not installed."
        exit 1
    fi

    echo "Starting Ollama..."
    nohup ollama serve >"$LOG_DIR/ollama.log" 2>&1 &

    for _ in {1..20}; do
        sleep 1
        if curl -fsS --max-time 2 \
            http://127.0.0.1:11434/api/tags >/dev/null; then
            break
        fi
    done

    if ! curl -fsS --max-time 2 \
        http://127.0.0.1:11434/api/tags >/dev/null; then
        echo "[ERROR] Ollama could not be started."
        cat "$LOG_DIR/ollama.log"
        exit 1
    fi

    echo "[OK] Ollama started"
fi

echo
echo "Checking Ollama models..."

MODELS="$(curl -fsS http://127.0.0.1:11434/api/tags)"

if echo "$MODELS" | grep -q '"name":"llama3'; then
    echo "[OK] llama3 found"
else
    echo "[WARNING] llama3 not found. Run: ollama pull llama3"
fi

if echo "$MODELS" | grep -q '"name":"nomic-embed-text'; then
    echo "[OK] nomic-embed-text found"
else
    echo "[ERROR] nomic-embed-text not found."
    echo "Run: ollama pull nomic-embed-text"
    exit 1
fi

echo
echo "Checking optional components..."

if [[ -x "$ROOT/zkp_engine/target/release/zkp_engine" ]]; then
    echo "[OK] ZKP engine found"
else
    echo "[WARNING] ZKP engine not found."
    echo "Build it with:"
    echo "  cd \"$ROOT/zkp_engine\""
    echo "  cargo build --release"
fi

if [[ -d "$ROOT/knowledge_mcp/chroma_db" ]]; then
    echo "[OK] ChromaDB found"
else
    echo "[WARNING] ChromaDB directory not found"
fi

test_port() {
    (echo >/dev/tcp/127.0.0.1/"$1") >/dev/null 2>&1
}

stop_existing_services() {
    local stopped=false

    for port in 8002 8003 8004 8005 8007 8010; do
        for pid in $(fuser -n tcp "$port" 2>/dev/null || true); do
            if [[ ! "$pid" =~ ^[0-9]+$ ]]; then
                continue
            fi

            local command_line
            command_line="$(ps -p "$pid" -o args= 2>/dev/null || true)"

            if [[ "$command_line" == *uvicorn* && "$command_line" == *app:app* ]]; then
                echo "[INFO] Stopping existing CDSS service (PID $pid) on port $port"
                kill "$pid" 2>/dev/null || true
                stopped=true
            else
                echo "[ERROR] Port $port is occupied by an unrelated process."
                exit 1
            fi
        done
    done

    if [[ "$stopped" == true ]]; then
        for _ in {1..10}; do
            local ports_busy=false
            for port in 8002 8003 8004 8005 8007 8010; do
                if test_port "$port"; then
                    ports_busy=true
                    break
                fi
            done

            if [[ "$ports_busy" == false ]]; then
                break
            fi
            sleep 1
        done
    fi

    for port in 8002 8003 8004 8005 8007 8010; do
        if test_port "$port"; then
            echo "[ERROR] CDSS port $port is still in use."
            exit 1
        fi
    done
}

wait_for_port() {
    local port="$1"
    local name="$2"

    echo "Waiting for $name on port $port..."

    for _ in {1..30}; do
        if test_port "$port"; then
            echo "[OK] $name is running"
            return 0
        fi
        sleep 1
    done

    echo "[ERROR] $name failed to start"
    return 1
}

start_service() {
    local name="$1"
    local module="$2"
    local port="$3"
    local log_file="$LOG_DIR/${name}.log"

    echo "Starting $name on port $port..."

    (
        cd "$ROOT" || exit 1
        nohup "$PYTHON" -m uvicorn "$module:app" \
            --port "$port"
    ) >"$log_file" 2>&1 &

    echo $! >"$LOG_DIR/${name}.pid"
}

echo
echo "===================================================="
echo "  Starting CDSS Services"
echo "===================================================="

stop_existing_services

start_service "patient_mcp" "patient_mcp.app" 8005

(
    cd "$ROOT" || exit 1
    OLLAMA_HOST="http://127.0.0.1:11434" \
        nohup "$PYTHON" -m uvicorn rule_engine.app:app --port 8004
) >"$LOG_DIR/rule_engine.log" 2>&1 &
echo $! >"$LOG_DIR/rule_engine.pid"

start_service "privacy_mcp" "privacy_mcp.app" 8003
start_service "decision_engine" "decision_engine.app" 8002

(
    cd "$ROOT" || exit 1
    OLLAMA_BASE_URL="http://127.0.0.1:11434" \
        nohup "$PYTHON" -m uvicorn knowledge_mcp.app:app --port 8010
) >"$LOG_DIR/knowledge_mcp.log" 2>&1 &
echo $! >"$LOG_DIR/knowledge_mcp.pid"

start_service "langgraph_coordinator" "langgraph_coordinator.app" 8007

echo
echo "Waiting for services..."

all_ready=true

wait_for_port 8005 "Patient MCP" || all_ready=false
wait_for_port 8004 "Rule Engine" || all_ready=false
wait_for_port 8003 "Privacy MCP" || all_ready=false
wait_for_port 8002 "Decision Engine" || all_ready=false
wait_for_port 8010 "Knowledge MCP" || all_ready=false
wait_for_port 8007 "LangGraph Coordinator" || all_ready=false

if [[ "$all_ready" != true ]]; then
    echo
    echo "[ERROR] System startup failed."
    echo "Check logs in: $LOG_DIR"
    exit 1
fi

echo
echo "===================================================="
echo "  ALL CDSS SERVICES ARE RUNNING"
echo "===================================================="
cd "$ROOT" || exit 1
exec "$PYTHON" "$ROOT/doctor_console.py"