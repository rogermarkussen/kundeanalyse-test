# Marimo testcase

Dette er en liten marimo-notebook for å teste interaktive Python-notebooks i Cursor.

## Kjør

```bash
uv run marimo edit customer_churn_demo.py
```

Notebooken viser en syntetisk kundeanalyse med:

- sliders og dropdown for input
- reaktiv datagenerering
- KPI-er som oppdateres automatisk
- Altair-graf
- enkel simulering av rabatt/tiltak

## Bygg GitHub Pages-versjon

```bash
./scripts/build-gh-pages.sh
```

Publiser deretter innholdet i `dist/` til GitHub Pages. `dist/index.html` er
inngangen til appen, og `dist/.nojekyll` er inkludert fordi marimo-eksporten
bruker statiske assets som GitHub Pages ikke skal Jekyll-prosessere.

Hvis prosjektet er koblet til et GitHub-repo som `origin`, kan du publisere
direkte til en klassisk `gh-pages` branch:

```bash
./scripts/publish-gh-pages.sh
```

I GitHub-repoet: gå til **Settings -> Pages** og velg:

```text
Source: Deploy from a branch
Branch: gh-pages
Folder: / (root)
```

Lokal test av den eksporterte appen:

```bash
python -m http.server 8027 --directory dist
```

Åpne:

```text
http://127.0.0.1:8027/
```
