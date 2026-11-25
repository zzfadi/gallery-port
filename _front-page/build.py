#!/usr/bin/env python3
"""Build the front page of zuabi.dev: ../index.html.

    python3 _front-page/build.py                  rewrites index.html at the root of the site
    python3 _front-page/build.py --preview DIR    also writes a standalone copy to DIR (its archive links point at the live site)

Reads   template.html     the stage, the wafer, the archive column and the script
        pages/<key>.html  the five pages: a <style> block, then the page's markup
        ../config.json    the gallery's page list: one archive tile per page
        ../home/          pictures, archive thumbnails and fonts, used in place
Needs only Python 3.
"""
import re, shutil, pathlib, html, sys, json

HERE = pathlib.Path(__file__).resolve().parent
SITE = HERE.parent
HOME = SITE / 'home'

# key (also the #name in the address), css class, title, paper colours for the roll under the page (light, mid, dark)
PAGES = [
 ("nine-layers",     "pg-layers",  "Nine layers",     ("#FFFFFF", "#C9D3E2", "#8793A8")),
 ("objects",         "pg-objects", "Objects",         ("#3C7565", "#1D4439", "#0B1F1A")),
 ("in-my-own-words", "pg-words",   "In my own words", ("#FFFFFF", "#DCDFE6", "#A4A9B6")),
 ("whos-asking",     "pg-asking",  "Who’s asking?",   ("#FFEA94", "#F2C21F", "#A67F00")),
 ("maker-and-user",  "pg-maker",   "Maker and user",  ("#74406F", "#451C43", "#200A1F")),
]

FONTS = [  # family, weight, style, file in home/fonts
 ("Bricolage Grotesque", "200 800", "normal", 'bricolage-grotesque.woff2'),
 ("Barlow", "400", "normal", 'barlow-400.woff2'),
 ("Barlow", "500", "normal", 'barlow-500.woff2'),
 ("Barlow", "600", "normal", 'barlow-600.woff2'),
 ("Barlow Condensed", "600", "normal", 'barlow-condensed-600.woff2'),
 ("Epilogue", "100 900", "normal", 'epilogue.woff2'),
 ("Newsreader", "200 800", "normal", 'newsreader.woff2'),
 ("Newsreader", "200 800", "italic", 'newsreader-italic.woff2'),
 ("Figtree", "300 900", "normal", 'figtree.woff2'),
]

# A page on the site that is not part of the gallery. It joins the archive at the end, so everything stays reachable.
EXTRA = [{'id': 'coflow-privacy', 'design': 'CoFlow', 'model': 'About and privacy', 'date': '2026-10', 'href': 'coflow-privacy.html'}]

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
def when(d):
    m = re.fullmatch(r'(\d{4})-(\d{2})', d or '')
    return f'{MONTHS[int(m.group(2)) - 1]} {m.group(1)}' if m else ''

def scope_css(css, cls):
    out = []
    for m in re.finditer(r'([^{}]+)\{([^{}]*)\}', css):
        sel, decl = m.group(1).strip(), m.group(2).strip()
        if sel in ('body', '*'):
            continue
        sels = [s.strip() for s in sel.split(',')]
        generic = {'h1','h2','h3','p','ul','ol','figure','blockquote','img'}
        if set(sels) <= generic and 'font-family' not in decl:
            continue                                    # resets live in the shared block
        if sels in (['a'], ['a:hover']) and decl in ('color:inherit;text-underline-offset:3px', 'text-decoration-thickness:2px'):
            continue
        out.append(','.join(f'.{cls} {s}' for s in sels) + '{' + decl + '}')
    return '\n'.join(out)

def page_parts(key, prefix):
    t = (HERE / 'pages' / f'{key}.html').read_text(encoding='utf-8')
    css = t[t.index('<style>') + 7:t.index('</style>')]
    body = t[t.index('</style>') + 8:].strip()
    used = set(re.findall(r'home/media/([\w.-]+)', body))
    if prefix != 'home/': body = body.replace('home/media/', prefix + 'media/')
    body = body.replace('<img ', '<img loading="lazy" decoding="async" ')
    return body, css, used

def gallery_pages():
    cfg = json.loads((SITE / 'config.json').read_text(encoding='utf-8'))
    return [{'id': m['id'], 'design': d['label'], 'model': m['model'], 'date': m.get('date', ''), 'path': m['path']}
            for cat in cfg['categories'] for d in cat['designs'] for m in d['models']]

def build(out, site):
    """site=True: index.html at the root of the site (assets under home/, archive links to gallery.html).
       site=False: a standalone copy in `out` (assets beside it, archive links to the live zuabi.dev)."""
    prefix = 'home/' if site else ''
    a = html.escape
    tpl = (HERE / 'template.html').read_text(encoding='utf-8')
    items = gallery_pages()
    cards, scoped, media, skip = [], [], set(), []
    for key, cls, title, (p1, p2, p3) in PAGES:
        body, css, used = page_parts(key, prefix)
        media |= used
        scoped.append(f'/* {title} */\n' + scope_css(css, cls))
        skip.append(f'<a href="#{key}">{a(title)}</a>')
        cards.append(
            f'<section class="card" id="{key}" data-key="{key}" aria-label="{a(title)}" style="--p1:{p1};--p2:{p2};--p3:{p3}">\n'
            f'<div class="pool"></div>\n'
            f'<div class="clip"><div class="page {cls}">\n{body}\n</div><div class="fog"></div><div class="curl"></div></div>\n'
            f'<div class="roll"></div>\n</section>')
    tiles = []
    for it in items + EXTRA:
        if 'href' in it:
            href = ('' if site else 'https://zuabi.dev/') + it['href']
            label = f"{it['design']}: {it['model'].lower()}"
        else:
            href = ('gallery.html#' if site else 'https://zuabi.dev/#') + it['id']
            label = f"{it['design']}, by {it['model']}" + (f", {when(it['date'])}" if when(it['date']) else '')
        src = f' data-src="{a(it.get("href") or it["path"])}"' if site else ''   # on the site a tile opens its page in place
        tiles.append(
            f'<a class="tile" href="{href}"{src} data-design="{a(it["design"])}" data-model="{a(it["model"])}" data-date="{a(it["date"])}" aria-label="{a(label)}">'
            f'<img src="{prefix}media/archive/{it["id"]}.webp" alt="" width="640" height="400" loading="lazy" decoding="async">'
            f'<span>{a(it["design"])}, {a(it["model"])}</span><i></i></a>')
    faces = '\n'.join(
        f"@font-face{{font-family:'{fam}';src:url('{prefix}fonts/{dst}') format('woff2');font-weight:{w};font-style:{st};font-display:swap}}"
        for fam, w, st, dst in FONTS)
    ids = [it['id'] for it in items]
    start = ids.index('terminal-opus') if 'terminal-opus' in ids else 0
    doc = (tpl.replace('/*@FONT_FACES@*/', faces)
              .replace('/*@SCOPED_CSS@*/', '\n'.join(scoped))
              .replace('<!--@CARDS@-->', '\n\n'.join(cards))
              .replace('<!--@TILES@-->', '\n'.join(tiles))
              .replace('<!--@SKIP@-->', '\n'.join(skip))
              .replace('/*@TITLE@*/', 'Fadi Zuabi' if site else 'Fadi Zuabi: five ways in')
              .replace('/*@ICON@*/', 'favicon.svg' if site else 'data:,')
              .replace('/*@SITE@*/false', 'true' if site else 'false')
              .replace('/*@OLD_IDS@*/[]', json.dumps(ids) if site else '[]')
              .replace('/*@START_TILE@*/0', str(start)))
    assert '@*/' not in doc and '<!--@' not in doc, 'placeholder left in the page'
    thumbs = [HOME / 'media/archive' / f"{it['id']}.webp" for it in items + EXTRA]
    missing = [str(p.relative_to(SITE)) for p in thumbs if not p.exists()]
    if missing:
        sys.exit('No thumbnail for: ' + ', '.join(missing) + '\nSave a 640x400 WebP screenshot of each page under that name, then run the build again.')
    missing = [str(p.relative_to(SITE)) for p in [HOME / 'media' / f for f in sorted(media)] + [HOME / 'fonts' / f[3] for f in FONTS] if not p.exists()]
    assert not missing, 'missing files: ' + ', '.join(missing)
    if site:
        out = SITE
    else:
        out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
        for d in ('media', 'fonts'):
            if (out / d).exists(): shutil.rmtree(out / d)
            shutil.copytree(HOME / d, out / d)
    (out / 'index.html').write_text(doc, encoding='utf-8')
    print(f"{out / 'index.html'}: {len(doc.encode())} bytes; {len(PAGES)} pages, {len(media)} pictures, {len(items + EXTRA)} archive tiles, {len(FONTS)} fonts")

if __name__ == '__main__':
    build(None, site=True)
    if '--preview' in sys.argv:
        build(sys.argv[sys.argv.index('--preview') + 1], site=False)
