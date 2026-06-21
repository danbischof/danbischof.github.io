# danbischof.github.io

Personal academic website of [Daniel Bischof](https://www.danbischof.com) — Professor and Chair of Comparative Politics at the University of Münster and Associate Professor at Aarhus University.

Live at: **[www.danbischof.com](https://www.danbischof.com)**

## Structure

Plain static HTML — no framework, no build step required.

| File / Folder | Purpose |
|---|---|
| `index.html` | Landing page |
| `bio.html` | CV and biography |
| `publications.html` | Peer-reviewed publications |
| `working-papers.html` | Working papers |
| `projects.html` | Research project overview |
| `project-*.html` | Individual project pages |
| `teaching.html` | Teaching and syllabi |
| `stata-schemes.html` | Stata figure scheme gallery |
| `style.css` | All styling, incl. dark mode |
| `theme.js` | Dark/light mode toggle + mobile nav |
| `build.py` | Regenerates publications pages from `publications.bib` |
| `publications.bib` | BibTeX source for all publications |
| `assets/` | PDFs, images, SVGs |

## Updating the site

1. Edit files locally in this folder
2. Commit and push via GitHub Desktop
3. GitHub Pages deploys automatically (~60 seconds)

**To update publications:** edit `publications.bib`, run `python3 build.py`, then commit the regenerated `publications.html` and `working-papers.html`.

## Built with

- Plain HTML/CSS/JS
- [Claude](https://claude.ai) (design and development)
- Hosted on [GitHub Pages](https://pages.github.com)
