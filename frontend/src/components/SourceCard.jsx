import { useState } from 'react'

export default function SourceCard({ src }) {
  const [open, setOpen] = useState(false)

  if (!src?.length) return null

  return (
    <div className="sources">
      <button className="sources-toggle" onClick={() => setOpen((o) => !o)}>
        {open ? '▾' : '▸'} {src.length} source{src.length > 1 ? 's' : ''}
      </button>

      {open &&
        src.map((s, i) => {
          const pct = Math.max(0, Math.min(100, Math.round(s.score * 100)))
          return (
            <div className="source" key={i}>
              <div className="source-head">
                <span className="source-badge">[{i + 1}]</span>
                <span className="source-name" title={s.source}>{s.source}</span>
                <span className="source-score">
                  <span className="score-bar"><span className="score-fill" style={{ width: `${pct}%` }} /></span>
                  {s.score.toFixed(2)}
                </span>
              </div>
              <p className="source-text">{s.text}…</p>
            </div>
          )
        })}
    </div>
  )
}