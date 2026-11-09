import { useEffect, useState } from 'react'
import { Landing, SECTIONS } from './pages/Landing'
import { Placeholder } from './pages/Placeholder'

function useHashRoute() {
  const [hash, setHash] = useState(location.hash)
  useEffect(() => {
    const on = () => setHash(location.hash)
    window.addEventListener('hashchange', on)
    return () => window.removeEventListener('hashchange', on)
  }, [])
  return hash.replace(/^#\/?/, '').split('/')[0]
}

export default function App() {
  const route = useHashRoute()
  const section = SECTIONS.find((s) => s.id === route)
  return section ? <Placeholder title={section.title} /> : <Landing />
}
