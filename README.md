# Cine CI/CD

Informe educativo sobre películas con validación automática y publicación en GitHub Pages.

Copia educativa: contiene modificaciones simuladas.

Datos de [FiveThirtyEight (Bechdel)](https://github.com/fivethirtyeight/data/tree/master/bechdel), bajo licencia [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Ejecutar en local

Con Python 3.12, desde la carpeta del proyecto:

```powershell
python -m unittest discover -v
python analizar.py
```

Abre `public/index.html` en el navegador. El programa lee `datos/movies.csv`. GitHub Actions valida ese mismo archivo en cada push a `main` y publica el informe si la validación es exitosa.

## Demostración

Completa esta tabla después de revisar las ejecuciones en GitHub Actions.

| Cambio | Valor de domgross | Resultado observado | Enlace a Actions |
| --- | --- | --- | --- |
| Aumento válido de USD 1.000.000 en 21 & Over | Antes y después pendientes | Pendiente | Pendiente |
| Prueba controlada | -100 | Pendiente | Pendiente |
| Corrección | Valor válido restaurado | Pendiente | Pendiente |
