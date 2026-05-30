# Python Code Runner

A secure, full-stack online Python code execution platform built with React and FastAPI. Code runs in isolated Docker containers for maximum security.

## Features

- **Monaco Editor** with Python syntax highlighting
- **Dark theme** UI inspired by Replit/CodeSandbox
- **Docker sandboxing** for secure code execution
- **Rate limiting** (10 requests/minute per IP)
- **Execution limits**: 5s timeout, 64MB memory, 0.5 CPU
- **Real-time output** with stdout/stderr differentiation

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────┐
│   Frontend  │────▶│   Backend   │────▶│  Docker Container│
│   (React)   │◀────│  (FastAPI)  │◀────│  (python:3.11)  │
│   Port 3000 │     │   Port 8000 │     │   Sandbox       │
└─────────────┘     └─────────────┘     └─────────────────┘
```

<img width="1909" height="837" alt="image" src="https://github.com/user-attachments/assets/937a29cf-bd22-4a86-98aa-129e2eb044c6" />


## Prerequisites

- **Docker** (latest version)
- **Docker Compose** (v2+)

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/bountyhunter12/python-code-runner.git
cd python-code-runner
```

### 2. Start with Docker Compose

```bash
docker-compose up --build
```

### 3. Access the application

Open your browser and navigate to:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Security Features

| Constraint | Value |
|------------|-------|
| Network | `none` (isolated) |
| Memory | 64MB |
| CPU | 0.5 cores |
| Filesystem | Read-only |
| User | `nobody` (UID 65534) |
| Capabilities | All dropped |
| Timeout | 5 seconds |
| Max code length | 10,000 chars |

### Restricted Imports

The following modules/patterns are blocked:
- `os`, `sys`, `subprocess`
- `eval()`, `exec()`
- `__import__()`
- `open()`, `socket`
- `requests`, `urllib`
- `ctypes`, `popen`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PYTHONUNBUFFERED` | `1` | Unbuffered Python output |

## Development

### Run locally (without Docker)

#### Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Reference

### Run Code

**POST** `/api/run`

Request:
```json
{
  "code": "print('Hello, World!')"
}
```

Response:
```json
{
  "stdout": "Hello, World!\n",
  "stderr": "",
  "exit_code": 0,
  "time_ms": 123
}
```

### Health Check

**GET** `/health`

## Rate Limiting

- **Limit**: 10 requests per minute per IP
- **Exceeded response**: HTTP 429

## Project Structure

```
python-code-runner/
├── backend/
│   ├── main.py          # FastAPI application
│   ├── requirements.txt # Python dependencies
│   └── Dockerfile       # Backend container
├── frontend/
│   ├── src/
│   │   ├── App.jsx      # Main React component
│   │   ├── main.jsx     # Entry point
│   │   └── index.css    # Styling
│   ├── index.html       # HTML template
│   ├── package.json     # Node dependencies
│   ├── vite.config.js   # Vite configuration
│   ├── nginx.conf       # Nginx config for production
│   └── Dockerfile       # Frontend container
├── docker-compose.yml   # Multi-container setup
└── README.md            # This file
```

## Troubleshooting

### Docker socket permission denied

If you encounter permission issues with the Docker socket:

```bash
# Linux: Add your user to docker group
sudo usermod -aG docker $USER
# Log out and back in for changes to take effect
```

### Container won't start

Check Docker is running:
```bash
docker info
```

### Code execution fails

Ensure Docker can pull the `python:3.11-slim` image:
```bash
docker pull python:3.11-slim
```

## License

MIT License
