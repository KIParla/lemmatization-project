# TODO: vedi riga 10/11, riga 17 e riga 67

import csv

# ============== IMPOSTAZIONI ==============
NOME_FILE_CSV = "TOA3006.csv"              # <-- inserisci qui il nome del tuo file CSV
DELIMITATORE = ","                         # delimitatore del file che legge: ',' per csv, '\t' per tsv
CODIFICA = "utf-8"
SALTA_INTESTAZIONE = True                  # True salta la prima riga (nomi colonne), False la include
FILE_OUTPUT = "prova_lemmatizzazione_5_con_form.tsv" # nome file di output # TODO: automatizzare assegnazione nomi FILE_OUTPUT
FILE_ANOMALIE = "righe_anomale_5.txt"      # righe saltate o da controllare # TODO come sopra per FILE_ANOMALIE
# ==========================================

N_COL = 20
UPOS = {"ADJ", "ADP", "ADV", "AUX", "CCONJ", "DET", "INTJ", "NOUN", "NUM",
        "PART", "PRON", "PROPN", "PUNCT", "SCONJ", "SYM", "VERB", "X", "_"}
# TODO: una volta scelte aggiungere upos per preposizioni articolate e verbi pronominali

scritte = 0
saltate = 0
sospette = 0

with open(NOME_FILE_CSV, newline="", encoding=CODIFICA) as f_in, \
     open(FILE_OUTPUT, "w", encoding="utf-8") as f_out, \
     open(FILE_ANOMALIE, "w", encoding="utf-8") as f_log:

    if SALTA_INTESTAZIONE:
        next(f_in, None)

    # Ogni riga viene letta DA SOLA: un problema di virgolette in una riga
    # non puo' piu' contagiare le righe successive.
    for n_riga, riga_testo in enumerate(f_in, start=2 if SALTA_INTESTAZIONE else 1):
        if not riga_testo.strip():
            continue

        # skipinitialspace=True: il file ha spazi di allineamento prima dei campi,
        # quindi un campo come   "roma,"   va riconosciuto come campo tra virgolette
        # (altrimenti la virgola interna spezza la colonna e sfasa tutte le altre)
        campi = next(csv.reader([riga_testo], delimiter=DELIMITATORE,
                                skipinitialspace=True))
        campi = [c.strip() for c in campi]

        if len(campi) != N_COL:
            saltate += 1
            f_log.write(f"SALTATA riga {n_riga}: {len(campi)} campi invece di {N_COL}: "
                        f"{riga_testo.strip()}\n")
            continue

        form, lemma, upos = campi[6], campi[7], campi[8]   # colonne 7, 8, 9

        # toglie le virgole interne (es. "ch,e" -> "che"); i token fatti di sole
        # virgole (la punteggiatura ",") restano invariati
        if set(form) != {","}:
            form = form.replace(",", "")
        if set(lemma) != {","}:
            lemma = lemma.replace(",", "")

        # controllo di sicurezza: upos deve essere un tag valido
        if upos not in UPOS:
            sospette += 1
            f_log.write(f"DA CONTROLLARE riga {n_riga}: upos '{upos}' insolito: "
                        f"{riga_testo.strip()}\n")

        # caso di preposizione articolate, verbi riflessivi ecc.
        if lemma == "_" and upos == "_":
            lemma = form
            upos = f"{campi[6]}_forma_composta_da" #TODO indicare da quali forme è composta (es. "dell'": "dell'_forma_composto_da_da+il")

        # le pause {P} ricevono "?" al posto di COMPOSTO
        if lemma == "{P}":
            upos = "PAUSE"

        # comportamento non_verbale
        if lemma == "{ride}":
            upos = "NVB"

        #f_out.write(f"{lemma}\t{upos}\n") # crea file con due colonne: lemma-upos
        f_out.write(f"{form}\t{lemma}\t{upos}\n") # crea file con tre colonne: form-lemma-upos
        scritte += 1

print(f"Fatto! Righe scritte in {FILE_OUTPUT}: {scritte}")
if saltate or sospette:
    print(f"Attenzione: {saltate} righe saltate, {sospette} da controllare: vedi {FILE_ANOMALIE}")
