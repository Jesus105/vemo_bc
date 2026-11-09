import { BatteryCharging, Car, FileText, Sparkles, Users } from 'lucide-react'

export const SECTIONS = [
  { id: 'impulso', title: 'Case 1 · Vemo Impulso', desc: 'Funnel de arrendamiento y la meta de 400 entregas en un mes.', icon: Car },
  { id: 'conduce', title: 'Case 2 · Vemo Conduce', desc: 'Retención de conductores, cobertura de turnos y los $1.5 M de Q1 2027.', icon: Users },
  { id: 'watts', title: 'Case 3 · Vemo Watts', desc: 'Utilización y margen de los hubs de carga; la promoción de agosto.', icon: BatteryCharging },
  { id: 'deck', title: 'Deck de recomendación', desc: 'Resumen ejecutivo, los tres cases y la pregunta final (máx. 7 láminas).', icon: FileText },
  { id: 'anexo-ia', title: 'Anexo · Cálculos y uso de IA', desc: 'Cálculos y cómo se usó y verificó la IA.', icon: Sparkles },
] as const

export function Landing() {
  return (
    <div className="max-w-[880px] mx-auto px-4 sm:px-8 py-16">
      <p className="text-[13px]" style={{ color: 'var(--text-muted)' }}>Business Case · Growth Analyst · Noviembre 2026</p>
      <h1 className="text-[28px] font-semibold mt-1">Vemo</h1>
      <p className="mt-2 text-[15px]" style={{ color: 'var(--text-secondary)' }}>
        Tres decisiones de Dirección, una por línea de negocio. Datos ficticios con fines de evaluación.
      </p>
      <div className="grid sm:grid-cols-2 gap-4 mt-8">
        {SECTIONS.map(({ id, title, desc, icon: Icon }) => (
          <a key={id} href={`#/${id}`} className="card p-5 block hover:opacity-90">
            <Icon size={20} style={{ color: 'var(--accent)' }} />
            <h2 className="text-[16px] font-semibold mt-3">{title}</h2>
            <p className="mt-1 text-[13px]" style={{ color: 'var(--text-secondary)' }}>{desc}</p>
          </a>
        ))}
      </div>
    </div>
  )
}
