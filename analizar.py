import csv
import os
import sys
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from html import escape, unescape
from pathlib import Path

CAMPOS = ("imdb", "title", "year", "budget", "domgross")
RAIZ = Path(__file__).resolve().parent
ESTUDIANTE = "soledado"


def dinero(texto):
    if texto.strip() in ("", "NA", "#N/A"):
        return None
    valor = Decimal(texto)
    if not valor.is_finite() or valor < 0:
        raise ValueError
    return valor


def validar(archivo):
    lector = csv.DictReader(archivo, strict=True)
    filas = []
    ids = set()
    try:
        cabecera = lector.fieldnames or []
        for campo in CAMPOS:
            if campo not in cabecera:
                raise ValueError(f"Fila 1, columna {campo}: falta en la cabecera")
        if len(cabecera) != len(set(cabecera)):
            raise ValueError("Fila 1, columna cabecera: hay nombres duplicados")
        for fila in lector:
            numero = lector.line_num
            if None in fila or None in fila.values():
                raise ValueError(f"Fila {numero}, columna campos: cantidad incorrecta")
            registro = {}
            for campo in CAMPOS:
                texto = fila[campo].strip()
                try:
                    if campo == "imdb":
                        if not texto or texto in ids:
                            raise ValueError
                        ids.add(texto)
                        valor = texto
                    elif campo == "title":
                        valor = unescape(texto).strip()
                        if not valor:
                            raise ValueError
                    elif campo == "year":
                        valor = int(texto)
                        if valor <= 0:
                            raise ValueError
                    else:
                        valor = dinero(texto)
                except (ValueError, InvalidOperation) as error:
                    raise ValueError(f"Fila {numero}, columna {campo}: valor inválido {texto!r}") from error
                registro[campo] = valor
            filas.append(registro)
    except csv.Error as error:
        raise ValueError(f"Fila {lector.line_num}, columna campos: {error}") from error
    if not filas:
        raise ValueError("Fila 2, columna imdb: se requiere al menos un registro")
    return filas


def calcular(filas):
    presupuestos = [fila["budget"] for fila in filas if fila["budget"] is not None]
    ingresos = [fila for fila in filas if fila["domgross"] is not None]
    return {
        "total": len(filas),
        "suma": sum((fila["domgross"] for fila in ingresos), Decimal(0)),
        "media": sum(presupuestos) / len(presupuestos) if presupuestos else None,
        "faltantes": len(filas) - len(ingresos),
        "top": sorted(ingresos, key=lambda fila: fila["domgross"], reverse=True)[:10],
    }


def usd(valor):
    return "Sin dato" if valor is None else f"USD {valor:,.2f}"


def generar_html(filas, resumen):
    maximo = max((fila["domgross"] for fila in resumen["top"]), default=0) or 1
    barras = []
    for fila in resumen["top"]:
        ingreso = fila["domgross"]
        ancho = ingreso / maximo * 100
        barras.append(
            f'<li>{escape(fila["title"])} · {usd(ingreso)}'
            f'<div class="barra" style="width:{ancho:.2f}%"></div></li>'
        )
    tabla = []
    for fila in filas[:10]:
        celdas = [fila["imdb"], fila["title"], fila["year"], usd(fila["budget"]), usd(fila["domgross"])]
        tabla.append("<tr>" + "".join(f"<td>{escape(str(valor))}</td>" for valor in celdas) + "</tr>")
    fecha = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    sha = escape(os.getenv("GITHUB_SHA") or "local")
    return f"""<!doctype html>
<html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Cine CI/CD</title>
<style>
body {{ font: 16px system-ui; max-width: 960px; margin: 2rem auto; padding: 0 1rem; color: #172554; }}
li {{ margin-bottom: .7rem; }} .barra {{ height: .8rem; background: #2563eb; }}
.tabla {{ overflow-x: auto; }} table {{ border-collapse: collapse; width: 100%; }}
th, td {{ text-align: left; padding: .5rem; border-bottom: 1px solid #cbd5e1; }}
</style>
<h1>Cine CI/CD</h1>
<p>Estudiante · {escape(ESTUDIANTE)}</p>
<p>Copia educativa: contiene modificaciones simuladas</p>
<p>Fuente: <a href="https://github.com/fivethirtyeight/data/tree/master/bechdel">FiveThirtyEight, datos Bechdel</a>.
Licencia <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>.</p>
<h2>Resumen de la muestra histórica</h2>
<p>Taquilla en Estados Unidos y presupuestos en USD nominales del año de estreno, sin ajuste por inflación.</p>
<ul>
<li>Total de películas: {resumen["total"]}</li>
<li>Suma de taquilla disponible: {usd(resumen["suma"])}</li>
<li>Media de presupuesto disponible: {usd(resumen["media"])}</li>
<li>Ingresos faltantes: {resumen["faltantes"]}</li>
</ul>
<h2>Diez mayores ingresos de taquilla</h2><ol>{"".join(barras)}</ol>
<h2>Primeras diez filas</h2>
<div class="tabla"><table><thead><tr>
<th>IMDb</th><th>Título</th><th>Año</th><th>Presupuesto</th><th>Taquilla en EE. UU.</th>
</tr></thead><tbody>{"".join(tabla)}</tbody></table></div>
<p>Generado el {fecha} · Commit <code>{sha}</code></p>
</html>
"""


def main():
    try:
        with (RAIZ / "datos" / "movies.csv").open(encoding="utf-8-sig", newline="") as archivo:
            filas = validar(archivo)
        informe = generar_html(filas, calcular(filas))
        destino = RAIZ / "public" / "index.html"
        destino.parent.mkdir(exist_ok=True)
        destino.write_text(informe, encoding="utf-8")
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    print(f"Informe generado con {len(filas)} películas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
