import { BackButton } from '../components/BackButton'
import { ExternalLink, Github } from 'lucide-react'
import { CODE_FILES, REPO_URL, SHEET_URL, SQL_FILES } from '../config'

export function Anexo() {
  const embed = SHEET_URL ? SHEET_URL.replace(/\/edit.*$/, '/htmlview') : ''
  return (
    <div className="max-w-[1200px] mx-auto px-4 sm:px-8 py-8">
      <BackButton />
      <h1 className="text-[26px] font-semibold mt-4">Anexo · Cálculos</h1>
      <p className="mt-1 text-[14px]" style={{ color: 'var(--text-secondary)' }}>
        Google Sheet con tablas por case, supuestos y calidad de datos. Las cifras salen de las queries SQL enlazadas abajo.
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
      {[
        { title: 'Queries SQL (GitHub)', files: SQL_FILES },
        { title: 'Código de verificación y modelos (GitHub)', files: CODE_FILES },
      ].map((g) => (
        <div key={g.title} className="card p-4 mt-4">
          <div className="flex items-center justify-between mb-3">
            <div className="text-[14px] font-semibold">{g.title}</div>
            <a href={REPO_URL} target="_blank" rel="noreferrer" className="chip"><Github size={14} /> Repositorio</a>
          </div>
          <ul className="space-y-2">
            {g.files.map((f) => (
              <li key={f.file}>
                <a href={f.url} target="_blank" rel="noreferrer" className="file-link">
                  <code>{f.file}</code>
                  <span>{f.desc}</span>
                  <ExternalLink size={13} />
                </a>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  )
}
