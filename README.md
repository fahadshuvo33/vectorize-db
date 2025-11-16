# DBMelt

Turn databases into AI-ready formats with a live chatbot preview.

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- BuildKit enabled (usually enabled by default in Docker 20.10+)

### Running the Application

**Important**: Make sure BuildKit is enabled for optimal caching:
```bash
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
```

Or add to your `~/.bashrc` or `~/.zshrc`:
```bash
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
```

Check your BuildKit setup:
```bash
./check-buildkit.sh
```

**Optional**: Pre-pull base images to ensure they're cached (recommended for first-time setup):
```bash
./prepull-images.sh
```

1. Start all services:
```bash
docker-compose up --build
```

**Note**: 
- The **first build** will download base images (Python, Node) and all dependencies - this is normal and only happens once
- **Subsequent builds** will use cached layers:
  - Base images (python:3.14-slim, node:25-alpine) are cached by Docker
  - System packages (apt) are cached via BuildKit cache mounts
  - Python packages (pip) are cached via BuildKit cache mounts  
  - NPM packages are cached via BuildKit cache mounts
- Only layers that change will be rebuilt (e.g., if you modify `requirements.txt` or `package.json`)

**⚠️ Networking Issue**: If you see iptables errors, see `NETWORKING-FIX.md` for solutions. Port mappings are temporarily disabled but containers can still communicate internally.

2. Access the application:
   - **Frontend:** http://localhost:5173 (Main UI)
   - **Backend API:** http://localhost:8000 (Root endpoint)
   - **Swagger Docs:** http://localhost:8000/docs (Interactive API testing)
   - **ReDoc:** http://localhost:8000/redoc (Alternative docs)
   - **Health Check:** http://localhost:8000/health

   See `ACCESS.md` for detailed access information and API endpoints.

### Services

- **Frontend**: React app running on port 5173
- **Backend**: FastAPI server running on port 8000
- **PostgreSQL**: Database on port 5432 (local dev only - production uses Supabase)
- **Redis**: Cache on port 6379

**Note**: pgAdmin is not included since you're using Supabase, which provides its own admin interface.

### Development

The setup includes hot-reload for both frontend and backend:
- Frontend changes in `frontend/src/` will auto-reload
- Backend changes in `backend/app/` will auto-reload

### API Endpoints

- `GET /` - Health check
- `POST /api/v1/auth/register` - User registration (placeholder)
- `POST /api/v1/auth/login` - User login (placeholder)
- `GET /api/v1/auth/me` - Get current user (placeholder)
- `POST /api/v1/upload/` - Upload file (placeholder)
- `GET /api/v1/upload/` - List uploads (placeholder)
- `POST /api/v1/chat/` - Send chat message (placeholder)
- `GET /api/v1/chat/sessions` - List chat sessions (placeholder)

### Next Steps

The basic setup is complete. You can now:
1. Build out the authentication system
2. Implement file upload and processing
3. Add the chatbot functionality
4. Connect to the database for data persistence
