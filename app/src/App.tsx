import { useEffect, useState } from 'react'
import { Landing } from './pages/Landing'
import { Dashboard } from './pages/Dashboard'
import { Anexo } from './pages/Anexo'
import { DeckViewer } from './deck/DeckViewer'
import { aiSlides, analysisSlides } from './deck/slides'

function useHash() {
  const [hash, setHash] = useState(location.hash)
  useEffect(() => {
    const on = () => setHash(location.hash)
    window.addEventListener('hashchange', on)
    return () => window.removeEventListener('hashchange', on)
  }, [])
  return hash.replace(/^#\/?/, '').split('/')
}

export default function App() {
  const [route, sub] = useHash()
  if (route === 'deck-analisis')
    return <DeckViewer key={route} slides={analysisSlides} route="deck-analisis" title="Deck de análisis · Vemo" pdf="/Vemo_Deck_Analisis.pdf" />
  if (route === 'deck-ia') return <DeckViewer key={route} slides={aiSlides} route="deck-ia" title="Uso de IA · Vemo" pdf="/Vemo_Deck_IA.pdf" />
  if (route === 'dashboard') return <Dashboard id={['impulso', 'conduce', 'watts'].includes(sub) ? sub : 'impulso'} />
  if (route === 'anexo') return <Anexo />
  return <Landing />
}
