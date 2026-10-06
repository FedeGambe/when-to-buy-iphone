"""Copertina a schermo intero di analisi.html: tramonto retrò su griglia in prospettiva.
Ispirata allo stile `orizzonte` della libreria copertine, adattata al tema. `python src/copertina.py` la rigenera in src/pagina.html."""
import re
from pathlib import Path

from copertine import favicon_uri
from copertine.palette import PALETTE, mescola

W, H = 1600, 900
p = PALETTE["retro"]
a = p["acc"]


def svg():
    y0, R, cx = 770, 215, W // 2
    sole = (f'<linearGradient id="sl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{a[2]}"/><stop offset="1" stop-color="{a[0]}"/></linearGradient>'
            f'<circle cx="{cx}" cy="{y0-R*.5:.0f}" r="{R}" fill="url(#sl)"/>')
    strisce = "".join(f'<rect x="{cx-R}" y="{y0-R*.5+R*(.1+i*.09):.0f}" width="{2*R}" height="{R*.02*(i+1):.1f}" fill="{p["sfondo"]}"/>' for i in range(5))
    terra = f'<rect y="{y0}" width="{W}" height="{H-y0}" fill="{mescola(p["sfondo"], "#000000", .35)}"/>'
    raggi = "".join(f'<line x1="{W/2}" y1="{y0}" x2="{W/2+(i-9)*W*.14:.0f}" y2="{H}" stroke="{a[3]}" stroke-width="2.5"/>' for i in range(19))
    righe = "".join(f'<line x1="0" y1="{y0+(H-y0)*(k/7)**2:.0f}" x2="{W}" y2="{y0+(H-y0)*(k/7)**2:.0f}" stroke="{a[3]}" stroke-width="2.5"/>' for k in range(1, 8))
    grana = ('<filter id="grana"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2"/>'
             '<feColorMatrix values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 .55 0"/></filter>')
    return (f'<svg class="bauhaus" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMax slice" aria-hidden="true">'
            f'<defs>{grana}</defs><rect width="{W}" height="{H}" fill="{p["sfondo"]}"/>{sole}{strisce}{terra}{raggi}{righe}'
            f'<rect width="{W}" height="{H}" filter="url(#grana)" opacity=".35"/></svg>')


CSS = """/* Copertina a schermo intero: l'illustrazione riempie lo schermo, titolo in alto a tutta larghezza, diciture in basso */
.copertina{position:relative; display:flex; flex-direction:column; justify-content:space-between; height:100svh; min-height:560px; overflow:hidden;
  background:#14161f; color:#efe3c8; --margine:max(20px, calc(50vw - 640px))}
.bauhaus{position:absolute; inset:0; width:100%; height:100%; z-index:0}
.slide-testa{position:relative; z-index:1; padding:calc(var(--barra) + clamp(16px,3vw,48px)) var(--margine) 0;
  opacity:calc(1 - 1.3 * var(--p,0)); transform:translateY(calc(var(--p,0) * 40px))}
.slide-testa h1{letter-spacing:-.02em; font-size:clamp(2.2rem,6.4vw,5.2rem); text-wrap:pretty;
  transform-origin:left bottom; transform:scale(calc(1 - .3 * var(--p,0)))}
.copertina .sottotitolo{font-size:clamp(1rem,1.7vw,1.35rem); margin:14px 0 0; color:#d9ccaf}
.copertina .sottotitolo p{margin:0}
.copertina .sottotitolo strong{color:#efe3c8}
.info{position:relative; z-index:1; display:flex; flex-wrap:wrap; justify-content:space-between; gap:12px 32px; padding:48px var(--margine) 18px;
  background:linear-gradient(transparent, #14161fd9 60%); font-size:.9rem; line-height:1.45}
.info b{font-family:var(--f-display); font-weight:800; font-size:1.05rem}

"""

pagina = Path(__file__).with_name("pagina.html")
s = pagina.read_text(encoding="utf-8")
i, j = s.index("/* Copertina"), s.index("/* Tabelle e grafici */")
s = s[:i] + CSS + s[j:]
i = s.index('<svg class="bauhaus"')
j = s.index('<a class="logo-cover"', i)  # tutto ciò che sta tra l'inizio dell'svg e il logo
s = s[:i] + svg() + s[j:]
s = re.sub(r'(<link rel="icon" type="image/svg\+xml" href=")[^"]*"', lambda m: m.group(1) + favicon_uri("orizzonte", "retro") + '"', s, count=1)
pagina.write_text(s, encoding="utf-8")
print("copertina rigenerata")
