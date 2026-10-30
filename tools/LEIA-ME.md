# Gerador da identidade visual

Todos os SVGs de `assets/` são gerados por `build_assets.py`. O texto é convertido em curvas
(o GitHub bloqueia fontes embutidas em SVG), por isso mudar um texto exige regenerar.

```bash
pip install fonttools
python tools/build_assets.py   # reescreve ../assets/*.svg
```

- Textos, projetos, stack e cores ficam em `build_assets.py` (listas `FEATURED`, `ROWS`, `STACK`, `SECTIONS`)
  e na paleta no topo de `lib.py`.
- Fontes (licença SIL OFL): Lora Bold e Carlito, em `tools/fonts/`.
