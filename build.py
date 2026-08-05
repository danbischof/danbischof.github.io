#!/usr/bin/env python3
"""Build publications.html and working-papers.html from BibTeX files."""
import re, os, html as html_mod

HERE    = os.path.dirname(os.path.abspath(__file__))
BIB_PUB = os.path.join(HERE, 'publications.bib')
BIB_WP  = os.path.join(HERE, 'papers.bib')
OUT_PUB = os.path.join(HERE, 'publications.html')
OUT_WP  = os.path.join(HERE, 'working-papers.html')

# ── Working-paper overrides ───────────────────────────────────────────────────
# Explicit order within the "Available Upon Request" group (unlisted → appended by year)
WP_REQUEST_ORDER = [
    'albers2026income',
    'bischof2023weimarriot',
    'bischof2026localleaders',
    'bischof2021protest',
]

# Papers to display with an "Under Review" badge
WP_UNDER_REVIEW = {
    'bischof2026scholz',
    'bischof2026bans',
    'haas2025',
    'Frederiksen2025',
}

# Title overrides (key → new title string)
WP_RENAME = {
    'bischof2026demcit': 'What Citizens Mean by Democracy: Partisan Differences in Open-Ended Survey Responses',
}

# Abstract overrides (key → abstract string)
WP_ABSTRACT = {
    'bischof2026demcit': 'Do voters from different partisan camps understand democracy in the same way? We analyze more than 25,000 open-ended survey responses from representative samples in 14 countries, classifying answers with a fine-tuned language model and sentence embeddings. Citizens most often define democracy through individual and civil rights; multidimensional definitions are rare, and elections are mentioned by only 17% of respondents. Yet shared vocabulary masks partisan divergence. Far-right voters and non-voters are less likely to mention civil rights, elections, and horizontal accountability, while far-right voters more often invoke majoritarian principles. Among respondents mentioning rights, left voters connect rights to equality and citizenship, whereas right voters emphasize freedom of speech. Democratic contestation thus unfolds within democratic language, creating openings for selective elite reframing.',
}


# ── Publication topic tags ────────────────────────────────────────────────────
# Each key maps to a list of topic slugs. Adjust as needed.
# Available slugs: key · farright · democracy · messaging · parties · methods
PUB_TOPICS = {
    # ── Key publications (user-specified 5) ──────────────────────────────────
    'foos2022tabloid':            ['key', 'messaging', 'publicopinion'],   # APSR: tabloid media & Euroscepticism
    'ziblatt2023':                ['key', 'farright'],                     # APSR: radical right in peripheral regions
    'bischof2019voters':          ['key', 'farright', 'publicopinion'],    # AJPS: voter polarization from radical entry
    'riaz2024':                   ['key', 'farright', 'publicopinion'],    # out-group threat & hate crimes
    'bischof2026complexity':      ['key', 'messaging', 'publicopinion'],   # simple language & voter knowledge

    # ── Far Right ────────────────────────────────────────────────────────────
    'bischof2024sd':              ['farright', 'parties', 'publicopinion'], # where did Social Dem. voters go?

    # ── Democracy ────────────────────────────────────────────────────────────
    'bischof2026rollcall':        ['protest', 'parties'],                    # protest → MP roll-call votes
    'Juratic2026':                ['democracy', 'protest', 'publicopinion'], # unequal tolerance for protest
    'bischof2015repression':      ['democracy'],                             # repression, monarchs, revolution (Arab world)

    # ── Protest ──────────────────────────────────────────────────────────────
    'bernardi2021public':         ['protest', 'publicopinion'],             # does protest move legislative agendas?
    'bischof2023place':           ['protest'],                              # place-based campaigning & grassroots mobilization
    'bernardi2017effects':        ['protest'],                              # Fukushima protests → nuclear energy policy

    # ── Messaging & Media ────────────────────────────────────────────────────
    'bischof2018simple':          ['messaging', 'publicopinion'],           # complexity in campaign messages & knowledge
    'bischof2018ideological':     ['parties', 'messaging'],                 # party rhetoric vs. actual policy-making

    # ── Party Politics ───────────────────────────────────────────────────────
    'bischof2026brexit':          ['parties'],                              # field exp.: MPs & constituent responsiveness
    'saalfeld2012minority':       ['parties'],                              # minority-ethnic MPs & substantive representation
    'Dumont2023':                 ['parties'],                              # coalition formation & tangential preferences
    'bischof2017towards':         ['parties'],                              # niche party concept renewal
    'bischof2017makes':           ['parties', 'publicopinion'],             # why parties adapt to voter preferences
    'senninger2018working':       ['parties'],                              # policy issue transfer in multilevel space
    'wolkenstein2020party':       ['parties'],                              # party policy diffusion in EU multilevel space
    'senninger2021voters':        ['parties', 'publicopinion'],             # voters & EU scrutiny by domestic politicians
    'senninger2021transnational': ['parties'],                              # transnational alliances → national party policy

    # ── Methods ──────────────────────────────────────────────────────────────
    'bischof2026sdb':             ['methods', 'publicopinion'], # social desirability bias in online surveys
    'bischof2016blindschemes':    ['methods'],             # Stata: colorblind-safe graph schemes
    'bischof2017new':             ['methods'],             # Stata: plotplain & plottig schemes
    'bischof2017g538schemes':     ['methods'],             # Stata: 538-style graph schemes
    'bischof2019use':             ['methods'],             # p-values in political science
    'bischof2021advantages':      ['methods'],             # audit experiments: advantages & limits
}

PUB_TOPIC_LABELS = {
    'key':           'Key Publications',
    'farright':      'Far Right',
    'democracy':     'Democracy',
    'protest':       'Protest',
    'messaging':     'Messaging &amp; Media',
    'publicopinion': 'Public Opinion',
    'parties':       'Party Politics',
    'methods':       'Methods',
}

# Topics rendered on the second line
MACRO_TOPICS = {'publicopinion', 'parties', 'methods'}

# ── Parser ────────────────────────────────────────────────────────────────────
def parse_bib(path):
    with open(path, encoding='utf-8') as f:
        text = f.read()
    text = re.sub(r'^---.*?---\s*', '', text, flags=re.DOTALL)
    entries = []; i = 0; n = len(text)
    while i < n:
        at = text.find('@', i)
        if at < 0: break
        ob = text.find('{', at)
        if ob < 0: break
        cm = text.find(',', ob)
        if cm < 0: break
        key = text[ob+1:cm].strip()
        depth = 0; j = ob
        while j < n:
            if text[j]=='{': depth+=1
            elif text[j]=='}':
                depth-=1
                if depth==0: break
            j+=1
        body = text[cm+1:j]; i = j+1
        e = {'_key': key}
        bi = 0; bn = len(body)
        while bi < bn:
            while bi < bn and body[bi] in ' \t\n\r,': bi+=1
            if bi >= bn: break
            m = re.match(r'(\w+)\s*=\s*', body[bi:])
            if not m: bi+=1; continue
            fname = m.group(1).lower(); bi += len(m.group(0))
            if bi >= bn: break
            ch = body[bi]
            if ch=='{':
                d=0; fj=bi
                while fj<bn:
                    if body[fj]=='{': d+=1
                    elif body[fj]=='}':
                        d-=1
                        if d==0: break
                    fj+=1
                val=body[bi+1:fj].strip(); bi=fj+1
            elif ch=='"':
                fj=bi+1
                while fj<bn and body[fj]!='"': fj+=1
                val=body[bi+1:fj].strip(); bi=fj+1
            else:
                fj=bi
                while fj<bn and body[fj] not in ',\n}': fj+=1
                val=body[bi:fj].strip(); bi=fj
            e[fname]=val
        entries.append(e)
    return entries

# ── Text helpers ──────────────────────────────────────────────────────────────
def clean(text):
    if not text: return ''
    text = re.sub(r'\\textcolor\{[^}]+\}\{([^}]+)\}', r'\1', text)
    text = re.sub(r'\\textit\{([^}]+)\}', r'<em>\1</em>', text)
    text = re.sub(r'\\emph\{([^}]+)\}', r'<em>\1</em>', text)
    text = re.sub(r'\\textbf\{([^}]+)\}', r'<strong>\1</strong>', text)
    text = re.sub(r"``(.+?)''", r'&#8220;\1&#8221;', text, flags=re.DOTALL)
    text = text.replace("``",'&#8220;').replace("''",'&#8221;')
    text = text.replace('\\%','%').replace('\\&','&amp;')
    text = re.sub(r"\\[`'^\"~]\{?(\w)\}?", r'\1', text)
    text = re.sub(r"\\'{?([a-zA-ZÄÖÜäöü])}?", r'\1', text)
    text = re.sub(r'\\\w+\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    text = re.sub(r'[{}]', '', text)
    text = re.sub(r'%[^\n]*', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def fmt_name(n):
    n = n.strip().replace('{','').replace('}','')
    n = re.sub(r"\\[`'^\"~]\{?(\w)\}?", r'\1', n)
    n = re.sub(r"\\'{?(\w)}", r'\1', n)
    if ',' in n:
        p = n.split(',',1)
        return p[1].strip()+' '+p[0].strip()
    return n

def fmt_authors(author_str):
    if not author_str: return ''
    parts = re.split(r'\s+and\s+', author_str)
    others = []
    for p in parts:
        fn = fmt_name(p)
        if re.match(r'Daniel\s+Bischof$', fn.strip(), re.I): continue
        if re.match(r'Bischof,?\s*Daniel', p.strip(), re.I): continue
        others.append(fn)
    if not others: return ''
    if len(others)==1: return 'with '+others[0]
    return 'with '+', '.join(others[:-1])+', and '+others[-1]

def h(s): return html_mod.escape(str(s))

# ── Classification ─────────────────────────────────────────────────────────────
CHAPTER_ABBRS = {'cup', 'routledge', 'springer', 'oxford', 'palgrave', 'book chapter'}

def classify_pub(e):
    j = e.get('journal','').lower()
    a = e.get('abbr','').lower()
    if a == 'software': return 'software'
    if a in CHAPTER_ABBRS: return 'chapter'
    if 'forthcoming' in j or 'conditional accept' in j: return 'forthcoming'
    return 'published'

def classify_wp(e):
    j = e.get('journal','').lower()
    if 'available upon request' in j: return 'request'
    return 'review'

# ── Entry HTML ─────────────────────────────────────────────────────────────────
def pub_item(e, show_journal=True, under_review=False, journal_label='Journal'):
    title    = clean(e.get('title',''))
    authors  = fmt_authors(e.get('author',''))
    raw_j    = e.get('journal','')
    abbr     = e.get('abbr','')
    pdf      = e.get('pdf','') or e.get('PDF','')
    jurl     = e.get('html','')
    abstract = clean(e.get('abstract',''))

    jdisplay = ''
    if show_journal and raw_j:
        jname = re.sub(r'\s*:\s*(forthcoming|conditional accept)', '', raw_j, flags=re.I).strip()
        jname = re.sub(r'In\s*:\s*', '', jname, flags=re.I)
        jname = jname.replace('\\&', '&').replace('\\%', '%')
        badge = ''
        if 'conditional accept' in raw_j.lower():
            badge = ' <span class="badge badge-forthcoming">Conditional Accept</span>'
        elif 'forthcoming' in raw_j.lower():
            badge = ' <span class="badge badge-forthcoming">Forthcoming</span>'
        jdisplay = f'      <div class="pub-venue"><em>{h(jname)}</em>{badge}</div>\n'
    elif under_review:
        jdisplay = '      <div class="pub-venue"><span class="badge badge-review">Under Review</span></div>\n'
    elif not show_journal and not jurl:
        jdisplay = '      <div class="pub-venue"><span class="badge badge-request">Available Upon Request</span></div>\n'

    GALLERY_KEYS = {'bischof2016blindschemes', 'bischof2017new', 'bischof2017g538schemes'}
    key = e.get('_key', '')

    links = []
    if abstract:
        links.append('<details><summary>Abstract</summary></details>')
    if pdf:
        links.append(f'<a href="assets/pdf/{h(pdf)}" target="_blank" rel="noopener">PDF</a>')
    if jurl:
        link_label = 'Book' if abbr.lower() in CHAPTER_ABBRS else journal_label
        links.append(f'<a href="{h(jurl)}" target="_blank" rel="noopener">{h(link_label)}</a>')
    if key in GALLERY_KEYS:
        links.append('<a href="stata-schemes.html" target="_blank" rel="noopener" class="gallery-link">Gallery</a>')

    links_str = '\n        '.join(links) if links else ''
    ahtml = f'\n      <div class="abstract-text" hidden>{abstract}</div>' if abstract else ''
    auth_html = f'\n      <div class="pub-authors">{h(authors)}</div>' if authors else ''

    topics_attr = ''
    if key in PUB_TOPICS:
        topics_attr = f' data-topics="{" ".join(PUB_TOPICS[key])}"'

    return f'''    <li{topics_attr}>
      <div class="pub-title">&#8220;{h(title)}&#8221;</div>{auth_html}
{jdisplay}      <div class="pub-links">
        {links_str}
      </div>{ahtml}
    </li>'''

# ── Shared HTML ────────────────────────────────────────────────────────────────
def nav(active=''):
    pc = ' class="active"' if active=='pub' else ''
    wc = ' class="active"' if active=='wp'  else ''
    return f'''<nav id="site-nav">
  <button class="nav-burger" onclick="toggleNav()" aria-label="Toggle menu">
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
  </button>
  <ul>
    <li><a href="index.html">About</a></li>
    <li><a href="bio.html">Bio</a></li>
    <li><a href="publications.html"{pc}>Publications</a></li>
    <li><a href="working-papers.html"{wc}>Working Papers</a></li>
    <li><a href="projects.html">Projects</a></li>
    <li><a href="teaching.html">Teaching</a></li>
    <li class="nav-toggle">
      <button id="theme-toggle" onclick="toggleTheme()" aria-label="Toggle dark mode" title="Toggle dark mode">
        <svg class="icon-moon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
        <svg class="icon-sun" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 17a5 5 0 1 1 0-10 5 5 0 0 1 0 10zm0-2a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM11 1h2v3h-2zm0 19h2v3h-2zM3.515 4.929l1.414-1.414L7.05 5.636 5.636 7.05 3.515 4.929zM16.95 18.364l1.414-1.414 2.121 2.121-1.414 1.414-2.121-2.121zM1 11h3v2H1zm19 0h3v2h-3zM4.929 20.485l-1.414-1.414 2.121-2.121 1.414 1.414-2.121 2.121zM18.364 7.05l-1.414-1.414 2.121-2.121 1.414 1.414-2.121 2.121z"/></svg>
      </button>
    </li>
  </ul>
</nav>'''

FOOTER = '  © Daniel Bischof &nbsp;·&nbsp; <a href="mailto:db@danbischof.com">db@danbischof.com</a> &nbsp;·&nbsp; Built with <a href="https://claude.ai" target="_blank" rel="noopener">Claude</a>'

SCRIPT = '''<script>
  document.querySelectorAll('.pub-links details').forEach(function(det){
    var li=det.closest('li');
    var ab=li?li.querySelector('.abstract-text'):null;
    if(!ab)return;
    det.addEventListener('toggle',function(){ab.hidden=!det.open;});
  });
</script>'''

# ── Build publications.html ────────────────────────────────────────────────────
def build_pub(entries):
    fc  = [e for e in entries if classify_pub(e)=='forthcoming']
    pub = [e for e in entries if classify_pub(e)=='published']
    ch  = [e for e in entries if classify_pub(e)=='chapter']
    sw  = [e for e in entries if classify_pub(e)=='software']
    for lst in [fc, pub, ch]: lst.sort(key=lambda e:int(e.get('year','0') or 0), reverse=True)

    numbered_total = len(fc) + len(pub) + len(ch)

    def sec(title, lst, jn=True, misc=False, first=False, reset=0):
        items = '\n\n'.join(pub_item(e, show_journal=jn) for e in lst)
        cls = 'pub-list pub-list-misc' if misc else 'pub-list'
        style = f' style="counter-reset: pub-counter {reset}"' if first else ''
        return f'  <h2>{title}</h2>\n  <ol class="{cls}"{style}>\n\n{items}\n\n  </ol>'

    parts = [
        sec('Forthcoming', fc, first=True, reset=numbered_total+1),
        sec('Peer-Reviewed Articles', pub),
    ]
    if ch:  parts.append(sec('Book Chapters', ch))
    if sw:  parts.append(sec('Software', sw, jn=False, misc=True))
    content = '\n\n'.join(parts)

    fine_btns = '\n  '.join(
        f'<button class="filter-btn" data-topic="{slug}" onclick="filterPubs(\'{slug}\')">{label}</button>'
        for slug, label in PUB_TOPIC_LABELS.items()
        if slug not in MACRO_TOPICS
    )
    macro_btns = '\n  '.join(
        f'<button class="filter-btn" data-topic="{slug}" onclick="filterPubs(\'{slug}\')">{label}</button>'
        for slug, label in PUB_TOPIC_LABELS.items()
        if slug in MACRO_TOPICS
    )
    filter_bar = f'''<div class="filter-bar">
  <button class="filter-btn active" data-topic="all" onclick="filterPubs(\'all\')">All</button>
  {fine_btns}
  <div class="filter-break"></div>
  {macro_btns}
</div>'''

    filter_script = '''<script>
  function filterPubs(topic) {
    document.querySelectorAll('.filter-btn').forEach(function(b) {
      b.classList.toggle('active', b.dataset.topic === topic);
    });
    var isFiltered = topic !== 'all';
    document.body.classList.toggle('filter-active', isFiltered);
    document.querySelectorAll('.pub-list > li').forEach(function(li) {
      var topics = (li.dataset.topics || '').split(' ');
      li.hidden = isFiltered && !topics.includes(topic);
    });
    // Hide section headers whose list has no visible items
    document.querySelectorAll('main h2').forEach(function(h2) {
      var ol = h2.nextElementSibling;
      if (!ol || !ol.classList.contains('pub-list')) return;
      var hasVisible = Array.from(ol.querySelectorAll('li')).some(function(li) { return !li.hidden; });
      h2.hidden = isFiltered && !hasVisible;
      ol.hidden = isFiltered && !hasVisible;
    });
  }
</script>'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Peer-reviewed publications by Daniel Bischof, including articles in the American Political Science Review, AJPS, BJPS, and Journal of Politics.">
  <title>Publications – Daniel Bischof, Political Scientist</title>
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://www.danbischof.com/publications.html">
  <meta property="og:title" content="Publications – Daniel Bischof">
  <meta property="og:description" content="Peer-reviewed publications by Daniel Bischof, including articles in the American Political Science Review, AJPS, BJPS, and Journal of Politics.">
  <meta property="og:image" content="https://www.danbischof.com/prof_pic.jpg">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="Publications – Daniel Bischof">
  <meta name="twitter:description" content="Peer-reviewed publications by Daniel Bischof, including articles in the American Political Science Review, AJPS, BJPS, and Journal of Politics.">
  <meta name="twitter:image" content="https://www.danbischof.com/prof_pic.jpg">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🏛️</text></svg>">
  <link rel="stylesheet" href="style.css">
  <script src="theme.js"></script>
  <!-- Google Analytics -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-MCGRQHKP21"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-MCGRQHKP21');
  </script>
</head>
<body>

{nav('pub')}

<main>
  <h1>Publications</h1>
  <p class="page-intro">Links per entry (where available): abstract &middot; PDF &middot; journal.</p>

{filter_bar}

{content}
</main>

<footer>
{FOOTER}
</footer>

{SCRIPT}
{filter_script}
</body>
</html>'''

# ── Build working-papers.html ──────────────────────────────────────────────────
def build_wp(entries):
    # Apply title / abstract overrides
    entries = [
        {**e,
         **({'title':    WP_RENAME[e['_key']]}    if e['_key'] in WP_RENAME    else {}),
         **({'abstract': WP_ABSTRACT[e['_key']]}  if e['_key'] in WP_ABSTRACT  else {})}
        for e in entries
    ]

    all_entries = entries

    def wp_group(e):
        """0 = Under Review, 1 = OSF link available, 2 = Available Upon Request"""
        if e['_key'] in WP_UNDER_REVIEW:
            return 0
        if e.get('html', '').strip():
            return 1
        return 2

    def wp_sort_key(e):
        g = wp_group(e)
        if g == 2:
            # Use explicit position; unlisted papers go last
            pos = WP_REQUEST_ORDER.index(e['_key']) if e['_key'] in WP_REQUEST_ORDER else len(WP_REQUEST_ORDER)
            return (g, pos)
        return (g, -int(e.get('year', '0') or 0))

    ordered = sorted(all_entries, key=wp_sort_key)

    total = len(ordered)

    def sec(title, lst, first=False, reset=0):
        items = '\n\n'.join(
            pub_item(e, show_journal=False,
                     under_review=(e['_key'] in WP_UNDER_REVIEW),
                     journal_label='OSF Link')
            for e in lst
        )
        style = f' style="counter-reset: pub-counter {reset}"' if first else ''
        return f'  <h2>{title}</h2>\n  <ol class="pub-list"{style}>\n\n{items}\n\n  </ol>'

    content = sec('Working Papers', ordered, first=True, reset=total+1)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Working papers by Daniel Bischof on democratic defense, extremism, political behavior, and comparative politics. Preprints and papers available upon request.">
  <title>Working Papers – Daniel Bischof, Political Scientist</title>
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://www.danbischof.com/working-papers.html">
  <meta property="og:title" content="Working Papers – Daniel Bischof">
  <meta property="og:description" content="Working papers and preprints by Daniel Bischof on democratic norms, extremism, political behavior, and comparative politics.">
  <meta property="og:image" content="https://www.danbischof.com/prof_pic.jpg">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="Working Papers – Daniel Bischof">
  <meta name="twitter:description" content="Working papers and preprints by Daniel Bischof on democratic norms, extremism, political behavior, and comparative politics.">
  <meta name="twitter:image" content="https://www.danbischof.com/prof_pic.jpg">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🏛️</text></svg>">
  <link rel="stylesheet" href="style.css">
  <script src="theme.js"></script>
  <!-- Google Analytics -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-MCGRQHKP21"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-MCGRQHKP21');
  </script>
</head>
<body>

{nav('wp')}

<main>
  <h1>Working Papers</h1>
  <p class="page-intro">Preprints link to OSF or similar repositories. Papers marked &#8220;available upon request&#8221; can be obtained by email.</p>

{content}
</main>

<footer>
{FOOTER}
</footer>

{SCRIPT}
</body>
</html>'''

# ── Main ───────────────────────────────────────────────────────────────────────
pub_entries = parse_bib(BIB_PUB)
wp_entries  = parse_bib(BIB_WP)
print(f'Parsed: {len(pub_entries)} publications, {len(wp_entries)} working papers')

# Print titles to verify
for e in pub_entries:
    print(f"  [{classify_pub(e)}] {e.get('year','')} — {e.get('title','')[:60]}")

with open(OUT_PUB, 'w', encoding='utf-8') as f: f.write(build_pub(pub_entries))
with open(OUT_WP,  'w', encoding='utf-8') as f: f.write(build_wp(wp_entries))
print('\nDone. Files written.')
