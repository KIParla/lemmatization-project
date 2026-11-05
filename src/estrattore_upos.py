# per estrarre da file lemma-upos -> modificare riga_16 con colonne[1]
# per estrarre da file form-lemma-upos -> modificare riga_16 con colonne[2]

lista_elementi_unici = set()

with open('prova_lemmatizzazione_5_tsv.txt', 'r', encoding='utf-8') as file:
    
    next(file)  # salto header
    
    for riga in file:
        colonne = riga.split()
        if len(colonne) > 1:
            if '_' in riga:
                continue  # salto le righe con il lemma "_"
            else: 
                lista_elementi_unici.add(colonne[1])  # aggiungo il lemma al set
                                                  # [1] perché uso seconda colonna

print(lista_elementi_unici)
