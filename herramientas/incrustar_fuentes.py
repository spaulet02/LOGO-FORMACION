"""Incrusta Montserrat (normal, negrita, cursiva, negrita cursiva) en un .docx.

Word guarda las fuentes incrustadas ofuscadas (.odttf): los 32 primeros bytes se combinan
con XOR con la clave GUID de la relación. Así el libro se ve con Montserrat aunque el
ordenador no la tenga instalada.
"""
import re
import sys
import uuid
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
VARIANTES = {"embedRegular": "Regular", "embedBold": "Bold", "embedItalic": "Italic", "embedBoldItalic": "BoldItalic"}


def ofuscar(datos, guid):
    clave_hex = guid.replace("-", "")
    clave = bytes(int(clave_hex[i:i + 2], 16) for i in range(30, -1, -2))
    b = bytearray(datos)
    for i in range(32):
        b[i] ^= clave[i % 16]
    return bytes(b)


def main(ruta):
    ruta = Path(ruta)
    tmp = ruta.with_suffix(".tmp.docx")
    with zipfile.ZipFile(ruta) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        nombres = zin.namelist()
        rels_ft = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        embeds = ""
        for i, (tag, var) in enumerate(VARIANTES.items(), 1):
            guid = str(uuid.uuid4()).upper()
            datos = (RAIZ / "assets" / "fuentes" / f"Montserrat-{var}.ttf").read_bytes()
            zout.writestr(f"word/fonts/montserrat{i}.odttf", ofuscar(datos, guid))
            rels_ft += f'<Relationship Id="rIdMont{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/font" Target="fonts/montserrat{i}.odttf"/>'
            embeds += f'<w:{tag} r:id="rIdMont{i}" w:fontKey="{{{guid}}}"/>'
        rels_ft += "</Relationships>"
        fuente = ('<w:font w:name="Montserrat"><w:panose1 w:val="00000500000000000000"/><w:charset w:val="00"/>'
                  '<w:family w:val="auto"/><w:pitch w:val="variable"/>' + embeds + '</w:font>')
        for n in nombres:
            if n.startswith("word/fonts/") or n == "word/_rels/fontTable.xml.rels":
                continue
            data = zin.read(n)
            if n == "word/fontTable.xml":
                x = data.decode("utf-8")
                x = re.sub(r'<w:font w:name="Montserrat">.*?</w:font>', "", x, flags=re.S)
                if 'xmlns:r=' not in x:
                    x = x.replace("<w:fonts ", '<w:fonts xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" ', 1)
                x = x.replace("</w:fonts>", fuente + "</w:fonts>")
                data = x.encode("utf-8")
            elif n == "[Content_Types].xml":
                x = data.decode("utf-8")
                if 'Extension="odttf"' not in x:
                    x = x.replace("<Types ", "<Types ", 1).replace(
                        "</Types>", '<Default Extension="odttf" ContentType="application/vnd.openxmlformats-officedocument.obfuscatedFont"/></Types>')
                data = x.encode("utf-8")
            elif n == "word/settings.xml":
                x = data.decode("utf-8")
                # orden exigido por el esquema (CT_Settings)
                for t in ("embedTrueTypeFonts", "mirrorMargins", "autoHyphenation"):
                    x = x.replace(f"<w:{t}/>", "")
                x = re.sub(r'<w:(consecutiveHyphenLimit|hyphenationZone) w:val="\d+"/>', "", x)
                bloque1 = "<w:embedTrueTypeFonts/><w:mirrorMargins/>"
                bloque2 = '<w:autoHyphenation/><w:consecutiveHyphenLimit w:val="2"/><w:hyphenationZone w:val="425"/>'
                if "<w:displayBackgroundShape/>" in x:
                    x = x.replace("<w:displayBackgroundShape/>", "<w:displayBackgroundShape/>" + bloque1, 1)
                else:
                    x = re.sub(r"(<w:settings[^>]*>)", r"\1" + bloque1, x, count=1)
                if "<w:defaultTabStop" in x:
                    x = re.sub(r"(<w:defaultTabStop[^>]*/>)", r"\1" + bloque2, x, count=1)
                elif "<w:evenAndOddHeaders/>" in x:
                    x = x.replace("<w:evenAndOddHeaders/>", bloque2 + "<w:evenAndOddHeaders/>", 1)
                else:
                    x = x.replace("<w:compat>", bloque2 + "<w:compat>", 1)
                data = x.encode("utf-8")
            zout.writestr(n, data)
        if "word/fontTable.xml" not in nombres:
            raise SystemExit("El documento no tiene fontTable.xml")
        zout.writestr("word/_rels/fontTable.xml.rels", rels_ft)
    tmp.replace(ruta)
    print("Montserrat incrustada en", ruta)


if __name__ == "__main__":
    main(sys.argv[1])
