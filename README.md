# Processament de dades de força
Aquest projecte conté un script Python que processa fitxers `.txt` de dades de força de la Kistler i genera gràfics.

## Fitxers
- `Codi procesat dades de Força.py`: script principal.
- `directory/`: carpeta on es col·loquen els fitxers `.txt` d'entrada.
- `Grafica/`: carpeta de sortida on es guarden les gràfiques generades.
- `guia_script_python.pdf`: document amb informació addicional.

## Requisits
- Python 3.x
- Paquets Python:
  - `matplotlib`
  - `scipy`

## Ús
1. Col·loca els fitxers `.txt` dins la carpeta `directory/`.
2. Executa l'script:
   ```bash
   python "Codi procesat dades de Força.py"
   ```
3. Opcions addicionals:
   - `-f` o `--figures`: dibuixa un gràfic per fitxer.
   - `-a` o `--adjacent`: crea subgràfics adjacents compartint l'eix X.
   - `-s` o `--superposed`: dibuixa totes les corbes en un únic gràfic.
   - `-m` o `--show_maxs`: marca els màxims absoluts amb punts vermells.

## Exemple
```bash
python "Codi procesat dades de Força.py" -f -m
```

## Notes
- Si no es passa cap directori, l'script utilitza la carpeta `directory` o el directori del script.
- Les gràfiques es guarden a `Grafica/` quan s'utilitza el mode `adjacent` o `superposed`.

