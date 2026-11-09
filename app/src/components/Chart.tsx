import type { Chart as ChartDef } from '../types'

const COLORS = ['var(--accent)', 'var(--series-2)', 'var(--series-1)', 'var(--series-4)', 'var(--series-3)']

export function fmtNum(v: number, unit?: string) {
  // '%' = valores ya en puntos porcentuales (46.1 → 46.1%)
  if (unit === '%') return `${+v.toFixed(Math.abs(v) < 10 ? 1 : 0)}%`
  const a = Math.abs(v)
  const s = a >= 1e6 ? `${(v / 1e6).toFixed(1)} M` : a >= 1e4 ? `${(v / 1e3).toFixed(0)} k` : a >= 1000 ? v.toLocaleString('es-MX', { maximumFractionDigits: 0 }) : `${+v.toFixed(a < 1 ? 2 : a < 100 ? 1 : 0)}`
  return unit === '$' ? `$${s}` : unit && unit !== '%' ? `${s} ${unit}` : s
}

function niceMax(v: number) {
  if (v <= 0) return 1
  const p = Math.pow(10, Math.floor(Math.log10(v)))
  const n = v / p
  return ([1, 1.2, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10].find((k) => n <= k) ?? 10) * p
}

export function Chart({ c, width = 560, height = 280, compact = false }: { c: ChartDef; width?: number; height?: number; compact?: boolean }) {
  const fs = compact ? 11 : 12
  const legend = c.series.length > 1
  const all = c.series.flatMap((s) => s.values).filter((v): v is number => v != null)
  const stackedMax = c.stacked ? Math.max(...c.x.map((_, i) => c.series.reduce((a, s) => a + (s.values[i] ?? 0), 0))) : 0
  const rawMin = Math.min(0, ...all)
  const rawMax = Math.max(c.stacked ? stackedMax : Math.max(...all, 0), c.refLine?.value ?? 0) * 1.05
  const tStep = niceMax((rawMax - rawMin) / 4)
  const minV = rawMin < 0 ? Math.floor(rawMin / tStep) * tStep : 0
  const max = rawMin < 0 ? Math.ceil(rawMax / tStep) * tStep : niceMax(rawMax)

  if (c.type === 'hbar') {
    const labelW = Math.min(170, Math.max(...c.x.map((x) => x.length)) * 7.6 + 14)
    const top = legend ? 26 : 6
    const rowH = (height - top - 6) / c.x.length
    const bw = (width - labelW - 60) / max
    const nS = c.series.length
    const barH = Math.min(22, (rowH * 0.72) / nS)
    return (
      <svg viewBox={`0 0 ${width} ${height}`} width="100%" role="img" aria-label={c.title}>
        {legend && <Legend c={c} y={12} fs={fs} />}
        {c.x.map((lab, i) => {
          const y0 = top + i * rowH + (rowH - barH * nS) / 2
          return (
            <g key={lab}>
              <text x={labelW - 8} y={y0 + (barH * nS) / 2} dy="0.35em" textAnchor="end" fontSize={fs} fill="var(--text-secondary)">{lab}</text>
              {c.series.map((s, k) => {
                const v = s.values[i]
                if (v == null) return null
                const w = Math.max(1, Math.abs(v) * bw)
                return (
                  <g key={s.name}>
                    <rect x={labelW} y={y0 + k * barH} width={w} height={barH - 2} rx={3} fill={COLORS[k % COLORS.length]} />
                    <text x={labelW + w + 6} y={y0 + k * barH + barH / 2 - 1} dy="0.35em" fontSize={fs} className="tnum" fill="var(--text-primary)">{fmtNum(v, c.unit)}</text>
                  </g>
                )
              })}
            </g>
          )
        })}
        {c.refLine && (
          <g>
            <line x1={labelW + c.refLine.value * bw} x2={labelW + c.refLine.value * bw} y1={top - 4} y2={height - 4} stroke="var(--critical)" strokeDasharray="4 3" />
            <text x={labelW + c.refLine.value * bw + 4} y={top + 4} fontSize={fs - 1} fill="var(--critical)">{c.refLine.label}</text>
          </g>
        )}
      </svg>
    )
  }

  const m = { l: 52, r: 14, t: legend ? 30 : 12, b: 26 }
  const iw = width - m.l - m.r
  const ih = height - m.t - m.b
  const y = (v: number) => m.t + ih - ((v - minV) / (max - minV)) * ih
  const n = c.x.length
  const step = iw / n
  const ticks = rawMin < 0 ? Array.from({ length: Math.round((max - minV) / tStep) + 1 }, (_, i) => minV + i * tStep) : [0, 0.25, 0.5, 0.75, 1].map((f) => minV + f * (max - minV))
  const skip = Math.ceil(n / (compact ? 8 : 12))

  return (
    <svg viewBox={`0 0 ${width} ${height}`} width="100%" role="img" aria-label={c.title}>
      {legend && <Legend c={c} y={12} fs={fs} />}
      {ticks.map((t) => (
        <g key={t}>
          <line x1={m.l} x2={width - m.r} y1={y(t)} y2={y(t)} stroke="var(--grid)" />
          <text x={m.l - 6} y={y(t)} dy="0.35em" textAnchor="end" fontSize={fs - 1} fill="var(--text-muted)" className="tnum">{fmtNum(t, c.unit)}</text>
        </g>
      ))}
      {c.x.map((lab, i) => (i % skip === 0 ? <text key={lab + i} x={m.l + step * (i + 0.5)} y={height - 8} textAnchor="middle" fontSize={fs - 1} fill="var(--text-muted)">{lab}</text> : null))}
      {c.type === 'bar' &&
        c.x.map((_, i) => {
          const nS = c.series.length
          let acc = 0
          return c.series.map((s, k) => {
            const v = s.values[i]
            if (v == null) return null
            const bwid = c.stacked ? step * 0.66 : (step * 0.74) / nS
            const x0 = c.stacked ? m.l + step * i + step * 0.17 : m.l + step * i + step * 0.13 + k * bwid
            const yTop = c.stacked ? y(acc + v) : y(Math.max(0, v))
            const yBot = c.stacked ? y(acc) : y(Math.min(0, v))
            acc += c.stacked ? v : 0
            return (
              <g key={s.name + i}>
                <rect x={x0} y={yTop} width={Math.max(1, bwid - 2)} height={Math.max(0.5, yBot - yTop)} rx={2} fill={COLORS[k % COLORS.length]} />
                {!c.stacked && nS === 1 && n <= 14 && (
                  <text x={x0 + bwid / 2 - 1} y={yTop - 4} textAnchor="middle" fontSize={fs - 1} className="tnum" fill="var(--text-secondary)">{fmtNum(v, c.unit)}</text>
                )}
              </g>
            )
          })
        })}
      {c.type === 'line' &&
        c.series.map((s, k) => {
          const pts = s.values.map((v, i) => (v == null ? null : [m.l + step * (i + 0.5), y(v)] as const))
          let d = ''
          pts.forEach((p, i) => {
            if (!p) return
            d += `${i === 0 || !pts[i - 1] ? 'M' : 'L'}${p[0]},${p[1]}`
          })
          const lastI = pts.map((p, i) => (p ? i : -1)).filter((i) => i >= 0).pop()
          return (
            <g key={s.name}>
              <path d={d} fill="none" stroke={COLORS[k % COLORS.length]} strokeWidth={2.2} />
              {pts.map((p, i) => p && <circle key={i} cx={p[0]} cy={p[1]} r={2.6} fill={COLORS[k % COLORS.length]} />)}
              {lastI != null && pts[lastI] && (
                <text x={pts[lastI]![0]} y={pts[lastI]![1] - 8} textAnchor="middle" fontSize={fs - 1} className="tnum" fill={COLORS[k % COLORS.length]} fontWeight={600}>
                  {fmtNum(s.values[lastI]!, c.unit)}
                </text>
              )}
            </g>
          )
        })}
      {c.refLine && (
        <g>
          <line x1={m.l} x2={width - m.r} y1={y(c.refLine.value)} y2={y(c.refLine.value)} stroke="var(--critical)" strokeDasharray="5 4" strokeWidth={1.4} />
          <text x={m.l + 4} y={y(c.refLine.value) - 5} textAnchor="start" fontSize={fs - 1} fill="var(--critical)" fontWeight={600} stroke="var(--surface-1)" strokeWidth={3} paintOrder="stroke">{c.refLine.label}</text>
        </g>
      )}
    </svg>
  )
}

function Legend({ c, y, fs }: { c: ChartDef; y: number; fs: number }) {
  let x = 4
  return (
    <g>
      {c.series.map((s, k) => {
        const g = (
          <g key={s.name} transform={`translate(${x},${y})`}>
            <rect width={10} height={10} y={-6} rx={2} fill={COLORS[k % COLORS.length]} />
            <text x={14} dy="0.3em" fontSize={fs} fill="var(--text-secondary)">{s.name}</text>
          </g>
        )
        x += 24 + s.name.length * 6.6
        return g
      })}
    </g>
  )
}
