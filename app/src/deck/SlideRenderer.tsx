import type { Kpi, Slide, Table } from '../types'
import { Chart } from '../components/Chart'

export const W = 1280
export const H = 720

function Kpis({ kpis }: { kpis: Kpi[] }) {
  return (
    <div className="grid gap-3" style={{ gridTemplateColumns: `repeat(${Math.min(kpis.length, 4)}, minmax(0,1fr))` }}>
      {kpis.map((k) => (
        <div key={k.label} className="rounded-[10px] px-4 py-3" style={{ background: '#f3f2ef' }}>
          <div className="text-[12.5px] leading-tight" style={{ color: '#52514e' }}>{k.label}</div>
          <div className="text-[28px] font-semibold tnum leading-tight mt-1" style={{ color: k.tone === 'bad' ? '#c0392b' : k.tone === 'good' ? '#0f8a6a' : '#0b0b0b' }}>{k.value}</div>
          {k.sub && <div className="text-[12px] leading-snug mt-0.5" style={{ color: '#898781' }}>{k.sub}</div>}
        </div>
      ))}
    </div>
  )
}

export function DeckTable({ t, large }: { t: Table; large?: boolean }) {
  return (
    <div>
      {t.title && <div className="text-[13px] font-semibold mb-1" style={{ color: '#52514e' }}>{t.title}</div>}
      <table className={`deck-table ${large ? 'deck-table-lg' : ''}`}>
        <thead>
          <tr>{t.columns.map((c) => <th key={c}>{c}</th>)}</tr>
        </thead>
        <tbody>
          {t.rows.map((r, i) => (
            <tr key={i}>{r.map((v, j) => <td key={j} style={{ color: j === 0 ? '#0b0b0b' : undefined }}>{typeof v === 'number' ? v.toLocaleString('es-MX') : v}</td>)}</tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function Bullets({ items, size = 15.5 }: { items: string[]; size?: number }) {
  return (
    <ul className="space-y-2.5">
      {items.map((b, i) => (
        <li key={i} className="flex gap-2.5 leading-snug" style={{ fontSize: size, color: '#2b2a28' }}>
          <span className="mt-[7px] h-[7px] w-[7px] shrink-0 rounded-full" style={{ background: '#0f8a6a' }} />
          <span dangerouslySetInnerHTML={{ __html: md(b) }} />
        </li>
      ))}
    </ul>
  )
}

// **negritas** y `código` mínimos
export function md(s: string) {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/`(.+?)`/g, '<code>$1</code>')
}

export function SlideRenderer({ s, n, total, brand = 'Vemo · Business Case Growth Analyst' }: { s: Slide; n: number; total: number; brand?: string }) {
  const hasVisual = !!(s.chart || s.table)
  const hasText = !!(s.bullets && s.bullets.length)
  const side = hasVisual && hasText
  return (
    <div className="deck-slide" style={{ width: W, height: H }}>
      <div className="absolute left-0 top-0 h-full w-[6px]" style={{ background: '#0f8a6a' }} />
      <div className="flex flex-col h-full px-14 pt-10 pb-8">
        {s.kicker && <div className="text-[13px] font-semibold uppercase tracking-[0.08em]" style={{ color: '#0f8a6a' }}>{s.kicker}</div>}
        <h1 className="text-[32px] font-semibold leading-tight mt-1">{s.title}</h1>
        {s.headline && <p className="text-[18px] font-semibold leading-snug mt-2" style={{ color: '#2b2a28' }} dangerouslySetInnerHTML={{ __html: md(s.headline) }} />}
        {s.kpis && s.kpis.length > 0 && <div className="mt-5"><Kpis kpis={s.kpis} /></div>}
        <div className={`flex-1 min-h-0 mt-5 ${side ? 'grid grid-cols-[1.15fr_1fr] gap-8' : 'flex flex-col gap-4'}`}>
          {hasVisual && (
            <div className="min-h-0 flex flex-col gap-2">
              {s.chart && (
                <>
                  <div className="text-[13.5px] font-semibold" style={{ color: '#52514e' }}>{s.chart.title}</div>
                  <Chart c={s.chart} width={side ? 640 : 1160} height={s.kpis ? (side ? 300 : 260) : side ? 380 : 330} />
                  {s.chart.note && <div className="text-[11.5px]" style={{ color: '#898781' }}>{s.chart.note}</div>}
                </>
              )}
              {s.table && <DeckTable t={s.table} large={!side && !s.chart} />}
            </div>
          )}
          {hasText && <div className="min-h-0"><Bullets items={s.bullets!} size={side ? 15 : 16.5} /></div>}
          {s.twoCol && (
            <div className="grid grid-cols-2 gap-8">
              {[{ t: s.twoCol.leftTitle, b: s.twoCol.left }, { t: s.twoCol.rightTitle, b: s.twoCol.right }].map((col, i) => (
                <div key={i} className="rounded-[10px] p-5" style={{ background: i === 0 ? '#f3f2ef' : '#e8f4ef' }}>
                  {col.t && <div className="text-[14px] font-semibold mb-3" style={{ color: i === 0 ? '#52514e' : '#0f6e55' }}>{col.t}</div>}
                  <Bullets items={col.b} size={15} />
                </div>
              ))}
            </div>
          )}
        </div>
        <div className="flex items-end justify-between pt-3 text-[11.5px]" style={{ color: '#898781' }}>
          <span className="max-w-[1000px]" dangerouslySetInnerHTML={{ __html: md(s.footer ?? brand) }} />
          <span className="tnum">{n} / {total}</span>
        </div>
      </div>
    </div>
  )
}
