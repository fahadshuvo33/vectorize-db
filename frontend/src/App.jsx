import { useState, useEffect } from 'react'
import './App.css'

// Backend URLs - accessible from browser
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'

function App() {
  const [backendStatus, setBackendStatus] = useState('Checking...')
  const [backendInfo, setBackendInfo] = useState(null)
  const [message, setMessage] = useState('')
  const [chatResponse, setChatResponse] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  // Check backend status on mount
  useEffect(() => {
    checkBackend()
  }, [])

  const checkBackend = async () => {
    try {
      setIsLoading(true)
      setBackendStatus('Connecting...')
      const response = await fetch(`${BACKEND_URL}/`)
      const data = await response.json()
      setBackendInfo(data)
      setBackendStatus('✅ Connected')
    } catch (error) {
      setBackendStatus(`❌ Error: ${error.message}`)
      setBackendInfo(null)
    } finally {
      setIsLoading(false)
    }
  }

  const testChat = async () => {
    if (!message.trim()) return
    
    try {
      setIsLoading(true)
      const response = await fetch(`${API_URL}/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      })
      const data = await response.json()
      setChatResponse(data.response)
    } catch (error) {
      setChatResponse(`Error: ${error.message}`)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🔥 DBMelt</h1>
        <p className="subtitle">Turn databases into AI-ready formats</p>
        <div className="version-badge">v1.0.0</div>
      </header>

      <main className="app-main">
        {/* Backend Status Card */}
        <div className="card status-card">
          <div className="card-header">
            <h2>Backend Status</h2>
            <button 
              onClick={checkBackend} 
              className="btn btn-secondary"
              disabled={isLoading}
            >
              {isLoading ? 'Checking...' : 'Refresh'}
            </button>
          </div>
          <div className="status-content">
            <p className={`status-text ${backendStatus.includes('✅') ? 'success' : 'error'}`}>
              {backendStatus}
            </p>
            {backendInfo && (
              <div className="backend-info">
                <p><strong>Service:</strong> {backendInfo.service}</p>
                <p><strong>Version:</strong> {backendInfo.version}</p>
                <p><strong>Status:</strong> {backendInfo.status}</p>
                <div className="endpoints">
                  <strong>Available Endpoints:</strong>
                  <ul>
                    <li><a href={`${BACKEND_URL}/docs`} target="_blank" rel="noopener noreferrer">API Docs</a></li>
                    <li><a href={`${BACKEND_URL}/health`} target="_blank" rel="noopener noreferrer">Health Check</a></li>
                  </ul>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Chat Test Card */}
        <div className="card chat-card">
          <h2>Chat Test</h2>
          <p className="card-description">Test the chatbot API endpoint</p>
          <div className="chat-input-group">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type a message to test the API..."
              className="chat-input"
              onKeyPress={(e) => e.key === 'Enter' && !isLoading && testChat()}
              disabled={isLoading}
            />
            <button 
              onClick={testChat} 
              className="btn btn-primary"
              disabled={isLoading || !message.trim()}
            >
              {isLoading ? 'Sending...' : 'Send'}
            </button>
          </div>
          {chatResponse && (
            <div className="chat-response">
              <strong>Response:</strong>
              <p>{chatResponse}</p>
            </div>
          )}
        </div>

        {/* Info Card */}
        <div className="card info-card">
          <h2>Project Status</h2>
          <ul className="status-list">
            <li className="completed">✅ Backend server running</li>
            <li className="completed">✅ Frontend connected</li>
            <li className="pending">⏳ File upload functionality</li>
            <li className="pending">⏳ Database integration</li>
            <li className="pending">⏳ Chatbot implementation</li>
            <li className="pending">⏳ Vector embeddings</li>
            <li className="pending">⏳ RAG code generation</li>
          </ul>
        </div>

        {/* Ports Info */}
        <div className="card ports-card">
          <h2>Service Ports</h2>
          <div className="ports-info">
            <div className="port-item">
              <strong>Backend:</strong> Port 8000
              <span className="port-note">(FastAPI / Uvicorn)</span>
            </div>
            <div className="port-item">
              <strong>Frontend:</strong> Port 5173
              <span className="port-note">(Vite Dev Server)</span>
            </div>
            <div className="port-item">
              <strong>PostgreSQL:</strong> Port 5432
              <span className="port-note">(Database)</span>
            </div>
            <div className="port-item">
              <strong>Redis:</strong> Port 6379
              <span className="port-note">(Cache)</span>
            </div>
          </div>
          <p className="note">
            <strong>Note:</strong> If port mappings are disabled, access services via Docker network.
            Check <code>docker compose ps</code> for container status.
          </p>
        </div>
      </main>
    </div>
  )
}

export default App
