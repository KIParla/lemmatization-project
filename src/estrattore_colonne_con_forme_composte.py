"""Legge un CSV/TSV di lemmatizzazione (con intestazione) e scrive form, lemma e upos,
una riga per token e senza intestazione.

Si può usare da riga di comando oppure importando la funzione estrai().

MODIFICHE rispetto alla versione iniziale (commit e0d4568); nel codice sono
segnate con "# MODIFICA:".
  1. Impostazioni da riga di comando (file, delimitatore, codifica, n. colonne, output...);
     i valori in cima al file restano come default.
  2. Nomi di output automatici, in una cartella separata (output/): risolve i due TODO
     sull'automazione di FILE_OUTPUT e FILE_ANOMALIE.
  3. Lettura con un solo csv.reader sul file intero, invece di una riga alla volta.
  4. Posizioni delle colonne e numero di colonne ricavati dall'intestazione
     (funziona sia con i file a 20 colonne, sia con quelli di wip/ a 9 o 11).
  5. Forme composte: le parti si cercano dal token_id (7-5 -> 7-5a, 7-5b), non
     dall'intervallo della colonna "id" (che in alcuni file non c'è).
  6. Pause: lemma PAUSE e upos NVB; comportamenti non verbali: lemma e upos NVB.
  7. Tutto il lavoro è nella funzione estrai(), così altri script possono importarla
     (es. generatore_tabella_occorrenze.py) senza lanciare un processo a parte.
  8. Lista chiara di cosa è ammesso (UPOS_AMMESSE e COMPOSTI_AMMESSI in cima al file):
     le righe con una upos o un composto non in lista, o con un campo "_", vanno nel file
     delle anomalie e NON vengono scritte nell'output (prima erano segnalate ma scritte).
  9. Form/lemma/upos vuoti (e upos "-") vengono normalizzati a "_", quindi segnalati come
     "campo '_' (non annotato)" invece che come upos '' non valida.
"""
import argparse
import csv
import re
from pathlib import Path

# ============== IMPOSTAZIONI (valori di default) ==============
# MODIFICA (1): tutto può essere sovrascritto da riga di comando, es.:
#   python estrattore_colonne_con_forme_composte.py TOA3006.csv
#   python estrattore_colonne_con_forme_composte.py TOA3006.csv -o out.tsv --n-col 20
NOME_FILE_CSV = "wip/KIP/BOA1001.csv"              # file CSV di default
DELIMITATORE = ","
CODIFICA = "utf-8-sig"                     # "-sig" ignora la BOM che alcuni csv hanno all'inizio
SALTA_INTESTAZIONE = True                  # True salta la prima riga (nomi colonne), False la include
# MODIFICA (2): cartella di output; prima i file venivano scritti con nome fisso nella cartella corrente
DIR_OUTPUT = Path(__file__).resolve().parent.parent / "output"   # cartella di output (creata se manca)
N_COL = 20
# ==============================================================

# ============== COSA È AMMESSO NELL'OUTPUT ==============
# MODIFICA (8): tutto ciò che non è in queste due liste va nel file delle anomalie
# e non viene scritto. Per ammettere un nuovo caso basta aggiungerlo qui.

# upos singole
UPOS_AMMESSE = {
    "ADJ", "ADP", "ADV", "AUX", "CCONJ", "DET", "INTJ", "NOUN", "NUM", "PART",
    "PRON", "PROPN", "PUNCT", "SCONJ", "VERB", "X",
    "PAUSE",   # pause: form "(.)"
    "NVB",     # comportamenti non verbali: form "((...))"
}

# upos dei token composti (lemma e upos sono la concatenazione con "+" delle parti)
COMPOSTI_AMMESSI = {
    "ADP+DET",             # preposizione articolata        nel -> in+il
    "VERB+PRON",           # verbo + clitico                darmi -> dare+mi
    "VERB+PRON+PRON",      # verbo + due clitici            portamelo -> portare+me+lo
    "AUX+PRON",            # ausiliare + clitico            averlo -> avere+lo
    "AUX+PRON+PRON",       # ausiliare + due clitici        essermene -> essere+me+ne
    "PRON+PRON",           # due pronomi                    glielo -> gli+lo
    "PRON+ADP",            # pronome + preposizione         teco -> te+con
    "ADV+PRON",            # avverbio + clitico             eccoci -> ecco+ci
}
# ========================================================


# MODIFICA (3): la pulizia delle virgole interne, prima ripetuta tre volte, è una funzione
def pulisci(c):
    # toglie le virgole interne (es. "ch,e" -> "che"); i token fatti di sole
    # virgole (la punteggiatura ",") restano invariati
    return c if set(c) == {","} else c.replace(",", "")


# MODIFICA (7): prima era codice eseguito direttamente a livello di modulo
def estrai(nome_file_csv, file_output=None, file_anomalie=None, dir_output=DIR_OUTPUT,
           delimitatore=DELIMITATORE, codifica=CODIFICA,
           salta_intestazione=SALTA_INTESTAZIONE, n_col=None):
    """Legge il csv, scrive form-lemma-upos in file_output e le anomalie in file_anomalie.

    Restituisce (righe, saltate, sospette):
      righe    lista di tuple (form, lemma, upos) scritte nell'output
      saltate  quante righe hanno un numero di campi sbagliato
      sospette quante righe sono finite nelle anomalie (e non nell'output)
    """
    # MODIFICA (2): nomi di output ricavati dal nome del file di input
    dir_output = Path(dir_output)
    dir_output.mkdir(parents=True, exist_ok=True)
    base = dir_output / Path(nome_file_csv).stem
    file_output = file_output or f"{base}.tsv"
    file_anomalie = file_anomalie or f"{base}.anomalie.txt"

    n_col_arg = n_col
    n_col = n_col or N_COL

    righe = []
    saltate = 0
    sospette = 0

    with open(nome_file_csv, newline="", encoding=codifica) as f_in, \
         open(file_output, "w", encoding="utf-8") as f_out, \
         open(file_anomalie, "w", encoding="utf-8") as f_log:

        # MODIFICA (3): un solo csv.reader sull'intero file (prima: un csv.reader per ogni riga,
        # per evitare che una virgoletta sbagliata contagiasse le righe successive; ora una
        # virgoletta aperta e mai chiusa puo' inglobare piu' righe)
        # skipinitialspace=True: il file può avere spazi di allineamento prima dei campi,
        # quindi un campo come   "roma,"   va riconosciuto come campo tra virgolette
        lettore = csv.reader(f_in, delimiter=delimitatore, skipinitialspace=True)

        # MODIFICA (4): prima le posizioni erano fisse (campi[6], campi[7], campi[8]) e
        # N_COL fisso a 20; ora vengono lette dall'intestazione
        # posizioni delle colonne: dall'intestazione se c'è, altrimenti quelle di default
        I_TOKEN, I_FORM, I_LEMMA, I_UPOS = 0, 6, 7, 8
        I_SPAN = None
        if salta_intestazione:
            intest = [c.strip() for c in next(lettore, [])]
            if intest and n_col_arg is None:
                n_col = len(intest)
            try:
                I_TOKEN, I_FORM, I_LEMMA, I_UPOS = (
                    intest.index(n) for n in ("token_id", "form", "lemma", "upos"))
            except ValueError:
                raise SystemExit(f"{nome_file_csv}: nell'intestazione mancano token_id, form, "
                                 f"lemma o upos: {intest}")

            I_SPAN = intest.index("span") if "span" in intest else None

        # tengo tutte le righe in memoria per guardare quelle successive: le parti di un
        # composto (7-5a, 7-5b) stanno nelle righe DOPO la riga del composto (7-5), e
        # nel ciclo sotto "idx" è la posizione della riga che stiamo elaborando.
        # (MODIFICA (3): lista di coppie (numero di riga, campi) invece delle righe di testo)
        linee = [(lettore.line_num, [c.strip() for c in r]) for r in lettore if r]

        for idx, (n_riga, campi) in enumerate(linee):
            riga_testo = delimitatore.join(campi)

            if len(campi) != n_col:
                # riga con un numero di colonne diverso dall'intestazione: la scarto
                # (continue) e la scrivo nel log come SALTATA
                saltate += 1
                f_log.write(f"SALTATA riga {n_riga}: {len(campi)} campi invece di {n_col}: "
                            f"{riga_testo}\n")
                continue

            form, lemma, upos = campi[I_FORM], campi[I_LEMMA], campi[I_UPOS]

            form, lemma = pulisci(form), pulisci(lemma)

            # MODIFICA (9): campi vuoti o con un segnaposto ("-", "–", "—") diventano "_"
            # (= non annotato). Per form e lemma solo il campo vuoto: "-" può essere un
            # trattino vero (punteggiatura); per la upos "-" non è mai valido.
            if not form: form = "_"
            # MODIFICA (10): se la form è "_" ma la colonna span ha il testo (tipico dei
            # composti: "farteli,_,_,_"), si usa span come form
            if form == "_" and I_SPAN is not None and campi[I_SPAN] not in ("", "_"):
                form = pulisci(campi[I_SPAN])
            if not lemma: lemma = "_"
            if upos in ("", "-", "–", "—"): upos = "_"

            # Token composto (preposizioni articolate, verbi con clitici ecc.):
            # nel file la riga "padre" ha lemma e upos "_" e le sue parti sono scritte nelle
            # righe successive, ognuna con un proprio lemma e una propria upos, es.:
            #     7-5,  ..., nel, _,  _      <- composto (lemma e upos "_")
            #     7-5a, ..., in,  in, ADP    <- prima parte
            #     7-5b, ..., il,  il, DET    <- seconda parte
            # MODIFICA (6): pause e non verbali hanno lemma e upos "_" come i composti,
            # quindi vanno riconosciuti prima ed esclusi da questo ramo
            e_pausa = form in ("(.)", "[PAUSE]", "{P}")
            # Comportamento non verbale: la form è tra doppie parentesi tonde, "((ride))",
            # oppure, nei vecchi file, tra graffe, "{ride}".
            #   \(\(  e  \)\)  le parentesi sono precedute da \ perché in una regex sono
            #                  caratteri speciali
            #   .*             qualsiasi testo in mezzo
            #   |              "oppure"
            # fullmatch richiede che l'INTERA form abbia questa forma, non solo una parte.
            e_nvb = bool(re.fullmatch(r"\(\(.*\)\)|\{.*\}", form))
            if form != "_" and lemma == "_" and upos == "_" and not (e_pausa or e_nvb):
                lemma = form
                upos = "COMPOSTO"

                # MODIFICA (5): prima il numero di parti si ricavava dall'intervallo della colonna
                # "id" (es. 8-9 -> 2 parti), e senza "id" i composti restavano COMPOSTO.
                # le parti sono le righe successive con token_id = quello del composto + lettere
                # (es. "7-5" -> "7-5a", "7-5b"); non servono né "id" né il numero di colonne
                lemmi_parti = []
                upos_parti = []
                for _, c in linee[idx + 1:]:
                    # La riga successiva è una parte di questo composto solo se il suo
                    # token_id è quello del composto seguito da una o più lettere:
                    # "7-5" -> "7-5a", "7-5b" sì; "7-6" no.
                    # re.escape protegge il "-" e gli altri caratteri speciali del token_id;
                    # [a-z]+ significa "una o più lettere minuscole".
                    if len(c) <= max(I_TOKEN, I_LEMMA, I_UPOS) or not re.fullmatch(
                            re.escape(campi[I_TOKEN]) + r"[a-z]+", c[I_TOKEN]):
                        break
                    lemmi_parti.append(pulisci(c[I_LEMMA]))
                    upos_parti.append(c[I_UPOS])
                if lemmi_parti:
                    lemma = "+".join(lemmi_parti)      # es. "gli+lo"
                    upos = "+".join(upos_parti)        # es. "PRON+PRON"
                    # TODO in un secondo momento: ADP+DET -> ADPART, VERB/AUX+PRON -> VERBPRON
                else:
                    sospette += 1
                    # nessuna parte trovata: non si può costruire il lemma, quindi la
                    # riga va nelle anomalie e non nell'output
                    f_log.write(f"ANOMALIA riga {n_riga}: parti della forma composta "
                                f"non trovate: {riga_testo}\n")
                    continue

            # MODIFICA (6): prima solo lemma "{P}" -> upos PAUSE e lemma "{ride}" -> upos NVB;
            # ora si guarda la form, per tutti i formati, e anche il lemma diventa PAUSE / NVB
            # pause: lemma PAUSE e upos NVB (come nei csv di wip/)
            # (nei csv di wip/ sono "(.)"; accetta anche i vecchi "[PAUSE]" e "{P}")
            if e_pausa:
                lemma, upos = "PAUSE", "NVB"

            # comportamenti non verbali: lemma e upos NVB
            # (nei csv di wip/ sono "((ride))", nei vert.tsv "{ride}")
            elif e_nvb:
                lemma = upos = "NVB"

            # MODIFICA (8): controllo finale, fatto dopo aver costruito lemma e upos definitivi.
            # La riga è anomala se: ha un campo "_"; è un composto non in COMPOSTI_AMMESSI;
            # oppure è una upos singola non in UPOS_AMMESSE.
            motivo = None
            parti = upos.split("+")    # "ADP+DET" -> ["ADP", "DET"]; "NOUN" -> ["NOUN"]

            # Qui controlliamo se in form, lemma o upos c'è un campo "_" (= non annotato).
            # Per un composto lemma e upos hanno più parti ("a+il", "ADP+DET"), e basta che
            # UNA sia "_" perché la riga sia anomala. Per controllarle tutte in un colpo
            # mettiamo form, le parti del lemma e le parti dell'upos in un'unica tupla:
            #     ("nel", *["in", "il"], *["ADP", "DET"])  ->  ("nel", "in", "il", "ADP", "DET")
            # L'asterisco "*" davanti a una lista la "spacchetta": ne inserisce gli elementi
            # uno per uno nella tupla, invece di inserire la lista intera come un solo elemento.
            # Poi "_" in (...) risponde True se almeno un elemento della tupla è proprio "_".
            # Versione equivalente, più lunga:
            #     tutti_i_campi = [form] + lemma.split("+") + parti
            #     if "_" in tutti_i_campi:
            if "_" in (form, *lemma.split("+"), *parti):
                motivo = "campo '_' (non annotato)"
            elif len(parti) > 1 and upos not in COMPOSTI_AMMESSI:
                motivo = f"composto '{upos}' non ammesso"
            elif len(parti) == 1 and upos not in UPOS_AMMESSE:
                motivo = f"upos '{upos}' non valida"
            if motivo:
                # riga anomala: nel log con il motivo, ma non nell'output
                sospette += 1
                f_log.write(f"ANOMALIA riga {n_riga}: {motivo}: {riga_testo}\n")
                continue

            f_out.write(f"{form}\t{lemma}\t{upos}\n")
            righe.append((form, lemma, upos))

    return righe, saltate, sospette


# MODIFICA (1), (7): argomenti da riga di comando; si eseguono solo se il file è lanciato direttamente
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("csv", nargs="?", default=NOME_FILE_CSV, help="file CSV di input")
    ap.add_argument("-o", "--output", default=None, help="file TSV di output")
    ap.add_argument("-a", "--anomalie", default=None, help="file log righe anomale")
    ap.add_argument("-D", "--dir-output", default=DIR_OUTPUT, help="cartella di output")
    ap.add_argument("-d", "--delimitatore", default=DELIMITATORE)
    ap.add_argument("-e", "--codifica", default=CODIFICA)
    ap.add_argument("--n-col", type=int, default=None,
                    help="numero di colonne atteso (default: quante ne ha l'intestazione, "
                         "altrimenti %d)" % N_COL)
    ap.add_argument("--con-intestazione", action=argparse.BooleanOptionalAction,
                    default=SALTA_INTESTAZIONE, help="la prima riga è l'intestazione (da saltare)")
    a = ap.parse_args()

    righe, saltate, sospette = estrai(a.csv, a.output, a.anomalie, a.dir_output,
                                      a.delimitatore, a.codifica, a.con_intestazione, a.n_col)
    print(f"Fatto! Righe scritte: {len(righe)}")
    if saltate or sospette:
        print(f"Attenzione: {saltate} righe saltate, {sospette} anomale (non scritte): vedi il file delle anomalie")

# TODO: correggere bug ch,e a cui viene assegnato tag COMPOSTO invece di pron o sconj
