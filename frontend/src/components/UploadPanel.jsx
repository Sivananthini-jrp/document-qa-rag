import { useRef, useState } from 'react'
import { uploadPdfs } from '../api'

export default function UploadPanel({ onSuccess }) {
  const [busy, setBusy] = useState(false)
  const [info, setInfo] = useState(null)
  const [dragover, setDragover] = useState(false)
  const inputRef = useRef(null)

  const process = async (files) => {
    const pdfs = files.filter((f) => f.name.toLowerCase().endsWith('.pdf'))
    if (!pdfs.length) {
      setInfo({ error: 'Please select PDF files only.' })
      return
    }
    setBusy(true)
    setInfo(null)
    try {
      const res = await uploadPdfs(pdfs)
      setInfo(res)
      if (onSuccess) onSuccess()
    } catch (err) {
      setInfo({ error: err.message })
    } finally {
      setBusy(false)
    }
  }

  const onDrop = (e) => {
    e.preventDefault()
    setDragover(false)
    if (e.dataTransfer.files?.length) process(Array.from(e.dataTransfer.files))
  }

  return (
    <section className="panel">
      <div className="panel-header">
        <div className="step">1</div>
        <h2>Upload documents</h2>
      </div>
      <div className="panel-body">
        <div
          className={`dropzone ${dragover ? 'dragover' : ''}`}
          onClick={() => inputRef.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setDragover(true) }}
          onDragLeave={() => setDragover(false)}
          onDrop={onDrop}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".pdf"
            multiple
            onChange={(e) => e.target.files?.length && process(Array.from(e.target.files))}
          />
          <span className="dz-icon">📂</span>
          <div className="dz-title">Drop PDFs here or click to browse</div>
          <div className="dz-hint">Multiple files supported · .pdf only</div>
        </div>

        {busy && <div className="progress" />}

        {info && !info.error && (
          <div className="banner ok">
            ✓ Indexed {info.documents} document{info.documents > 1 ? 's' : ''} ({info.chunks} chunks)
          </div>
        )}
        {info?.error && <div className="banner err">✕ {info.error}</div>}
      </div>
    </section>
  )
}