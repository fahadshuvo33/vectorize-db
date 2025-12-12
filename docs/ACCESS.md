# 🚀 VectorizeDB - Access Guide

## 🌐 Live URLs (Access from Browser)

### Frontend
**URL:** http://localhost:5173

- Main application interface
- Shows backend status
- Test chat functionality
- View project status

### Backend API
**URL:** http://localhost:8000

- Root endpoint with API information
- Returns service status and available endpoints

### Swagger API Documentation
**URL:** http://localhost:8000/docs

- Interactive API documentation
- Test all endpoints directly from browser
- See request/response schemas
- Try out API calls

### Alternative API Docs (ReDoc)
**URL:** http://localhost:8000/redoc

- Alternative documentation format
- Clean, readable API docs

### Health Check
**URL:** http://localhost:8000/health

- Detailed health status
- Service information
- Timestamp

## 📋 Available API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user

### File Upload
- `POST /api/v1/upload/` - Upload file
- `GET /api/v1/upload/` - List uploads

### Chat
- `POST /api/v1/chat/` - Send chat message
- `GET /api/v1/chat/sessions` - List chat sessions

## 🔍 Quick Test Commands

### Test Backend
```bash
curl http://localhost:8000/
```

### Test Health
```bash
curl http://localhost:8000/health
```

### Test Chat API
```bash
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

## 🐳 Docker Commands

### Check Service Status
```bash
docker compose ps
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
```

### Restart Services
```bash
docker compose restart
```

### Stop Services
```bash
docker compose down
```

### Start Services
```bash
docker compose up -d
```

## 📝 Notes

- All services use **host networking** to bypass Docker iptables issues
- Services are accessible directly on localhost
- Frontend automatically connects to backend on port 8000
- Hot-reload is enabled for both frontend and backend

## 🎯 Next Steps

1. Open http://localhost:5173 in your browser to see the frontend
2. Open http://localhost:8000/docs to explore the API
3. Test the chat functionality from the frontend
4. Try API calls from Swagger UI

