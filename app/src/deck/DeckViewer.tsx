import { BackButton } from '../components/BackButton'
import { useEffect, useRef, useState, type RefObject } from 'react'
import { ChevronLeft, ChevronRight, Download, StickyNote } from 'lucide-react'
import type { Slide } from '../types'
import { H, SlideRenderer, W } from './SlideRenderer'

function useScale(ref: RefObject<HTMLDivElement | null>) {
  const [scale, setScale] = useState(1)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const ro = new ResizeObserver(([e]) => {
      const { width, height } = e.contentRect
      setScale(Math.min(width / W, height / H))
    })
    ro.observe(el)
    return () => ro.disconnect()
  }, [ref])
  return scale
}

export function DeckViewer({ slides, route, title, pdf }: { slides: Slide[]; route: string; title: string; pdf: string }) {
  const print = location.hash.includes('/print')
  const initial = () => {
    const m = location.hash.match(new RegExp(`${route}/(\\d+)`))
    return m ? Math.min(slides.length - 1, Math.max(0, Number(m[1]) - 1)) : 0
  }
  const [i, setI] = useState(initial)
  const [notes, setNotes] = useState(false)
  const stageRef = useRef<HTMLDivElement>(null)
  const scale = useScale(stageRef)

  useEffect(() => {
    if (!print) history.replaceState(null, '', `#/${route}/${i + 1}`)
  }, [i, print, route])

  useEffect(() => {
    if (print) return
    const on = (e: KeyboardEvent) => {
      if (['ArrowRight', 'PageDown', ' '].includes(e.key)) setI((x) => Math.min(slides.length - 1, x + 1))
      else if (['ArrowLeft', 'PageUp'].includes(e.key)) setI((x) => Math.max(0, x - 1))
      else if (e.key === 'Home') setI(0)
      else if (e.key === 'End') setI(slides.length - 1)
      else if (e.key.toLowerCase() === 'n') setNotes((v) => !v)
      else return
      e.preventDefault()
    }
    window.addEventListener('keydown', on)
    return () => window.removeEventListener('keydown', on)
  }, [print, slides.length])

  if (print)
    return (
      <div className="deck deck-print">
        {slides.map((s, k) => (
          <div key={k} className="deck-page">
            <SlideRenderer s={s} n={k + 1} total={slides.length} />
          </div>
        ))}
      </div>
    )

  return (
    <div className="deck deck-viewer h-screen flex flex-col">
      <div className="h-12 shrink-0 flex items-center gap-3 px-4 border-b" style={{ borderColor: 'var(--border)' }}>
        <BackButton />
        <span className="text-[13px] font-semibold ml-2">{title}</span>
        <div className="ml-auto flex items-center gap-2">
          <button className="chip" aria-pressed={notes} onClick={() => setNotes((v) => !v)} title="Notas (N)">
            <StickyNote size={14} /> Notas
          </button>
          <a className="chip" href={pdf} download>
            <Download size={14} /> PDF
          </a>
        </div>
      </div>
      <div ref={stageRef} className="flex-1 min-h-0 relative overflow-hidden">
        <div
          className="absolute shadow-xl"
          style={{ width: W, height: H, left: '50%', top: '50%', transform: `translate(-50%, -50%) scale(${scale * 0.96})`, transformOrigin: 'center' }}
        >
          <SlideRenderer s={slides[i]} n={i + 1} total={slides.length} />
        </div>
      </div>
      {notes && (
        <div className="shrink-0 max-h-[22vh] overflow-auto px-6 py-3 border-t text-[14px] leading-relaxed" style={{ borderColor: 'var(--border)', background: 'var(--surface-1)' }}>
          <div className="text-[11px] uppercase tracking-wide mb-1" style={{ color: 'var(--text-muted)' }}>Notas · lámina {i + 1}</div>
          {slides[i].notes ?? 'Sin notas.'}
        </div>
      )}
      <div className="h-14 shrink-0 flex items-center justify-center gap-4 border-t" style={{ borderColor: 'var(--border)' }}>
        <button className="chip" onClick={() => setI((x) => Math.max(0, x - 1))} disabled={i === 0} aria-label="Anterior">
          <ChevronLeft size={16} />
        </button>
        <div className="flex gap-1.5" role="tablist" aria-label="Láminas">
          {slides.map((_, k) => (
            <button
              key={k}
              role="tab"
              aria-selected={k === i}
              aria-label={`Lámina ${k + 1}`}
              onClick={() => setI(k)}
              className="h-2 rounded-full transition-all"
              style={{ width: k === i ? 22 : 8, background: k === i ? 'var(--accent)' : 'var(--axis)' }}
            />
          ))}
        </div>
        <button className="chip" onClick={() => setI((x) => Math.min(slides.length - 1, x + 1))} disabled={i === slides.length - 1} aria-label="Siguiente">
          <ChevronRight size={16} />
        </button>
        <span className="text-[12px] tnum ml-2" style={{ color: 'var(--text-muted)' }}>
          {i + 1} / {slides.length} · ← → para navegar · N para notas
        </span>
      </div>
    </div>
  )
}
