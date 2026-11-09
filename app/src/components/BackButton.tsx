import { ArrowLeft } from 'lucide-react'

// Regresa a la vista anterior dentro de la app; si se entró directo por URL, va al inicio.
export function BackButton() {
  const back = (e: React.MouseEvent) => {
    e.preventDefault()
    if (window.history.length > 1 && document.referrer.startsWith(location.origin)) window.history.back()
    else location.hash = '#/'
  }
  return (
    <a href="#/" onClick={back} className="back-btn" aria-label="Regresar">
      <ArrowLeft size={15} /> Regresar
    </a>
  )
}
