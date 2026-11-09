# Vemo · Business Case App

Landing con 5 secciones (Impulso, Conduce, Watts, Deck, Anexo de IA). Por ahora todas son placeholders.

Stack: React 19 + Vite 6 + Tailwind 4 + TypeScript (mismo stack que el proyecto de TaskNest). App 100 % estática;
cuando haya dashboard, los datos irán como JSON en `public/data/` generados con SQL desde Postgres.

```bash
npm install
npm run dev      # http://localhost:5173
npm run build    # dist/
npm run deploy   # compila y publica a producción en Vercel (usa .vercel-link/project.json, no versionado)
```

Despliegue: proyecto `vemo-business-case` en Vercel. `vercel.json` ya trae build, salida `dist` y rutas SPA.
