import { BatteryCharging, Car, FileSpreadsheet, FileText, Sparkles, Users } from 'lucide-react'

export const SECTIONS = [
  { href: '#/deck-analisis', title: 'Deck de análisis', desc: 'Resumen ejecutivo, los tres cases y la pregunta final (7 láminas).', icon: FileText },
  { href: '#/deck-ia', title: 'Uso de IA', desc: 'Qué delegué, cómo lo verifiqué y dónde corregí a la IA.', icon: Sparkles },
  { href: '#/dashboard/impulso', title: 'Dashboard · Vemo Impulso', desc: 'Funnel de arrendamiento y la meta de 400 entregas.', icon: Car },
  { href: '#/dashboard/conduce', title: 'Dashboard · Vemo Conduce', desc: 'Retención, cobertura de turnos y los $1.5 M de Q1 2027.', icon: Users },
  { href: '#/dashboard/watts', title: 'Dashboard · Vemo Watts', desc: 'Utilización, margen y la promoción de agosto.', icon: BatteryCharging },
  { href: '#/anexo', title: 'Anexo · Google Sheet y SQL', desc: 'Cálculos, supuestos y calidad de datos.', icon: FileSpreadsheet },
] as const

export function Landing() {
  return (
    <div className="max-w-[920px] mx-auto px-4 sm:px-8 py-16">
      <p className="text-[13px]" style={{ color: 'var(--text-muted)' }}>Business Case · Growth Analyst · Noviembre 2026</p>
      <h1 className="text-[30px] font-semibold mt-1">
        Vemo <span style={{ color: 'var(--accent)' }}>·</span> Impulso, Conduce y Watts
      </h1>
      <p className="mt-2 text-[15px]" style={{ color: 'var(--text-secondary)' }}>
        Tres decisiones de Dirección, una por línea de negocio. Recomendación sustentada con datos. Datos ficticios con fines de evaluación.
      </p>
      <div className="grid sm:grid-cols-2 gap-4 mt-8">
        {SECTIONS.map(({ href, title, desc, icon: Icon }) => (
          <a key={href} href={href} className="card p-5 block hover:opacity-90">
            <Icon size={20} style={{ color: 'var(--accent)' }} />
            <h2 className="text-[16px] font-semibold mt-3">{title}</h2>
            <p className="mt-1 text-[13px]" style={{ color: 'var(--text-secondary)' }}>{desc}</p>
          </a>
        ))}
      </div>
    </div>
  )
}
