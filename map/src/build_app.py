"""Bake the land map into the Corujeira app (repo acorujeira/flora) as map/."""
import re, os, shutil
APP = '/home/claude/flora'
h = open('site/index.html').read()
h = h.replace('"plates/', '"../plates/')
h = h.replace('<button id="btn-index">places</button>', '<button id="btn-index">places</button>\n  <a href="../">plants</a>')
h = h.replace('<a class="wide" href="https://winternest.acorujeira.pt">stay</a>\n', '')
h = h.replace('<link rel="preconnect"', '<link rel="manifest" href="../manifest.webmanifest">\n<meta name="theme-color" content="#E4DDC5">\n<link rel="apple-touch-icon" href="../icons/apple-touch-icon.png">\n<link rel="preconnect"', 1)
h = h.replace('</body>', '''<script>
/* Part of the Corujeira app: the service worker at the app root keeps this page and its photos for use with no signal. */
if ("serviceWorker" in navigator) addEventListener("load", () => navigator.serviceWorker.register("../sw.js", { scope: "../" }).catch(() => {}));
</script>
</body>''')
assert 'href="../"' in h and '../sw.js' in h
open(f'{APP}/map/index.html', 'w').write(h)
used = sorted(set(re.findall(r'img/[\w.-]+\.jpg', h)))
for f in os.listdir(f'{APP}/map/img'):
    if 'img/' + f not in used: os.remove(f'{APP}/map/img/' + f)
for u in used: shutil.copy('site/' + u, f'{APP}/map/' + u)
for p in re.findall(r'\.\./plates/([\w.-]+\.webp)', h):
    assert os.path.exists(f'{APP}/plates/{p}'), p
# sources, so the map can be rebuilt (the Flora Sheet snapshot is fetched at build time and never committed)
for f in ['build3.py', 'build_app.py', 'template3.html', 'land.json', 'canopy.jpg']:
    shutil.copy(f, f'{APP}/map/src/' + f)
print('map ok', len(h), 'images', len(used))
