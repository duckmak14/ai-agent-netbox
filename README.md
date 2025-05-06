# Agent Netbox

## Prerequisites
- Docker
- Docker Compose

## Running the Application

1. Clone the repository:
```bash
git clone https://github.com/duckmak14/ai-agent-netbox.git
cd ai-agent-netbox
```

2. Run the application using Docker Compose:

```markdown
**Note:** Starting from Docker Compose version 2.0, use the `docker compose` command. For older versions, use `docker-compose`.
```

```bash
docker compose up -d
```

```markdown
**Note:** For older versions, use `docker-compose`.
```

```bash
docker-compose up -d
```

This command will:
- Build the Docker image with tag `agent-netbox:latest`
- Start the container in detached mode
- The application will be accessible at `http://localhost:8501`

## Environment Variables
The application uses the following environment variables:
- `STREAMLIT_SERVER_ADDRESS`: Set to `0.0.0.0` to allow external access 