import csv

# creo lista con i nomi colonne
colonne = [
    'form',
    'lemma',
    'frequenza assoluta', # quante volte appare nel corpus
    'frequenza percentuale', # quante volte appare nel corpus rispetto al totale dei lemmi
    'ADV', # avverbi
    'SCONJ', # congiunzioni subordinanti
    'CCONJ', # congiunzioni coordinanti
    'NOUN', # nomi comuni
    'PROPN', # nomi propri
    'ADJ', # aggettivi
    'VERB', # verbi
    'VERBPRON', # verbi pronominali
    'AUX', # ausiliari
    'ADP', # preposizioni
    'ADPART', # preposizioni articolate
    'INTJ', # interiezioni
    'SYM', # simboli
    'PRON', # pronomi
    'DET', # determinativi
    'NUM', # numerali
    'X', # parole inclassificabili
    '?', # TODO
]
# genero file tsv con nomi colonne
with open("tabella_occorrenze.tsv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerow(colonne)  # scrivo nomi colonne

with open("prova_lemmatizzazione_5_tsv.txt", "r", encoding="utf-8") as f_input, \
    open('tabella_occorrenze.tsv', 'a', newline='', encoding='utf-8') as f_output:
    reader = csv.reader(f_input, delimiter='\t')
    writer = csv.writer(f_output, delimiter='\t')

    next(reader)  # salto header

    for row in reader:

# TODO
# 1. inserire file a tre colonne (form, lemma, upos) e inserire ogni elemento al posto
#    giusto della tabella generata da questo script
# 2. ogni volta che un lemma appare, incrementare la frequenza assoluta e percentuale

# DUBBI
# 1. come gestire lemmi uguali con form diverso?
# 2. 