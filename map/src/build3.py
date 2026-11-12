"""Public land map: QGIS geometry + place copy + photos + Flora plant cards -> site/index.html"""
import json, re, base64, io, os, shutil, math
from PIL import Image, ImageFilter, ImageChops

D = json.load(open('land.json'))
D.pop('canopy', None)
D['slope'] = [[91.8, 18.1], [99.9, 23.3], [101.6, 25.3], [99.9, 31.0], [94.4, 39.5], [82.5, 50.8], [75.6, 53.0], [64.4, 54.7], [59.7, 57.1], [56.1, 60.2], [38.7, 81.2], [33.7, 90.1], [33.2, 95.3], [33.9, 100.2], [32.5, 100.7], [31.0, 100.1], [19.9, 87.1], [15.5, 75.1], [18.3, 52.8], [24.8, 37.1], [25.9, 35.9], [29.7, 34.5], [38.5, 33.6], [72.5, 27.1], [81.5, 23.5], [88.7, 18.2], [91.8, 18.1]]

# electrical cabinet, 0.6 x 1.2 m, on the outside of the Clayhouse's north wall at its west corner
c0 = (106.3, 51.9); c1 = (112.0, 53.9)
L = math.hypot(c1[0]-c0[0], c1[1]-c0[1]); u = ((c1[0]-c0[0])/L, (c1[1]-c0[1])/L); n = (-u[1], u[0])
if n[1] > 0: n = (-n[0], -n[1])  # point north, away from the house
P = lambda a, b: [round(c0[0]+u[0]*a+n[0]*b, 2), round(c0[1]+u[1]*a+n[1]*b, 2)]
D['cabinet'] = [P(0, 0), P(1.2, 0), P(1.2, 0.6), P(0, 0.6), P(0, 0)]

# canopy wash from the QGIS canopy screen, baked onto the clay ground
im = Image.open('canopy.jpg').convert('RGB')
im = im.point([round(255*(i/255)**2.1) for i in range(256)]*3).filter(ImageFilter.GaussianBlur(1.6))
im = ImageChops.multiply(im, Image.new('RGB', im.size, (228, 221, 197)))
buf = io.BytesIO(); im.save(buf, 'JPEG', quality=80)
CANOPY = 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()

# ---------------- plants: Flora sheet + botanical plates ----------------
rows = json.load(open('flora_rows.json')); H = rows[0]
FL = {}
for r in rows[1:]:
    d = dict(zip(H, r + ['']*(len(H)-len(r))))
    k = d['Scientific name'].strip().lower()
    if k and k not in FL: FL[k] = d
PL = json.load(open('/home/claude/acorujeira/flora/plates.json'))
slug = lambda s: re.sub(r'[^a-z0-9]+', '-', s.lower().replace('×', 'x')).strip('-')
MON = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
def months(a, b):
    try: return f'{MON[int(a)]} to {MON[int(b)]}' if a and b else ''
    except: return ''
os.makedirs('site/plates', exist_ok=True)
PLANTS = {}
for k in ['trees', 'shrubs', 'herbs']:
    for p in D[k]:
        sci = (p.get('plant_name') or '').strip()
        if not sci or sci in PLANTS: continue
        f = FL.get(sci.lower(), {})
        s = slug(sci); g = s.split('-')[0]
        key = s if s in PL else (None if g == 'salvia' else (next((x for x in (g+'-sp', ) if x in PL), None) or next((x for x in PL if x.startswith(g+'-')), None)))
        plate = None
        if key:
            rec = PL[key]; src = '/home/claude/acorujeira/flora/' + rec['url']
            if os.path.exists(src):
                dst = 'plates/' + os.path.basename(rec['url']); shutil.copy(src, 'site/' + dst)
                plate = {'src': dst, 'credit': ', '.join(x for x in [rec.get('artist'), rec.get('licence') or rec.get('credit')] if x),
                         'page': rec.get('page', ''), 'genus': key != s}
        info = [
            ('Family', f.get('Family')), ('Native to', f.get('Native range')), ('Layer', f.get('Layer')),
            ('Size', ' × '.join(x for x in [f.get('Height (m)') and f.get('Height (m)')+' m tall', f.get('Spread (m)') and f.get('Spread (m)')+' m wide'] if x)),
            ('Light', f.get('Light')), ('Water', f.get('Moisture')), ('Life', ', '.join(x for x in [f.get('Life cycle'), f.get('Leaves')] if x)),
            ('Flowers', months(f.get('Flower start (month)'), f.get('Flower end (month)'))),
            ('Roles', f.get('Functions')), ('Edible', f.get('Edible parts')), ('Caution', f.get('Toxic parts')),
        ]
        PLANTS[sci] = {'common': (f.get('Common name') or p.get('plant_common') or '').strip(), 'sci': sci,
                       'colour': f.get('Flower colour', ''), 'plate': plate, 'info': [[a, b] for a, b in info if b]}
print('plants', len(PLANTS), 'with flora', sum(1 for v in PLANTS.values() if v['info']), 'with plate', sum(1 for v in PLANTS.values() if v['plate']))

# ---------------- places ----------------
WN = {'t': 'Winter Nest', 'u': 'https://winternest.acorujeira.pt'}
LAB = {'t': 'More in the Lab', 'u': 'https://lab.acorujeira.pt'}
I = lambda n: 'img/' + n

PLACES = [
 dict(id='entrance', name='The Entrance', sub='a living portal', x=72.0, y=133.0, a='e', major=1, hit=dict(circle=[72.0, 133.0, 4]),
  body=["A metal trellis stands at the north end of the parking area, where the path enters the oak forest. Jannis welded it here on the land from rebar, about four metres tall.",
        "The plan is to cover it with chayote in its first year and to train grapevines in as its long-term frame, a nod to the vineyard these terraces once held."],
  link={'t': 'Made by Jannis', 'u': 'https://www.instagram.com/jannis.flow/'}),
 dict(id='oaks', name='The Old Oaks', sub='the oldest trees on the land', x=100.5, y=100.5, a='w', major=1, hit=dict(circle=[100.5, 100.5, 6.5]), spirit='The old oaks',
  body=["The lower half of the land is oak forest, recovering since the fires of 2010.",
        "We look after it gently. We thin the trees to deal with fungal disease and to let more light reach the forest floor, repair the old terraces where they were eroding, and build small earthworks that hold water in the slope.",
        "Under the oaks we are planting a woodland garden of shade-loving plants, to bring back diversity and soil life."],
  draw=[(I('map-woodland.jpg'), 'Planning base for the woodland garden under the oaks, drawn in QGIS')]),
 dict(id='van', name='Bertha', label='bertha', sub='a red Ford Transit, parked for good', x=64.9, y=103.0, a='e', hit=dict(buildings=['campervan']),
  photos=[I('web-van.jpg'), I('van-2.jpg'), I('van-3.jpg')],
  body=["Bertha has retired from the road and stays on the land as a cosy room for short stays."]),
 dict(id='creek', name='The Creek', sub='the mother of the land', x=114, y=92, a='e', major=1, hit=dict(river=1, ponds=['Creek pool · lower', 'Creek pool · sauna']), spirit='The creek',
  photos=[I('creek-1.jpg'), I('creek-2.jpg'), I('creek-3.jpg'), I('creek-4.jpg')],
  body=["The creek runs along the eastern edge of the land, with small pools held along its bed. The sauna sits beside it, and the creek is the cold after the heat.",
        "When the water silo runs low, a small pump lifts creek water up to it."]),
 dict(id='kitchen', name='The Kitchen', sub='shared by everyone on the land', x=104.3, y=94.2, a='s', hit=dict(buildings=['Kitchen']),
  photos=[I('kitchen-1.jpg')],
  body=["The communal kitchen sits just below the yurt. Everyone living on the land cooks and eats here, and sparkling spring water runs from the tap.",
        "Each day starts with a check-in, and every new arrival gets a warm orientation."]),
 dict(id='lamppost', name='The Lamp Post', label='lamp post', sub='news carried in light', x=86.3, y=88.4, a='w', hit=dict(circle=[86.3, 88.4, 3.5]),
  photos=[I('web-lamp.jpg')],
  body=["The lamp post by the path carries the land's most important news. It pulses red when a fire is close or upwind of us, orange when the battery runs low, and blue when the water silo runs low. Anyone walking past knows, phone in pocket.",
        "Fire season is part of the year here. In the summer of 2025 we watched the Gerês mountains burn from the hill above the yurt.",
        "The signals come from Vigia, our fire watch, and the land dashboard, both running on Home Assistant. The dashboard hangs on the kitchen wall and lives on our phones; its cards are open source."],
  draw=[(I('lab-dashboard-card.jpg'), 'The land dashboard: weather, fire risk, water, power and air on one screen')], link=LAB),
 dict(id='yurt', name='The Yurt & the Perch', label='yurt & the perch', sub='a winter nest space', x=100.5, y=89.5, a='w', major=1, hit=dict(buildings=['Yurt', 'Deck']),
  photos=[I('yurt-2.jpg'), I('yurt-1.jpg'), I('lab-yurt-ext-outside.jpg'), I('yurt-5.jpg'), I('yurt-3.jpg'), I('yurt-7.jpg')],
  body=["A seven-metre Mongolian yurt with an egg-shaped wood burner, and the Perch, an extension Eska built by hand in summer 2026. The Perch is glazed with glass salvaged from a friend's project, and its vaulted roof cuts into the yurt's own radius.",
        "Like most new buildings on the land, it is clad in charred boards. We char them the Japanese way, called yakisugi, in a chimney of three boards tied together and stood on end. The fire takes the surface and leaves a skin of carbon that protects the wood from sun and rain. The sauna was our first try, in 2024."],
  draw=[(I('lab-yurt-ext-model.jpg'), 'The Perch modelled in Rhino'), (I('lab-yurt-ext-line.jpg'), 'Line drawing of the frame'), (I('lab-yurt-ext-frame.jpg'), 'Frame study')], link=WN),
 dict(id='woodshed', name='The Woodshed', sub='a reciprocal arch', x=99.7, y=79.4, a='e', hit=dict(buildings=['wood storage']),
  photos=[I('woodshed-1.jpg'), I('woodshed-2.jpg'), I('woodshed-3.jpg')],
  body=["The woodshed sits on the terrace above the yurt, against an old stone wall, close to all three wood stoves. Its frame holds itself up: short timbers rest on one another in a woven pattern, after the self-supporting bridges Leonardo da Vinci sketched.",
        "We worked out the geometry in code before cutting any wood. It is roofed with charred cryptomeria shingles and holds about four and a half cubic metres of firewood."],
  draw=[(I('lab-woodshed-model.jpg'), 'The arch in 3D, coloured by layer'), (I('lab-woodshed-tool.jpg'), 'The calculator that sets each strip and angle'), (I('lab-woodshed-runner.jpg'), 'Cut sheet for a runner')], link=LAB),
 dict(id='workshop', name='The Workshop', sub='where most things get made', x=83.6, y=71.2, a='n', major=1, hit=dict(buildings=['workshop']),
  photos=[I('workshop-1.jpg'), I('lab-workshop-card.jpg'), I('lab-lantern-lit.jpg'), I('workshop-2.jpg')],
  body=["A sheltered workshop of about 37 m² on the terrace above the yurt, with a welder, a table saw and a wall of tools. It began as a small roundwood shelter, was closed in during autumn 2025 and grew by another six by five metres in 2026.",
        "The frame is eucalyptus from the land, and the studs are offcuts from a local lumber yard.",
        "In 2026 Eska made seventeen wooden lamps here, each sketched by hand, modelled in Rhino, laser-cut from plywood and wired by hand. With Anca, they are becoming lanterns of 266 LEDs that simulate fire and respond to music."],
  draw=[(I('lab-lantern-rhino.jpg'), 'Lantern model in Rhino'), (I('lab-lantern-cut-sheets.jpg'), 'Laser-cut sheets for the lamp ribs')], link=LAB),
 dict(id='nursery', name='The Nursery', sub='the next forest, in pots', x=76.3, y=72.1, a='w', hit=dict(nursery=1),
  body=["Seedlings and cuttings raised on the land, waiting for their place in the firebreak and the woodland garden."]),
 dict(id='spring', name='The Breathing Spring', label='the spring', sub='seasonal, for now', x=57.5, y=70.5, a='w', major=1, hit=dict(spring=1, ponds=['Spring pond', 'Spring pond · lower pool']), spirit='The Shrine of the Breathing Spring',
  body=["The spring once ran all year. Since the 2010 fire, on ground already worn down by eucalyptus, it runs for only part of it.",
        "Raising the water table so that it flows all year again is one of the main goals behind the planting across the land, alongside more diversity and more water held in the soil."],
  draw=[(I('map-spring.jpg'), 'Water map of the slope above the spring: where water gathers and sinks in')]),
 dict(id='firebreak', name='The Living Firebreak', label='the firebreak', sub='eucalyptus giving way to food forest', x=40.0, y=80.0, a='w', major=1, hit=dict(slope=1), spirit='The eucalyptus forest',
  photos=[I('web-f44.jpg'), I('web-f62.jpg'), I('web-f97.jpg'), I('web-f186.jpg'), I('firebreak-1.jpg')],
  body=["A power line crosses the top of the land through a slope of eucalyptus regrowth, which in a dry summer would carry fire up to the wires. We are replacing it, patch by patch, with a low, fire-resistant food forest.",
        "At the first Owl's Nest gathering, in October 2025, we felled about 70 eucalyptus along the contours and laid the trunks and branches across the slope to hold water and soil. Then we planted around 150 trees and shrubs: strawberry tree, wild olive, elder, lavender and rosemary along the outer edge, and small mixed groups behind.",
        "There is no drip irrigation on the slope, only a hose for the worst of the drought. Over 70% came through the first year.",
        "The slope is also becoming a gallery of land art made from its own wood, starting with a large owl by Sarah Duryea and Morley."],
  draw=[(I('map-firebreak.jpg'), 'Water map of the eucalyptus slope, with the October 2025 planting')]),
 dict(id='belltent', name='Bell Tent Terrace', sub='a round platform, seven metres across', x=25.9, y=81.4, a='w', hit=dict(platform=1),
  photos=[I('belltent-1.jpg')],
  body=["A circular terrace levelled for a bell tent at the western edge of the land."]),
 dict(id='reservoir', name='The Old Reservoir', sub='a dry granite ring', x=90.7, y=51.7, a='n', hit=dict(reservoir=1),
  body=["A former water reservoir, now an empty ring of granite wall about sixty centimetres thick."]),
 dict(id='silo', name='The Water Silo', label='water silo', sub='five thousand litres', x=89.7, y=16.3, a='e', hit=dict(storage=1),
  photos=[I('silo-2.jpg')],
  body=["The land's water is stored in a 5,000 litre silo at the top of the footpath. A sensor in its lid reports the level to the land dashboard.",
        "When the level drops below 1,000 litres and the battery is above 80%, the creek pump starts by itself. It runs until the silo is full or the battery falls to 60%."]),
 dict(id='toilet', name='The Poop Shrine', label='the poop shrine', sub='a compost toilet', x=98.5, y=54.9, a='w', hit=dict(buildings=['compost toilet']),
  photos=[I('lab-shrine-outside.jpg'), I('lab-shrine-inside.jpg')],
  body=["A compost toilet on the slope above the Clayhouse, built by Eska in summer 2026 from scrap wood, clad in charred boards and roofed with salvaged flashing. An almond-shaped window lights the inside."],
  draw=[(I('lab-shrine-model.jpg'), 'Modelled in Rhino'), (I('lab-shrine-drawing.jpg'), 'Frame and parts')]),
 dict(id='cabinet', name='The Power Cabinet', label='power cabinet', sub='the off-grid system', x=106.7, y=51.0, a='w', hit=dict(cabinet=1),
  body=["This small cabinet on the north wall of the Clayhouse holds the land's power and internet. There is no grid connection.",
        "Eight solar panels on the Clayhouse roof, 3,480 W in two arrays, charge a 48 V lithium battery bank of about 9.6 kWh through two Victron solar chargers. A Victron MultiPlus-II turns that into ordinary 230 V for the land, and a generator stands by as backup.",
        "A Starlink dish on the roof brings the internet. A router, Home Assistant and the solar monitor share the cabinet, and a single access point carries the Wi-Fi to the yurt."],
  diagram=1),
 dict(id='clayhouse', name='The Clayhouse', label='the clayhouse', sub='a winter nest space', x=107.9, y=54.6, a='n', major=1, hit=dict(buildings=['clayhouse'], solar=1),
  photos=[I('clayhouse-1.jpg'), I('clayhouse-2.jpg'), I('clayhouse-3.jpg')],
  body=["A naturally built tiny house, designed by Eska with clay work by Lea, from locally sourced and salvaged materials. It is one of the two spaces held through the winter, with a wood stove and a desk by the corner window.",
        "The solar panels on its roof power the whole land."], link=WN),
 dict(id='garden', name='The Medicinal Garden', label='medicinal garden', sub='planted with Leonie of Millefolium', x=116.2, y=61.2, a='s', major=1, hit=dict(beds_near=[116, 60, 9]),
  photos=[I('web-herbs.jpg'), I('garden-1.jpg'), I('garden-2.jpg'), I('garden-3.jpg'), I('garden-4.jpg')],
  body=["When we arrived these terraces were thick with brambles. Over five years we cleared them back, cultivated the soil, and added carbon and manure from neighbours' animals to rebuild fertility. Over twenty medicinal plants now grow in their place.",
        "Where the terraces were eroding, we rebuilt them by digging and by laying prunings and other biomass on contour along their outer edges, which builds the soil back up.",
        "They go into the steam ceremonies in the sauna below, into tea, and onto the skin. Look and smell as much as you like; please ask before picking anything.",
        "Each dot on the map is a plant. Tap one to meet it."],
  link={'t': 'Ask the garden', 'u': 'https://garden.acorujeira.pt'}),
 dict(id='sauna', name='The Sauna', sub='steam in the banya tradition', x=124.6, y=59.8, a='e', major=1, hit=dict(buildings=['sauna']), spirit='The sauna',
  photos=[I('sauna-1.jpg'), I('sauna-2.jpg'), I('sauna-3.jpg'), I('sauna-4.jpg')],
  body=["A wood-fired sauna beside the creek, seating eight. Eska designed it and built it by hand with Omali and Damien, from Japanese cedar they planed themselves.",
        "It is home to Steamology: guided steam ceremonies in the Russian banya tradition, moving through heat, steam, whisking with leafy brooms and the cold of the creek. Over a hundred ceremonies have been held here since 2024."],
  draw=[(I('lab-sauna-model-line.jpg'), 'The egg-shaped sauna, drawn in Rhino'), (I('lab-sauna-model-night.jpg'), 'Rendered at night'), (I('lab-sauna-parts.jpg'), 'Parts laid out for cutting')],
  link={'t': 'Private sessions', 'u': 'https://acorujeira.pt'}),
]

# spirit offerings from the Owl's Nest signs (Almanac, owls-nest)
t = open('/home/claude/knowledge/subjects/owls-nest.md').read()
SP = {}
for m in re.finditer(r'^- \*\*(.+?)\*\*[:,]?\s*(.*)$', t, re.M):
    txt = re.sub(r'\s*\(see \[\[[a-z-]+\]\]\)', '', m.group(2)).strip(' :,')
    SP[m.group(1)] = txt[:1].upper() + txt[1:]
out = []
for p in PLACES:
    q = dict(p); q.setdefault('photos', []); q.setdefault('draw', []); q.setdefault('label', None); q.setdefault('major', 0)
    if p.get('spirit'): q['spirit'] = {'name': p['spirit'], 'text': SP[p['spirit']]}
    q['draw'] = [{'src': s, 'cap': c} for s, c in q['draw']]
    for s in q['photos'] + [d['src'] for d in q['draw']]:
        assert os.path.exists('site/' + s), s
    out.append(q)

INTRO = {
 'story': ["These terraces were probably built by the village in the 16th or 17th century, to grow maize. Granite pillars still stand from a vineyard that came later. The family who inherited the land planted eucalyptus as a cash crop and later emigrated, and in 2010 the land burned.",
           "It is a pattern found across much of rural Portugal. We are working through it slowly: turning the upper half from eucalyptus into a food forest and firebreak, and tending the oak forest on the lower half back to health."],
 'map': ["Every plant on this map was surveyed with centimetre-precision GNSS, photographed where it stands and identified through a PlantNet plugin for QGIS that Eska wrote. The plant cards come from Flora, our plant database; most botanical plates are public domain."],
}

def clean(o):
    if isinstance(o,str): return re.sub(r'(\d)\s*\u2013\s*(\d)', r'\1 to \2', o).replace('\u2013','-').replace('\u2014',',')
    if isinstance(o,list): return [clean(x) for x in o]
    if isinstance(o,dict): return {k:clean(v) for k,v in o.items()}
    return o
PLANTS = clean(PLANTS)
blob = json.dumps(out, ensure_ascii=False) + json.dumps(INTRO, ensure_ascii=False) + json.dumps(PLANTS, ensure_ascii=False)
# Words the public map must never contain. The private part of the list (place names, unreleased
# projects) stays out of this public repo: keep it in banned_words.txt beside this script, one term per line.
BANNED = ['—', '–', 'TODO', 'no generator'] + [l.strip() for l in open('banned_words.txt', encoding='utf-8') if l.strip() and not l.startswith('#')]
assert len(BANNED) > 4, 'banned_words.txt is missing its terms'
for bad in BANNED:
    assert bad.lower() not in blob.lower(), bad

html = open('template3.html').read()
html = (html.replace('__DATA__', json.dumps(D, separators=(',', ':')))
            .replace('__PLACES__', json.dumps(out, ensure_ascii=False))
            .replace('__INTRO__', json.dumps(INTRO, ensure_ascii=False))
            .replace('__PLANTS__', json.dumps(PLANTS, ensure_ascii=False))
            .replace('__CANOPY__', CANOPY))
open('site/index.html', 'w').write(html)
print('ok', len(html), 'places', len(out))
