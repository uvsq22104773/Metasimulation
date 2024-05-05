# Importation des modules requis
import re  # Module pour les expressions régulières
import subprocess  # Module pour exécuter des commandes système

# Fonction pour convertir un fichier texte en code RAM
def convertTxt(nom_fichier):
    ''' Prend le nom du fichier à convertir en code RAM en entrée'''
    # Ouvrir le fichier en mode lecture
    with open(nom_fichier, 'r') as fichier:
        contenu = fichier.readlines()

    # Initialiser une liste pour stocker les instructions RAM
    ram = []

    # Parcourir chaque ligne du fichier
    for lines in contenu:
        # Utiliser une expression régulière pour extraire les opérations et opérandes de chaque ligne
        match = re.match(r'(\w+)\((.*?)(?:,\s*(.*?))?(?:,\s*(.*?))?\)', lines)
        if match:
            # Extraire l'opération et les opérandes
            operation = match.group(1)  
            operand1 = match.group(2)  
            operand2 = match.group(3)  
            operand3 = match.group(4)  

            # Convertir les opérandes en entiers si possible
            try:
                operand1 = int(operand1)
            except:
                pass

            if operand2 == None:
                # Si seul un opérande est présent, l'ajouter à la liste des instructions
                ram.append([operation, [operand1]])
                continue

            try:
                operand2 = int(operand2)
            except:
                pass

            try:
                operand3 = int(operand3)
            except:
                pass

            # Ajouter l'opération et ses opérandes à la liste des instructions RAM
            ram.append([operation, [operand1, operand2, operand3]])
        else:
            continue

    # Réorganisation des registres pour qu'ils se suivent et mise à jour des références dans le code RAM
    # (par exemple, réorganiser r1, r2, r3 en r0, r1, r2 et mettre à jour les références dans les instructions)
    R = list(set(re.findall(r'[r|i|o][0-9]+', str(ram))))  # Trouver tous les registres
    R.sort(key=lambda x : int(x[1:]))  # Trier les registres par numéro
    translate = dict()  # Dictionnaire pour mapper les anciens registres aux nouveaux

    # Assigner de nouveaux indices aux registres et stocker les traductions dans un dictionnaire
    i, k = 0, 0
    nbI = set(re.findall(r'i[0-9]+', str(ram)))
    if "i0" in nbI:
        j = 0
    else:
        j = 1
    for elem in R:
        if elem.startswith("r"):
            translate[elem] = "r" + str(i)
            i += 1
        if elem.startswith("i"):
            translate[elem] = "i" + str(j)
            j += 1
        if elem.startswith("o"):
            translate[elem] = "o" + str(k)
            k += 1

    # Remplacer les anciens registres par les nouveaux dans les instructions RAM
    i = 0
    for instruction in ram:
        j = 0
        for op in instruction[1]:
            if type(op) == str:
                if "@" in op:
                    ram[i][1][j] = op[:2] + translate[op[2:]]
                else:
                    ram[i][1][j] = translate[op]
            j += 1
        i += 1

    return ram


# Fonction pour effectuer une étape de la machine RAM
def step(ram, config):
    '''config = [indice, I, R, O]
        avec I la liste d'input du genre [2, a, b]
        R = [k, r1, r2, ..., rk]
        O = [n, o1, ..., on]'''
    # Récupérer l'instruction à l'indice actuel
    instruction = ram[config[0]]

    # Afficher la configuration avant l'exécution de l'instruction
    print(f"Instruction : {instruction}")
    print(f"Configuration avant instruction :\nPosition actuelle : {config[0]}\nRegistre I : {config[1]}\nRegistre R : {config[2]}\nRegistre O : {config[3]}")

    # Exécuter l'instruction
    if instruction[0] == "JUMP":
        config[0] += instruction[1][0]
    else:    
        a, b, c = instruction[1]
        if type(a) == str:
            a = registre(a, config)[0]
        if type(b) == str:
            b = registre(b, config)[0]
        if type(c) == str:
            c, pos1, pos2 = registre(c, config)
            if (pos1 == 3 and pos2 == 0) or (pos1 == 2 and pos2 == 0):
                # Si c'est un registre o et qu'il n'y a pas assez d'emplacements, en ajouter jusqu'à ce qu'il y en ait suffisamment
                while (len(config[pos1])-2) < config[pos1][0]:
                    config[pos1].append("")

        # Exécuter l'opération correspondant à l'instruction
        if instruction[0] == "ADD":
            config[pos1][pos2] = a + b
            config[0] += 1
        # ...
        # Ajouter les autres opérations ici

    # Afficher la configuration après l'exécution de l'instruction
    print(f"Configuration après instruction :\nPosition suivante : {config[0]}\nRegistre I : {config[1]}\nRegistre R : {config[2]}\nRegistre O : {config[3]}\n")

    return config


# Fonction pour récupérer la valeur d'un registre en fonction de son type et de sa position dans la configuration
def registre(r : str, config : list):
    """ Renvoie la valeur du registre en fonction de son type (I, R, O) et de sa position dans la configuration"""
    val = int(r[-1])
    if r.startswith("i") and "@" not in r:
        return config[1][val], 1, val
    elif r.startswith("i") and "@" in r:
        return config[1][config[2][val]], 1, config[2][val]
    # Ajouter les autres cas pour les registres r et o ici
    # ...


# Fonction pour initialiser la configuration de la machine RAM avec le mot d'entrée
def initializeConfig(ram, mot : list):
    """ Ajoute dans le mot la taille de l'entrée, initialise la première configuration et calcule la taille du registre O"""
    if type(mot) == list:
        # Insérer la taille du mot dans la première position
        mot.insert(0, len(mot))
        # Initialiser la configuration avec la position 0, le mot d'entrée, un registre de travail vide et un registre de sortie vide
        config = [0, mot, [0], [0]]
        # Étendre le registre R pour qu'il ait le même nombre d'emplacements que le registre le plus élevé dans les instructions RAM
        config[2].extend([""] * (len(set(re.findall(r'r[0-9]+', str(ram))))-1))
        return config
    else:
        raise TypeError("Le mot doit être sous la forme d'une liste (la taille ne doit pas être précisée)")


# Fonction pour exécuter la machine RAM
def execRAM(ram, mot):
    ''' Le mot en entrée doit être donné sous la forme d'une liste'''
    # Convertir le texte en instructions RAM et initialiser la configuration avec le mot d'entrée
    config = initializeConfig(ram, mot)
    
    # Tant que la position actuelle dans les instructions n'est pas hors de la portée des instructions
    while config[0] < len(ram):
        # Effectuer une étape de la machine RAM
        config = step(ram, config)

    # Afficher le résultat final stocké dans le registre de sortie
    print(f"Résultat final : {config[3]}")


# Fonction pour répondre à la question 1
def q1(text):
    ''' Imprime chaque instruction RAM convertie à partir du texte donné'''
    print("Le texte en entrée est stocké sous la forme d'une liste contenant les instructions :\nLes numéros des registres sont également réorganisés pour qu'ils se suivent")
    # Convertir le texte en instructions RAM et afficher chaque instruction
    ram = convertTxt(text)
    for line in ram:
        print(line)


# Fonction pour répondre à la question 2
def q2(text, mot):
    ''' Le mot en entrée doit être donné sous la forme d'une liste'''
    print("Une configuration est donnée sous cette forme : [n, [I], [R], [O]]\n"
          "n : le numéro de l'instruction\n"
          "I : le registre d'entrée contenant le mot d'entrée et sa taille (I[0])\n"
          "R : le registre de travail avec sa taille (R[0])\n"
          "O : le registre de sortie contenant la taille (O[0]) et le résultat de l'exécution de la machine RAM\n")
    # Convertir le texte en instructions RAM
    ram = convertTxt(text)
    # Initialiser la configuration avec le mot d'entrée
    config = initializeConfig(ram, mot)
    # Exécuter une étape de la machine RAM
    step(ram, config)


# Fonction pour répondre à la question 3
def q3(text, mot):
    ''' Le mot en entrée doit être donné sous la forme d'une liste'''
    # Convertir le texte en instructions RAM et exécuter la machine RAM avec le mot d'entrée
    ram = convertTxt(text)
    execRAM(ram, mot)


# Fonction principale pour lire l'entrée utilisateur et choisir la question à répondre
def main():
    # Lire l'entrée utilisateur pour choisir la question à répondre
    question = input("Quelle question souhaitez-vous répondre (q1, q2, q3) ? ")

    # Lire le nom du fichier contenant les instructions RAM
    nom_fichier = input("Entrez le nom du fichier contenant les instructions RAM : ")

    # Lire le mot d'entrée
    mot = list(input("Entrez le mot d'entrée : "))

    # Choisir la fonction à appeler en fonction de la question choisie
    if question == "q1":
        q1(nom_fichier)
    elif question == "q2":
        q2(nom_fichier, mot)
    elif question == "q3":
        q3(nom_fichier, mot)
    else:
        print("Question invalide.")

if __name__ == "__main__":
    import sys

    # Mapping entre les arguments de ligne de commande et les fonctions
    fonctions_avec_mot = {
        "q2": q2,
        "q3": q3
    }

    fonctions_sans_mot = {
        "q1": q1,
        "q8": q8,
        "q9": q9,
        "q10": q10
    }

    # Vérification des arguments de ligne de commande
    if len(sys.argv) < 2:
        print("Usage: python metasimulation.py <nom_fonction> <nom_fichier> <mot_d_entree>\nAide: python metasimulation.py help\nFichier disponible: python metasimulation.py file")
        sys.exit(1)

    # Vérification de la présence d'un fichier en entrée
    if sys.argv[1] in fonctions_sans_mot:
        if len(sys.argv) == 3:
            # Exécution de la fonction spécifiée avec le fichier en entrée
            nom_fonction = sys.argv[1]
            fonction_a_executer = fonctions_sans_mot[nom_fonction]
            nom_fichier = sys.argv[2]
            fonction_a_executer(nom_fichier)
        else:
            print(f"Usage de {sys.argv[1]}: python metasimulation.py <nom_fonction> <nom_fichier>")
    elif sys.argv[1] in fonctions_avec_mot:
        if len(sys.argv) == 4:
            nom_fonction = sys.argv[1]
            fonction_a_executer = fonctions_avec_mot[nom_fonction]
            nom_fichier = sys.argv[2]
            # Chaîne avec des entiers séparés par des virgules
            mot_entree = sys.argv[3]
            # Diviser la chaîne en une liste de sous-chaînes séparées par des virgules
            sous_chaines = mot_entree.split(',')
            # Convertir chaque sous-chaîne en entier et les stocker dans une liste
            liste_mot_entree = [int(x) for x in sous_chaines]
            fonction_a_executer(nom_fichier, liste_mot_entree)
        else:
            print(f"Usage de {sys.argv[1]}: python metasimulation.py <nom_fonction> <nom_fichier> <nom_d_entree>")
    elif sys.argv[1] == "help":
        print("Fonction disponible:")
        print("q1: Réponse de la question 1")
        print("q2: Réponse de la question 2")
        print("q3: Réponse de la question 3")
        print("q8: Réponse de la question 8")
        print("q9: Réponse de la question 9")
        print("q10: Réponse de la question 10")
    elif sys.argv[1] == "file":
        # Exécuter la commande ls
        result = subprocess.run(['ls'], stdout=subprocess.PIPE)

        # Récupérer la sortie de la commande
        output = result.stdout.decode('utf-8')

        # Afficher la sortie
        print(output)
    else:
        print("Usage: python metasimulation.py <nom_fonction> <nom_fichier> <mot_d_entree>")
        print("Aide: python metasimulation.py help")
        print("Fichier disponible: python metasimulation.py file")
