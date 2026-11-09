// Genera los PDF de los decks desde la app compilada (una lámina 1280x720 por página).
// Uso (desde la raíz): (cd app && npm run build) && node tools/pdf/build_deck_pdfs.mjs
// Requiere: (cd tools/pdf && npm i) y un Chromium de Playwright en ~/Library/Caches/ms-playwright
import { spawn } from 'node:child_process'
import { existsSync, mkdirSync, readdirSync, copyFileSync } from 'node:fs'
import { homedir } from 'node:os'
import { join, resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { chromium } from 'playwright-core'

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '../..')
const APP = join(ROOT, 'app')
const OUT = join(ROOT, 'entregables')
const PORT = 4179

function findChromium() {
  if (process.env.CHROMIUM_PATH) return process.env.CHROMIUM_PATH
  const cache = join(homedir(), 'Library/Caches/ms-playwright')
  const dirs = readdirSync(cache).filter((d) => d.startsWith('chromium_headless_shell-')).sort().reverse()
  for (const d of dirs) {
    for (const sub of readdirSync(join(cache, d))) {
      const p = join(cache, d, sub, 'chrome-headless-shell')
      if (existsSync(p)) return p
    }
  }
  return undefined
}

const DECKS = [
  { route: 'deck-analisis', file: 'Vemo_Deck_Analisis.pdf' },
  { route: 'deck-ia', file: 'Vemo_Deck_IA.pdf' },
]

mkdirSync(OUT, { recursive: true })
const server = spawn('npx', ['vite', 'preview', '--port', String(PORT), '--strictPort'], { cwd: APP, stdio: 'pipe' })
await new Promise((ok, ko) => {
  const t = setTimeout(() => ko(new Error('vite preview no arrancó')), 20000)
  server.stdout.on('data', (d) => { if (String(d).includes(String(PORT))) { clearTimeout(t); ok() } })
})
try {
  const browser = await chromium.launch({ executablePath: findChromium() })
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } })
  for (const d of DECKS) {
    await page.goto(`http://localhost:${PORT}/#/${d.route}/print`, { waitUntil: 'networkidle' })
    await page.waitForSelector('.deck-page')
    const n = await page.locator('.deck-page').count()
    const out = join(OUT, d.file)
    await page.pdf({ path: out, width: '1280px', height: '720px', printBackground: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } })
    // copia pública para el botón "PDF" de la app
    copyFileSync(out, join(APP, 'public', d.file))
    console.log(`${d.file}: ${n} láminas -> ${out}`)
  }
  await browser.close()
} finally {
  server.kill()
}
