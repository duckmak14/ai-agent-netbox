# Netbox MCP Server

A powerful integration server that combines Netbox's network infrastructure management capabilities with MCP (Multi-Cloud Platform) functionality. 

## Installation

### Option 1: Local Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/netbox-mcp.git
cd netbox-mcp
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
Create a `.env` file in the project root with the following variables:
```
NETBOX_URL=your_netbox_url
NETBOX_TOKEN=your_api_token
```
5. Start the server:
```bash
python server.py
```

6. Access the application at `http://localhost:8000`

### Option 2: Docker Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/netbox-mcp.git
cd netbox-mcp
```

2. Configure environment variables:
Create a `.env` file in the project root with the following variables:
```
NETBOX_URL=your_netbox_url
NETBOX_TOKEN=your_api_token
```

3. Build and run with Docker Compose:
```bash
# Build and start the container in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

4. Access the application at `http://localhost:8000`
