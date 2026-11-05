"""Genera la tabella finale: per ogni coppia (form, lemma), quante volte è stata annotata con ogni PoS.

Uso:
    python src/generatore_tabella_occorrenze.py                  # tutti i csv in wip/
    python src/generatore_tabella_occorrenze.py wip/KIP/BOA1001.csv wip/KIP/BOA1002.csv

Per ogni csv usa la funzione estrai() di estrattore_colonne_con_forme_composte.py
(che salva anche form, lemma, upos in output/estratti/), poi conta le triple e scrive
output/tabella_occorrenze.tsv.

Le righe con upos non ammesse o campi "_" non entrano nella tabella ma finiscono nelle anomalie
(output/estratti/*.anomalie.txt). Le upos e i composti ammessi sono elencati in
UPOS_AMMESSE e COMPOSTI_AMMESSI, in cima a estrattore_colonne_con_forme_composte.py.
"""
import csv
import sys
from math import log2
from collections import Counter, defaultdict
from pathlib import Path

from estrattore_colonne_con_forme_composte import estrai

CARTELLA_PROGETTO = Path(__file__).resolve().parent.parent
CARTELLA_ESTRATTI = CARTELLA_PROGETTO / "output" / "estratti"
FILE_TABELLA = CARTELLA_PROGETTO / "output" / "tabella_occorrenze.tsv"


def dispersione(per_upos):
    """Entropia di Shannon della distribuzione dei PoS, in percentuale (0-100).

    0   = la coppia ha sempre lo stesso PoS (nessun dubbio)
    100 = tutti i PoS osservati sono ugualmente frequenti (massimo dubbio)
    L'entropia e' divisa per log2(numero di PoS osservati), cosi' va da 0 a 100.
    """
    totale = sum(per_upos.values())
    if len(per_upos) < 2:
        return 0.0
    entropia = -sum(n / totale * log2(n / totale) for n in per_upos.values())
    return 100 * entropia / log2(len(per_upos))


# 1. quali csv elaborare: quelli passati da riga di comando, altrimenti tutti quelli in wip/
if len(sys.argv) > 1:
    file_csv = [Path(p) for p in sys.argv[1:]]
else:
    file_csv = sorted((CARTELLA_PROGETTO / "wip").glob("*/*.csv"))

# 2. per ogni csv estraggo le triple (form, lemma, upos) e le conto
conteggi = defaultdict(Counter)   # (form, lemma) -> Counter({upos: quante volte})

for csv_in in file_csv:
    righe, _, _ = estrai(csv_in, dir_output=CARTELLA_ESTRATTI)
    for form, lemma, upos in righe:
        conteggi[(form, lemma)][upos] += 1

# 3. le colonne dei PoS sono quelle che compaiono nei dati
tutte_le_upos = sorted({upos for c in conteggi.values() for upos in c})

# 4. scrivo la tabella: form, lemma, frequenza totale, dispersione, una colonna per ogni PoS
with open(FILE_TABELLA, "w", encoding="utf-8", newline="") as f:
    scrittore = csv.writer(f, delimiter="\t")
    scrittore.writerow(["form", "lemma", "frequenza", "dispersione_%"] + tutte_le_upos)
    for (form, lemma), per_upos in sorted(conteggi.items()):
        riga = [form, lemma, sum(per_upos.values()), round(dispersione(per_upos), 1)]
        riga += [per_upos[u] or "" for u in tutte_le_upos]   # cella vuota se zero
        scrittore.writerow(riga)

print(f"Fatto! {len(conteggi)} coppie form-lemma da {len(file_csv)} file in {FILE_TABELLA}")
