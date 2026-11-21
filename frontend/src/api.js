const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function uploadPdfs(files) {
  const fd = new FormData()
  for (const f of files) fd.append('files', f)
  const r = await fetch(`${API}/upload`, { method: 'POST', body: fd })
  if (!r.ok) throw new Error('Upload failed')
  return r.json()
}

export async function askQuestion(question, allowedSources = null) {
  const r = await fetch(`${API}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, allowed_sources: allowedSources }),
  })
  if (!r.ok) throw new Error('Ask failed')
  return r.json()
}

export async function fetchDocuments() {
  const r = await fetch(`${API}/documents`)
  if (!r.ok) throw new Error('Failed to fetch documents')
  return r.json()
}

export async function deleteDocument(filename) {
  const r = await fetch(`${API}/documents/${encodeURIComponent(filename)}`, {
    method: 'DELETE',
  })
  if (!r.ok) throw new Error('Failed to delete document')
  return r.json()
}

export async function checkHealth() {
  try {
    const r = await fetch(`${API}/health`)
    return r.ok
  } catch {
    return false
  }
}