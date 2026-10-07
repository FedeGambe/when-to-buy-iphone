"""Esporta i grafici del notebook: PNG in analisi/img/ (per ANALISI_PREZZI.md) e pagina interattiva analisi/analisi.html."""
import re
from pathlib import Path
import markdown
from utils import calcoli, grafici

cartella = Path(__file__).resolve().parent.parent / "analisi"  # report: .md, img/, .html


def crea_figure(dati):
    return {
        "sconto_per_giorno": grafici.sconto_per_giorno(dati),
        "heatmap_trimestri": grafici.heatmap_trimestri(dati),
        "box_trimestri": grafici.box_trimestri(dati),
        "minimi": grafici.minimi(calcoli.riepilogo_minimi(dati)),
        "costo_attesa": grafici.costo_attesa({m: calcoli.costo_attesa(df) for m, df in dati.items()}),
        "stagionalita": grafici.stagionalita(calcoli.stagionalita_mensile(dati), calcoli.stagionalita_settimanale(dati)),
        "offerte": grafici.offerte(calcoli.profilo_offerte(dati)),
        "effetto_lancio": grafici.effetto_lancio(calcoli.effetto_lancio(dati)),
    }


def esporta(dati):
    (cartella / "img").mkdir(exist_ok=True)
    figure = crea_figure(dati)
    for nome, fig in figure.items():
        fig.write_image(cartella / "img" / f"{nome}.png", width=1100, scale=2)
    # pagina interattiva (layout in src/pagina.html): "# titolo" e paragrafo iniziale vanno in copertina,
    # ogni "## " diventa un capitolo, ogni riga ![..](img/nome.png) il grafico plotly
    md = (cartella / "ANALISI_PREZZI.md").read_text(encoding="utf-8")
    testa, *capitoli = re.split(r"^## ", md, flags=re.M)
    titolo, intro = testa[2:].split("\n", 1)
    corpo, indice, primo = "", "", True
    for i, cap in enumerate(capitoli):
        nome, testo = cap.split("\n", 1)
        parte = "oggi" if nome.startswith("7.") else "analisi" if nome[0].isdigit() else ""  # Conclusione: grigio
        html = ""
        for j, pezzo in enumerate(re.split(r"^!\[[^\]]*\]\(img/(\w+)\.png\)\s*$", testo, flags=re.M)):  # testo, nome, testo, ...
            if j % 2 == 0:
                html += markdown.markdown(pezzo, extensions=["tables"]).replace("<table>", '<div class="tabella"><table>').replace("</table>", "</table></div>")
            else:
                html += "<figure>" + grafici.stile_html(figure[pezzo]).to_html(full_html=False, include_plotlyjs="cdn" if primo else False, config=grafici.CONFIG_HTML) + "</figure>"
                primo = False
        if not parte:
            html = f'<div class="conclusione">{html}</div>'
        corpo += f'<section class="capitolo {parte}" id="c{i}" data-titolo="{nome}" data-parte="{parte}"><h2>{nome}</h2>{html}</section>\n'
        classe = {"": ' class="gruppo-grigio"', "analisi": "", "oggi": ""}[parte]
        link = ' class="oggi-link"' if parte == "oggi" else ""
        indice += f'<li{classe}><a{link} href="#c{i}">{nome}</a></li>'
    pagina = (Path(__file__).parent / "pagina.html").read_text(encoding="utf-8")
    for k, v in {"TITOLO": titolo, "INTRO": markdown.markdown(re.sub(r"\s*Fonte:.*", "", intro.strip())), "INDICE": indice, "CORPO": corpo}.items():
        pagina = pagina.replace(f"@@{k}@@", v)
    (cartella / "analisi.html").write_text(pagina, encoding="utf-8")


if __name__ == "__main__":
    from utils.dati import carica_modello
    esporta({m: carica_modello(m) for m in ["iPhone14", "iPhone15", "iPhone16", "iPhone17"]})
