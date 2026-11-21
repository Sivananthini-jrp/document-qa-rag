import { useEffect, useState } from 'react'
import UploadPanel from './components/UploadPanel'
import ChatPanel from './components/ChatPanel'
import DocumentManager from './components/DocumentManager'
import { checkHealth } from './api'

export default function App() {
  const [online, setOnline] = useState(null)
  const [selectedDocs, setSelectedDocs] = useState([])
  const [refreshKey, setRefreshKey] = useState(0)

  useEffect(() => {
    let cancelled = false
    const probe = async () => {
      const ok = await checkHealth()
      if (!cancelled) setOnline(ok)
    }
    probe()
    const t = setInterval(probe, 15000)
    return () => { cancelled = true; clearInterval(t) }
  }, [])

  const handleUploadSuccess = () => setRefreshKey((k) => k + 1)

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1><span className="logo">📄</span> Document QA</h1>
          <p>Upload PDFs · Select · Ask questions</p>
        </div>
        <div className={`status-pill ${online === false ? 'offline' : ''}`}>
          <span className="status-dot" />
          {online === null ? 'Connecting…' : online ? 'Backend online' : 'Backend offline'}
        </div>
      </header>

      <UploadPanel onSuccess={handleUploadSuccess} />

      <section className="panel">
        <div className="panel-header">
          <div className="step">2</div>
          <h2>Select active documents</h2>
        </div>
        <div className="panel-body">
          <DocumentManager
            selected={selectedDocs}
            onChange={setSelectedDocs}
            onRefreshTrigger={refreshKey}
          />
          <p style={{ marginTop: '12px', fontSize: '0.8rem', color: 'var(--text-faint)' }}>
            {selectedDocs.length === 0 
              ? "No boxes checked: AI will search across ALL documents." 
              : `AI will only search inside the ${selectedDocs.length} selected document(s).`}
          </p>
        </div>
      </section>

      <ChatPanel selectedDocs={selectedDocs} />

      <footer>Built with FastAPI · LangChain · FAISS · Groq · React</footer>
    </div>
  )
}