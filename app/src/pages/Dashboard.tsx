import { BackButton } from '../components/BackButton'
import { useEffect, useState } from 'react'
import type { CaseData } from '../types'
import { Chart } from '../components/Chart'
import { md } from '../deck/SlideRenderer'

const CASES = [
  { id: 'impulso', label: 'Impulso' },
  { id: 'conduce', label: 'Conduce' },
  { id: 'watts', label: 'Watts' },
]

export function Dashboard({ id }: { id: string }) {
  const [data, setData] = useState<CaseData | null>(null)
  const [err, setErr] = useState('')
  useEffect(() => {
    setData(null)
    setErr('')
    fetch(`/data/${id}.json`, { cache: 'no-cache' })
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then(setData)
      .catch(() => setErr('No se pudo cargar el JSON del dashboard.'))
  }, [id])

  return (
    <div className="max-w-[1200px] mx-auto px-4 sm:px-8 py-8">
      <div className="flex flex-wrap items-center gap-3">
        <BackButton />
        <div className="seg ml-auto">
          {CASES.map((c) => (
            <button key={c.id} aria-pressed={c.id === id} onClick={() => (location.hash = `#/dashboard/${c.id}`)}>
              {c.label}
            </button>
          ))}
        </div>
      </div>
      {err && <p className="mt-8" style={{ color: 'var(--critical)' }}>{err}</p>}
      {!data && !err && <p className="mt-8" style={{ color: 'var(--text-muted)' }}>Cargando…</p>}
      {data && (
        <>
          <h1 className="text-[26px] font-semibold mt-6">{data.title}</h1>
          <div className="card p-4 mt-3 text-[15px] leading-relaxed" style={{ borderLeft: '4px solid var(--accent)' }} dangerouslySetInnerHTML={{ __html: md(data.answer) }} />
          <div className="grid gap-3 mt-5" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))' }}>
            {data.kpis.map((k) => (
              <div key={k.label} className="card px-4 py-3">
                <div className="text-[12.5px]" style={{ color: 'var(--text-secondary)' }}>{k.label}</div>
                <div className="text-[24px] font-semibold tnum mt-0.5" style={{ color: k.tone === 'bad' ? 'var(--critical)' : k.tone === 'good' ? 'var(--accent)' : undefined }}>{k.value}</div>
                {k.sub && <div className="text-[12px]" style={{ color: 'var(--text-muted)' }}>{k.sub}</div>}
              </div>
            ))}
          </div>
          <div className="grid lg:grid-cols-2 gap-4 mt-5">
            {data.charts.map((c) => (
              <div key={c.id} className="card p-4">
                <div className="text-[14px] font-semibold mb-2">{c.title}</div>
                <Chart c={c} width={560} height={c.type === 'hbar' ? Math.max(220, c.x.length * 34 + 30) : 280} compact />
                {c.note && <div className="text-[12px] mt-2" style={{ color: 'var(--text-muted)' }}>{c.note}</div>}
              </div>
            ))}
          </div>
          {data.tables?.map((t, i) => (
            <div key={i} className="card p-4 mt-4 overflow-x-auto">
              {t.title && <div className="text-[14px] font-semibold mb-2">{t.title}</div>}
              <table className="data-table">
                <thead>
                  <tr>{t.columns.map((c) => <th key={c}>{c}</th>)}</tr>
                </thead>
                <tbody>
                  {t.rows.map((r, k) => (
                    <tr key={k}>{r.map((v, j) => <td key={j}>{typeof v === 'number' ? v.toLocaleString('es-MX') : v}</td>)}</tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
          {data.notes.length > 0 && (
            <div className="mt-5 rounded-[10px] p-4 text-[13px] leading-relaxed" style={{ background: 'var(--warning-bg)', color: 'var(--warning-ink)' }}>
              <div className="font-semibold mb-1">Notas, supuestos y calidad de datos</div>
              <ul className="list-disc pl-5 space-y-1">
                {data.notes.map((n, i) => <li key={i} dangerouslySetInnerHTML={{ __html: md(n) }} />)}
              </ul>
            </div>
          )}
        </>
      )}
    </div>
  )
}
