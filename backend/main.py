import time
import re
import base64
import docker as docker_sdk
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

MAX_CODE_LENGTH = 10000
MAX_TIMEOUT_SECONDS = 5
DOCKER_MEMORY = "64m"
DOCKER_CPUS = "0.5"
RATE_LIMIT_REQUESTS = 10
RATE_LIMIT_WINDOW_SECONDS = 60

class RateLimiter:
    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
    def is_allowed(self, client_ip):
        now = datetime.now()
        window_start = now - timedelta(seconds=self.window_seconds)
        self.requests[client_ip] = [ts for ts in self.requests[client_ip] if ts > window_start]
        if len(self.requests[client_ip]) >= self.max_requests:
            return False, 0
        self.requests[client_ip].append(now)
        return True, self.max_requests - len(self.requests[client_ip])

rate_limiter = RateLimiter(RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW_SECONDS)

class RunCodeRequest(BaseModel):
    code: str

class RunCodeResponse(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    time_ms: int

app = FastAPI(title="Python Code Runner API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def validate_code(code):
    if not code or not code.strip():
        return False, "Code cannot be empty"
    if len(code) > MAX_CODE_LENGTH:
        return False, f"Code exceeds maximum length of {MAX_CODE_LENGTH} characters"
    dangerous_patterns = [
        r'import\s+os', r'from\s+os\s+import',
        r'import\s+sys', r'from\s+sys\s+import',
        r'subprocess', r'__import__',
        r'open\s*\(', r'socket', r'requests',
        r'urllib', r'ctypes', r'popen', r'spawn',
    ]
    for pattern in dangerous_patterns:
        if re.search(pattern, code):
            return False, f"Code contains restricted pattern: {pattern}"
    return True, ""

def execute_in_docker(code):
    start_time = time.time()
    try:
        client = docker_sdk.from_env()
        encoded = base64.b64encode(code.encode()).decode()
        cmd = f"import base64; exec(base64.b64decode('{encoded}').decode())"
        logs = client.containers.run(
            "python:3.11-slim",
            command=["python", "-u", "-c", cmd],
            remove=True,
            network_disabled=True,
            mem_limit=DOCKER_MEMORY,
            nano_cpus=int(float(DOCKER_CPUS) * 1e9),
            read_only=True,
            user="65534",
            cap_drop=["ALL"],
            security_opt=["no-new-privileges"],
            pids_limit=50,
            stdout=True,
            stderr=True,
            detach=False,
        )
        elapsed_ms = int((time.time() - start_time) * 1000)
        output = logs.decode() if isinstance(logs, bytes) else str(logs)
        return output, "", 0, elapsed_ms
    except docker_sdk.errors.ContainerError as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        err = e.stderr.decode() if isinstance(e.stderr, bytes) else str(e.stderr)
        return "", err, 1, elapsed_ms
    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        return "", f"Execution error: {str(e)}", 1, elapsed_ms

def check_docker_available():
    try:
        client = docker_sdk.from_env()
        client.ping()
        return True
    except Exception:
        return False

@app.get("/")
async def root():
    return {"status": "ok", "service": "Python Code Runner API"}

@app.get("/health")
async def health():
    return {"status": "healthy", "docker_available": check_docker_available()}

@app.post("/api/run", response_model=RunCodeResponse)
async def run_code(request: Request, body: RunCodeRequest):
    client_ip = request.client.host if request.client else "unknown"
    allowed, remaining = rate_limiter.is_allowed(client_ip)
    if not allowed:
        raise HTTPException(status_code=429, detail={"error": "Rate limit exceeded"})
    valid, error_msg = validate_code(body.code)
    if not valid:
        raise HTTPException(status_code=400, detail={"error": "Invalid code", "message": error_msg})
    stdout, stderr, exit_code, time_ms = execute_in_docker(body.code)
    return RunCodeResponse(stdout=stdout, stderr=stderr, exit_code=exit_code, time_ms=time_ms)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": "Internal server error", "message": str(exc)})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
