import csv
import re

# ============== IMPOSTAZIONI ==============
NOME_FILE_CSV = "TOA3006.csv"              # <-- inserisci qui il nome del tuo file CSV
DELIMITATORE = ","
CODIFICA = "utf-8"
SALTA_INTESTAZIONE = True                  # True salta la prima riga (nomi colonne), False la include
FILE_OUTPUT = "prova_lemmatizzazione_5_con_prep_art.tsv"
FILE_ANOMALIE = "righe_anomale_5_con_prep_art.txt"      # righe saltate o da controllare
# ==========================================

N_COL = 20
UPOS = {"ADJ", "ADP", "ADV", "AUX", "CCONJ", "DET", "INTJ", "NOUN", "NUM",
        "PART", "PRON", "PROPN", "PUNCT", "SCONJ", "SYM", "VERB", "X", "_", "VERBPRON", "ADPART"}

scritte = 0
saltate = 0
sospette = 0

with open(NOME_FILE_CSV, newline="", encoding=CODIFICA) as f_in, \
     open(FILE_OUTPUT, "w", encoding="utf-8") as f_out, \
     open(FILE_ANOMALIE, "w", encoding="utf-8") as f_log:

    if SALTA_INTESTAZIONE:
        next(f_in, None)

    linee = f_in.readlines()    #tengo tutte le righe in memoria per guardare quelle successive

    # Ogni riga viene letta DA SOLA: un problema di virgolette in una riga
    # non può più contagiare le righe successive.
    for idx, riga_testo in enumerate(linee):
        n_riga = idx + (2 if SALTA_INTESTAZIONE else 1)
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
            upos = "COMPOSTO"

            intervallo = re.match(r"^(\d+)-(\d+)$", campi[4])
            if intervallo:
                n_parti = int(intervallo.group(2)) - int(intervallo.group(1)) + 1
                lemmi_parti = []
                upos_parti = []
                for t in linee[idx + 1: idx + 1 + n_parti]:
                    c = next(csv.reader([t], delimiter=DELIMITATORE, skipinitialspace=True))
                    c = [x.strip() for x in c]
                    # la riga seguente deve essere davvero una parte (token_id tipo "2-0a")
                    if len(c) == N_COL and c[0].startswith(campi[0]) and c[0] != campi[0]:
                        l = c[7]
                        if set(l) != {","}:
                            l = l.replace(",", "")
                        lemmi_parti.append(l)
                        upos_parti.append(c[8])
                if len(lemmi_parti) == n_parti:
                    lemma = "+".join(lemmi_parti)      # es. "gli+lo"
                    upos = "+".join(upos_parti)        # es. "PRON+PRON"
                else:
                    sospette += 1
                    f_log.write(f"DA CONTROLLARE riga {n_riga}: parti della forma composta "
                                f"non trovate: {riga_testo.strip()}\n")       
                # TODO cambiare upos in ARTADP se la forma composta è una preposizione articolata
                #      cambiare upos in PRONVERB se la forma composta è un verbo pronominale


        # le pause {P} ricevono "?" al posto di COMPOSTO
        if lemma == "{P}":
            upos = "PAUSE"

        # comportamento non_verbale
        if lemma == "{ride}":
            upos = "NVB"

        f_out.write(f"{form}\t{lemma}\t{upos}\n")
        scritte += 1

print(f"Fatto! Righe scritte in {FILE_OUTPUT}: {scritte}")
if saltate or sospette:
    print(f"Attenzione: {saltate} righe saltate, {sospette} da controllare: vedi {FILE_ANOMALIE}")

# TODO: automatizzare assegnazione nomi FILE_OUTPUT
# TODO: come sopra per FILE_ANOMALIE
# TODO: una volta scelte aggiungere tag preposizioni articolate e verbi pronominali in UPOS (riga 14)
# TODO: correggere bug ch,e a cui viene assegnato tag COMPOSTO invece di pron o sconj