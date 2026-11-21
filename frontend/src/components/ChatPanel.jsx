import { useRef, useState, useEffect } from 'react'
import { askQuestion } from '../api'
import SourceCard from './SourceCard'

export default function ChatPanel({ selectedDocs }) {
  const [q, setQ] = useState('')
  const [log, setLog] = useState([])
  const [busy, setBusy] = useState(false)
  const scrollRef = useRef(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [log, busy])

  const send = async (e) => {
    e.preventDefault()
    const question = q.trim()
    if (!question || busy) return
    setQ('')
    setBusy(true)
    setLog((l) => [...l, { role: 'user', text: question }])
    
    try {
      const filter = selectedDocs.length > 0 ? selectedDocs : null
      const res = await askQuestion(question, filter)
      setLog((l) => [...l, { role: 'ai', text: res.answer, sources: res.sources }])
    } catch (err) {
      setLog((l) => [...l, { role: 'ai', text: '⚠ ' + err.message, sources: [] }])
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="panel">
      <div className="panel-header">
        <div className="step">3</div>
        <h2>Ask your documents</h2>
      </div>

      <div className="panel-body">
        <div className="chat-scroll" ref={scrollRef}>
          {log.length === 0 && !busy && (
            <div className="empty-state">
              <span className="emoji">💬</span>
              <p>Ask anything about the selected documents.</p>
            </div>
          )}
          {log.map((m, i) => (
            <div key={i} className={`msg ${m.role}`}>
              <div className="avatar">{m.role === 'user' ? 'You' : 'AI'}</div>
              <div className="msg-content">
                <div className="bubble">{m.text}</div>
                {m.sources?.length > 0 && <SourceCard src={m.sources} />}
              </div>
            </div>
          ))}
          {busy && (
            <div className="msg ai">
              <div className="avatar">AI</div>
              <div className="msg-content">
                <div className="bubble">
                  <span className="thinking"><span /><span /><span /></span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      <form className="input-bar" onSubmit={send}>
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder={selectedDocs.length > 0 ? `Ask about ${selectedDocs.length} selected doc(s)…` : "Ask anything..."}
          disabled={busy}
        />
        <button className="btn-send" disabled={busy || !q.trim()}>Ask →</button>
      </form>
    </section>
  )
}