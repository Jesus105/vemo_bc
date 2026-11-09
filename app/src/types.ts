export type Kpi = { label: string; value: string; sub?: string; tone?: 'good' | 'bad' | 'neutral' }
export type Series = { name: string; values: (number | null)[] }
export type Chart = {
  id: string
  title: string
  type: 'line' | 'bar' | 'hbar'
  unit?: string
  x: string[]
  series: Series[]
  note?: string
  refLine?: { value: number; label: string }
  stacked?: boolean
}
export type Table = { title?: string; columns: string[]; rows: (string | number)[][] }
export type CaseData = { title: string; answer: string; kpis: Kpi[]; charts: Chart[]; tables?: Table[]; notes: string[] }
export type Slide = {
  kicker?: string
  title: string
  headline?: string
  bullets?: string[]
  kpis?: Kpi[]
  chart?: Chart
  table?: Table
  footer?: string
  twoCol?: { left: string[]; right: string[]; leftTitle?: string; rightTitle?: string }
  notes?: string
}
