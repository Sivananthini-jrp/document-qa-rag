import { useEffect, useState } from 'react'
import { fetchDocuments, deleteDocument } from '../api'

export default function DocumentManager({ selected, onChange, onRefreshTrigger }) {
  const [docs, setDocs] = useState([])
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState(null)

  const loadDocs = async () => {
    setLoading(true)
    try {
      const data = await fetchDocuments()
      setDocs(data.documents || [])
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDocs()
  }, [onRefreshTrigger])

  const toggleDoc = (name) => {
    if (selected.includes(name)) {
      onChange(selected.filter((d) => d !== name))
    } else {
      onChange([...selected, name])
    }
  }

  const handleDelete = async (name) => {
    setDeleting(name)
    try {
      await deleteDocument(name)
      setDocs((d) => d.filter((x) => x !== name))
      onChange(selected.filter((s) => s !== name))
    } catch (err) {
      alert(err.message)
    } finally {
      setDeleting(null)
    }
  }

  if (loading) return <div style={{ color: 'var(--text-faint)' }}>Loading documents…</div>
  if (!docs.length) return <div style={{ color: 'var(--text-faint)', fontSize: '0.9rem' }}>No documents uploaded yet.</div>

  return (
    <div className="doc-list">
      {docs.map((name) => {
        const isSelected = selected.length === 0 || selected.includes(name)
        return (
          <div key={name} className={`doc-row ${isSelected ? 'active' : ''}`}>
            <label className="doc-checkbox">
              <input
                type="checkbox"
                checked={selected.length === 0 || selected.includes(name)}
                onChange={() => toggleDoc(name)}
              />
              <span className="doc-name">{name}</span>
            </label>
            <button
              className="btn-del"
              onClick={() => handleDelete(name)}
              disabled={deleting === name}
              title="Delete document"
            >
              {deleting === name ? '…' : '🗑'}
            </button>
          </div>
        )
      })}
    </div>
  )
}