import { ArrowLeft, ExternalLink } from 'lucide-react'
import { SHEET_URL, SQL_FILES } from '../config'

export function Anexo() {
  const embed = SHEET_URL ? SHEET_URL.replace(/\/edit.*$/, '/htmlview') : ''
  return (
    <div className="max-w-[1200px] mx-auto px-4 sm:px-8 py-8">
      <a href="#/" className="inline-flex items-center gap-1 text-[13px]" style={{ color: 'var(--text-secondary)' }}>
        <ArrowLeft size={14} /> Inicio
      </a>
      <h1 className="text-[26px] font-semibold mt-4">Anexo · Cálculos</h1>
      <p className="mt-1 text-[14px]" style={{ color: 'var(--text-secondary)' }}>
        Google Sheet con tablas por case, supuestos y calidad de datos. La fuente de verdad es la SQL sobre Postgres.
      </p>
      <div className="card p-4 mt-5">
        {SHEET_URL ? (
          <>
            <a href={SHEET_URL} target="_blank" rel="noreferrer" className="chip">
              <ExternalLink size={14} /> Abrir Google Sheet
            </a>
            <iframe title="Google Sheet del anexo" src={embed} className="w-full mt-4 rounded-[8px]" style={{ height: '70vh', border: '1px solid var(--border)' }} />
          </>
        ) : (
          <p style={{ color: 'var(--text-muted)' }}>Google Sheet pendiente.</p>
        )}
      </div>
      <div className="card p-4 mt-4">
        <div className="text-[14px] font-semibold mb-2">Archivos SQL del repositorio</div>
        <ul className="text-[13px] space-y-1" style={{ color: 'var(--text-secondary)' }}>
          {SQL_FILES.map((f) => <li key={f}><code>{f}</code></li>)}
        </ul>
      </div>
    </div>
  )
}
