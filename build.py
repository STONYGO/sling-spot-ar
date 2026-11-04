import pathlib
b = pathlib.Path(__file__).resolve().parent
d = b / 'vendor/node_modules/maplibre-gl/dist'
src = (b / 'src/app.html').read_text()
js = (d / 'maplibre-gl.js').read_text()
css = (d / 'maplibre-gl.css').read_text()
assert '</script' not in js
import datetime, html
lic = (d.parent / 'LICENSE.txt').read_text() if (d.parent / 'LICENSE.txt').exists() else ''
assert '</script' not in lic
build = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime('%Y-%m-%d %H:%M SGT')
src = src.replace('/*MAPLIBRE_LICENSE*/', lic).replace('__BUILD__', build)
out = src.replace('/*MAPLIBRE_JS*/', js).replace('/*MAPLIBRE_CSS*/', css)
(b / 'sling-spot-ar-prototype.html').write_text(out)
print(len(out))
