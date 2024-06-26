# metasimulation.py
import re
import subprocess

def convertTxt(nom_fichier):
    ''' Prend le nom du fichier à convertir en code RAM en entrée'''
    with open(nom_fichier, 'r') as fichier:
        contenu = fichier.readlines()
    ram = []
    for lines in contenu:
        match = re.match(r'(\w+)\((.*?)(?:,\s*(.*?))?(?:,\s*(.*?))?\)', lines)
        if match:
            operation = match.group(1)  # n'importe quel mot
            operand1 = match.group(2)  # n'importe quel carac
            operand2 = match.group(3)  # , space suivi de n'importe quel carac mais ?: veut dire que le groupe peut ne pas être la
            operand3 = match.group(4)  # , space suivi de n'importe quel carac mais ?: veut dire que le groupe peut ne pas être la et se termine par ) ou non
            try:
                operand1 = int(operand1)
            except:
                pass
            if operand2 == None:
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
            ram.append([operation, [operand1, operand2, operand3]])
        else:
            continue
    # le but est de vérifier que les indices des r,i,o se suivent donc on les stocks tous
    # et après on leur assigne si besoin un nouvel indice
    R = list(set(re.findall(r'[r|i|o][0-9]+', str(ram))))
    R.sort(key=lambda x : int(x[1:]))
    translate = dict()
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
    # on va aller modifier le code en renomant les r,i,o
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
    

def step(ram, config):
    '''config = [indice, I, R, O]
        avec I la liste d'input du genre [2, a, b]
        R = [k, r1, r2, ..., rk]
        O = [n, o1, ..., on]'''
    instruction = ram[config[0]]
    print(f"Instruction : {instruction}")
    print(f"Configuration avant instruction :\nPosition actuelle : {config[0]}\nRegistre I : {config[1]}\nRegistre R : {config[2]}\nRegistre O : {config[3]}")
    if instruction[0] == "JUMP":
        config[0] += instruction[1][0]
    else:    
        a, b, c = instruction[1]
        if type(a) == str:
            a = registre(a, config)[0]
        if type(b) == str:
            b = registre(b, config)[0]
        if type(c) == str:
            # pos1 représente l'endroit où trouver si c'est un i un r ou un o
            # pos2 représente le nombre après la variable par exemple si on a r2 pos2 = 2 ce qui permet d'accéder à l'emplacement de r2
            c, pos1, pos2 = registre(c, config)
            # ajoute dans la liste O, R le bon nombre d'emplacement si il y en a pas assez
            if (pos1 == 3 and pos2 == 0) or (pos1 == 2 and pos2 == 0):
                while (len(config[pos1])-2) < config[pos1][0]:
                    config[pos1].append("")
        if instruction[0] == "ADD":
            config[pos1][pos2] = a + b
            config[0] += 1
        if instruction[0] == "SUB":
            config[pos1][pos2] = a - b
            config[0] += 1
        if instruction[0] == "MULT":
            config[pos1][pos2] = a * b
            config[0] += 1
        if instruction[0] == "DIV":
            config[pos1][pos2] = a / b
            config[0] += 1
        if instruction[0] == "JL":
            if a < b:
                config[0] += c
            else:
                config[0] += 1
        if instruction[0] == "JG":
            if a > b:
                config[0] += c
            else:
                config[0] += 1
        if instruction[0] == "JE":
            if a == b:
                config[0] += c
            else:
                config[0] += 1
        if instruction[0] == "JLE":
            if a <= b:
                config[0] += c
            else:
                config[0] += 1
        if instruction[0] == "JGE":
            if a >= b:
                config[0] += c
            else:
                config[0] += 1
    print(f"Configuration après instruction :\nPosition suivante : {config[0]}\nRegistre I : {config[1]}\nRegistre R : {config[2]}\nRegistre O : {config[3]}\n")
    return config


def registre(r : str, config : list):
    """ Renvoie la valeur du registre en fonction de sont type I, R, O ainsi que sa position dans la config
        par exemple registre(r2, [ADD, [2, 2, 5] [2, 3, 4], [0]]) 
        renvoie la valeur à la position 2 dans la liste R qui est la deuxième liste
        donc 4, 2, 2"""
    val = int(r[-1])
    if r.startswith("i") and "@" not in r:
        return config[1][val], 1, val
    elif r.startswith("i") and "@" in r:
        return config[1][config[2][val]], 1, config[2][val]
    
    elif r.startswith("r") and "@" not in r:
        return config[2][val], 2, val
    elif r.startswith("r") and "@" in r:
        return config[2][config[2][val]], 2, config[2][val]

    elif r.startswith("o") and "@" not in r:
        return config[3][val], 3, val
    elif r.startswith("o") and "@" in r:
        return config[3][config[2][val]], 3, config[2][val]


def initializeConfig(ram, mot : list):
    """ ajoute dans le mot la taille de l'entrée, initialise la première config et calcul la taille du registre O"""
    if type(mot) == list:
        mot.insert(0, len(mot))
        config = [0, mot, [0], [0]]
        config[2].extend([""] * (len(set(re.findall(r'r[0-9]+', str(ram))))-1))
        return config
    else:
        raise TypeError("Le mot doit être sous la forme d'une liste (la taille ne doit pas être précisé)")


def execRAM(ram, mot):
    config = initializeConfig(ram, mot)
    print(config)
    while config[0] < len(ram):
        step(ram, config)
    print(f"Résultat final (avec la taille dans le premier élément) : {config[-1]}")

def makeGraph(ram):
    ''' Fonction qui prend le code de la machine RAM
        Et qui retourne le graphe orienté de ce dernier sous la forme d'un dictionnaire
        avec les clés représentant les sommets donc l'instruction 
        et les valeurs sont les sommets accessibles depuis cette instruction'''
    graph = dict()
    for i in range(len(ram)):
        if ram[i][0] == "ADD" or ram[i][0] == "SUB" or ram[i][0] == "MULT" or ram[i][0] == "DIV":
            graph[i] = [i+1]
        elif ram[i][0] == "JUMP":
            graph[i] = [i+ram[i][1][0]]
        elif (ram[i][0] == "JE" or ram[i][0] == "JGE" or ram[i][0] == "JLE") and ram[i][1][0] == ram[i][1][1]:
            graph[i] = [i+ram[i][1][2]]
        else:
            graph[i] = [i+1, i+ram[i][1][2]]
    for elem in graph.get(i):
        if elem >= len(ram):
            graph[i] = ["FIN" if x == elem else x for x in graph[i]]
    return graph, ram


def deadCode(graph : dict, ram, indice=0):
    ''' Fonction qui prend en entré le graphe du code RAM et le code RAM
        Et qui les retournent sans les instructions inaccessibles'''
    accessible = set()
    notAccessible = set()
    # on regarde les éléments accessible
    for key in graph.keys():
        try:
            for value in graph.get(key):
                accessible.add(value)
        except:
            continue
    # on regarde ceux qui ne sont pas dedans
    for j in graph:
        if j == 0:
            continue
        if j not in accessible:
            notAccessible.add(j)
    # on regarde les éléments inaccessible pour les supprimer du code RAM et du graph
    cpt = len(notAccessible)
    for elem in notAccessible:
        print(f"Code mort : {ram[elem-indice]}, instruction n°{elem}")
        ram.remove(ram[elem-indice])
        graph.pop(elem)
        indice += 1
    if len(notAccessible) != 0:
        deadCode(graph, ram, indice)
    return graph, ram


def combine(graph, ram):
    ramDebut = ram.copy()
    try:
        for i in range(len(ram)-1):
            if (ram[i][0] == "ADD" or ram[i][0] == "SUB") and (ram[i+1][0] == "ADD" or ram[i+1][0] == "SUB"):
                if ram[i][1][2] == ram[i+1][1][2]:
                    part1 = [elem for elem in ram[i][1]]
                    part2 = [elem for elem in ram[i+1][1]]
                    combination = part1 + part2
                    somme = 0
                    if ram[i][0] == "ADD":
                        for elem in part1:
                            if type(elem) != str:
                                somme += elem
                                combination.remove(elem)
                    if ram[i][0] == "SUB":
                        somme = part1[0]
                        somme -= part1[1]
                        combination.remove(part1[0])
                        combination.remove(part1[1])

                    if ram[i+1][0] == "ADD":
                        for elem in part2:
                            if type(elem) != str:
                                somme += elem
                                combination.remove(elem)
                    if ram[i+1][0] == "SUB":
                        for elem in part2:
                            if type(elem) != str:
                                somme -= elem
                                combination.remove(elem)    
                    if len(set(combination)) == 1:
                        ram[i] = ["ADD", [somme, 0, ram[i][1][2]]]
                        ram.remove(ram[i+1])
            if (ram[i][0] == "MULT" or ram[i][0] == "DIV") and (ram[i+1][0] == "MULT" or ram[i+1][0] == "DIV"):
                if ram[i][1][2] == ram[i+1][1][2]:
                    part1 = [elem for elem in ram[i][1]]
                    part2 = [elem for elem in ram[i+1][1]]
                    combination = part1 + part2
                    produit = 1
                    if ram[i][0] == "MULT":
                        for elem in part1:
                            if type(elem) != str:
                                produit *= elem
                                combination.remove(elem)
                    if ram[i][0] == "DIV":
                        produit = part1[0]
                        produit /= part1[1]
                        combination.remove(part1[0])
                        combination.remove(part1[1])

                    if ram[i+1][0] == "MULT":
                        for elem in part2:
                            if type(elem) != str:
                                produit *= elem
                                combination.remove(elem)
                    if ram[i+1][0] == "DIV":
                        if type(part2[0]) != str and type(part2[1]) != str:
                            produit = part2[0]
                            produit /= part2[1]
                            combination.remove(part2[0])
                            combination.remove(part2[1])
                        elif type(part2[0]) != str and type(part2[1]) == str:
                            produit = part2[0]
                            produit /= produit
                            combination.remove(part2[0])
                            combination.remove(part2[1])
                        else:
                            produit = produit
                            produit /= part2[1]
                            combination.remove(part2[0])
                            combination.remove(part2[1])  
                    if len(set(combination)) == 1:
                        ram[i] = ["ADD", [produit, 0, ram[i][1][2]]]
                        ram.remove(ram[i+1])
            if (ram[i][0] == "ADD" or ram[i][0] == "SUB") and (ram[i+1][0] == "MULT" or ram[i+1][0] == "DIV"):
                if ram[i][1][2] == ram[i+1][1][2]:
                    part1 = [elem for elem in ram[i][1]]
                    part2 = [elem for elem in ram[i+1][1]]
                    combination = part1 + part2
                    somme = 0
                    produit = 1
                    if ram[i][0] == "ADD":
                        for elem in part1:
                            if type(elem) != str:
                                somme += elem
                                combination.remove(elem)
                    if ram[i][0] == "SUB":
                        somme = part1[0]
                        somme -= part1[1]
                        combination.remove(part1[0])
                        combination.remove(part1[1])
                    if ram[i+1][0] == "MULT":
                        for elem in part2:
                            if type(elem) != str:
                                produit *= elem
                                combination.remove(elem)
                        produit *= somme
                    if ram[i+1][0] == "DIV":
                        if type(part2[0]) != str and type(part2[1]) != str:
                            produit = part2[0]
                            produit /= part2[1]
                            combination.remove(part2[0])
                            combination.remove(part2[1])
                        elif type(part2[0]) != str and type(part2[1]) == str:
                            produit = part2[0]
                            produit /= somme
                            combination.remove(part2[0])
                            combination.remove(part2[1])
                        else:
                            produit = somme
                            produit /= part2[1]
                            combination.remove(part2[0])
                            combination.remove(part2[1])
                    if len(set(combination)) == 1:
                        ram[i] = ["ADD", [produit, 0, ram[i][1][2]]]
                        ram.remove(ram[i+1])
            if (ram[i][0] == "MULT" or ram[i][0] == "DIV") and (ram[i+1][0] == "ADD" or ram[i+1][0] == "SUB"):
                if ram[i][1][2] == ram[i+1][1][2]:
                    part1 = [elem for elem in ram[i][1]]
                    part2 = [elem for elem in ram[i+1][1]]
                    combination = part1 + part2
                    somme = 0
                    produit = 1
                    if ram[i][0] == "MULT":
                        for elem in part1:
                            if type(elem) != str:
                                produit *= elem
                                combination.remove(elem)
                    if ram[i][0] == "DIV":
                        produit = part1[0]
                        produit /= part1[1]
                        combination.remove(part1[0])
                        combination.remove(part1[1])
                    if ram[i+1][0] == "ADD":
                        for elem in part2:
                            if type(elem) != str:
                                somme += elem
                                combination.remove(elem)
                        somme += produit
                    if ram[i+1][0] == "SUB":
                        if type(part2[0]) != str and type(part2[1]) != str:
                            somme = part2[0]
                            somme -= part2[1]
                            combination.remove(part2[0])
                            combination.remove(part2[1])
                        elif type(part2[0]) != str and type(part2[1]) == str:
                            somme = part2[0]
                            somme -= produit
                            combination.remove(part2[0])
                            combination.remove(part2[1])
                        else:
                            somme = produit
                            somme -= part2[1]
                            combination.remove(part2[0])
                            combination.remove(part2[1])
                    
                    if len(set(combination)) == 1:
                        ram[i] = ["ADD", [somme, 0, ram[i][1][2]]]
                        ram.remove(ram[i+1])               
            if ram != ramDebut:
                combine(graph, ram)
            else:
                return ram
    except:
        return ram
        

def reconnect(graphOrig, graphMod, ramMod):
    ''' Permet de réassembler le graphe et le code RAM quand il y a eu une suppression'''
    if graphMod != graphOrig:
        keysOrig = list(graphOrig.keys())
        keysMod = list(graphMod.keys())
        valMod = list(graphMod.values())
        dico = {"FIN" : "FIN"}
        # on va crée un dictionnaire qui va changer les valeurs des sommets par exemple tous les sommets 6 vont être changer en sommet 4 si il y eu des suppressions de sommets
        for i in range(len(keysMod)):
            dico[keysMod[i]] = keysOrig[i]
        tempKey = []
        tempVal = []
        reconnected = dict()
        for elem in keysMod:
            tempKey.append(dico[elem])
        for liste in valMod:
            temp = []
            for elem in liste:
                temp.append(dico[elem])
            tempVal.append(temp)
        # on forme le noueau dictionnaire avec les bon sommets et valeurs
        for i in range(len(tempKey)):
            reconnected[tempKey[i]] = tempVal[i]    
        # on modifie le code RAM en fonction du nouveau graphe
        instruction = ["ADD", "SUB", "MULT", "DIV"]
        for i in range(len(ramMod)):
            if ramMod[i][0] not in instruction:
                j = 0
                for key, val in reconnected.items():
                    if j == i and type(val[-1]) != str:
                        ramMod[i][1][-1] = val[-1] - key
                    j += 1
        return reconnected, ramMod
    else:
        return graphOrig, ramMod


def q1(text):
    '''Le texte en entrée est stocké sous la forme d'une liste contenant les instructions. Les numéros des registres sont aussi réarangés pour qu'ils se suivent entre eux. Par exemple ['SUB', ['r3', 1, 'r3']]'''
    ram = convertTxt(text)
    for line in ram:
        print(line)

def q2(text, mot):
    '''Une configuration est donnée sous cette forme : [n, [I], [R], [O]]\n
          n : le numéro de l'instruction\n
          I : le registre input contenant le mot d'entrée et sa taille en I[0]\n
          R : le registre de travail avec la taille en R[0]\n
          O : le registre de sortie contenant la taille en O[0] et le résultat de l'éxécution de la machine RAM\n'''
    ram = convertTxt(text)
    config = initializeConfig(ram, mot)
    step(ram, config)

def q3(text, mot):
    ram = convertTxt(text)
    execRAM(ram, mot)

def q8(text):
    '''Le graphe est sous la forme d'un dictionaire dont les clés sont les numéros des instructions et les valeurs sont les numéros des instructions accessible depuis cette clé. Par exemple l'instruction ADD(2, 0, r0) donne {0 : [1]}'''
    print("Affichage simplifié pour la lecture :")
    ram = convertTxt(text)
    graph, ram = makeGraph(ram)
    for key, value in graph.items():
        print(f"{ram[key]} => {[ram[val] if val != 'FIN' else val for val in value]}")

def q9(text):
    ram = convertTxt(text)
    graph, ram = makeGraph(ram)
    graphCopy = graph.copy()
    graph, ram = deadCode(graph, ram)
    graph, ram = reconnect(graphCopy, graph, ram)
    print(f"Nouveau graphe : {graph}\nNouveau code RAM :")
    for elem in ram:
        print(elem)

def q10(text):
    ram = convertTxt(text)
    ramC = ram.copy()
    graph, ram = makeGraph(ram)
    graph, ram = deadCode(graph, ram)
    ram = combine(graph, ram)
    if ram != ramC:
        print("RAM simplifié :")
        for elem in ram:
            print(elem)
    else:
        print("Pas de simplifications trouvées")

def q3Ex():
    print("Exécution de a^b avec a = 2 et b = 4")
    ram = convertTxt("a_power_b.txt")
    execRAM(ram, [2, 4])

def q5Puissance():
    print("Code RAM de a puissance b : ")
    for elem in convertTxt("a_power_b.txt"):
        print(elem)

def q5Tri():
    print("Code RAM du tri à bulle : ")
    for elem in convertTxt("bubble_sort.txt"):
        print(elem)

def q6():
    print("Code RAM automate à pile : ")
    for elem in convertTxt("automata.txt"):
        print(elem)

def q7Ex():
    print("Exécution de a^n b^n avec le mot aabb")
    ram = convertTxt("automata.txt")
    execRAM(ram, [5,0,0,0,2,0,1,0,0,0,1,2,1,1,0,0,1,1,0,2,2,1,1,0,2,2,2,0,1,0,1, 0, 0, 1, 1])

def q8Ex():
    print(f"Graphe du code RAM correspondant à a^b :")
    q8("a_power_b.txt")

def q9Ex():
    print("Exemple de code mort avec le code RAM suivant :")
    for elem in convertTxt("code_mort.txt"):
        print(elem)
    q9("code_mort.txt")

def q10Ex():
    print("Exemple de simplification de code avec le code RAM suivant :")
    for elem in convertTxt("example_simplification.txt"):
        print(elem)
    q10("example_simplification.txt")

def reponses():
    print(f"\nRéponse à la question 1. Veuillez exécuter q1 avec un fichier pour voir un exemple.")
    print(q1.__doc__)

    print(f"\nRéponse à la question 2. Veuillez exécuter q2 avec un fichier pour voir un exemple.")
    print(q2.__doc__)

    print(f"\nRéponse à la question 3. Veuillez exécuter q3 avec un fichier et un mot pour voir un exemple, ou exécutez q3Ex.")

    print(f"\nRéponse à la question 5. Veuillez exécuter q5Puissance ou q5Tri pour voir un exemple donné, ou lancez q3 avec a_power_b.txt ou bubble_sort.txt avec le mot de votre choix.")
    print("Réponse à la question 6. Veuillez exécuter q6 pour voir le code RAM.")
    print("Réponse à la question 7. Veuillez exécuter q7Ex ou alors lancez q3 avec automata.txt et l'entrée 5,0,0,0,2,0,1,0,0,0,1,2,1,1,0,0,1,1,0,2,2,1,1,0,2,2,2,0,1,0,1, en ajoutant des 0 pour des a et des 1 pour des b.")
    print(q1.__doc__)

    print("Réponse à la question 8. Veuillez exécuter q8Ex pour voir un exemple défini ou alors exécuter q8 avec un fichier de votre choix.")
    print(q8.__doc__)

    print("Réponse à la question 9. Veuillez exécuter q9Ex pour voir un exemple ou alors exécuter q9 avec un fichier de votre choix.")

    print("Réponse à la question 10. Veuillez exécuter q10Ex pour voir un exemple ou alors exécuter q10 avec un fichier de votre choix.")


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

    fonctions_ex = {
        "q3Ex" : q3Ex,
        "q5Puissance" : q5Puissance,
        "q5Tri" : q5Tri,
        "q6" : q6,
        "q7Ex" : q7Ex,
        "q8Ex" : q8Ex,
        "q9Ex" : q9Ex,
        "q10Ex" : q10Ex,
        "reponses" : reponses
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
    elif sys.argv[1] in fonctions_ex:
        if len(sys.argv) == 2:
            # Exécution de la fonction spécifiée avec le fichier en entrée
            nom_fonction = sys.argv[1]
            fonction_a_executer = fonctions_ex[nom_fonction]
            fonction_a_executer()
        else:
            print(f"Usage de {sys.argv[1]}: python metasimulation.py <nom_fonction>")
    elif sys.argv[1] == "help":
        print("Fonctions disponibles :")
        print("reponses : Affiche les réponses aux questions et quelles commandes lancer pour avoir plus de détails.")
        print("q1 : Réponse de la question 1 en précisant les arguments.")
        print("q2 : Réponse de la question 2 en précisant les arguments.")
        print("q3 : Réponse de la question 3 en précisant les arguments.")
        print("q3Ex : Affiche un exemple d'exécution.")
        print("q5Puissance : Affiche un exemple d'exécution pour a^b.")
        print("q5Tri : Affiche un exemple d'exécution pour le tri à bulle.")
        print("q6 : Réponse de la question 6.")
        print("q7Ex : Affiche un exemple d'exécution avec le mot 'aabb'.")
        print("q8 : Réponse de la question 8 en précisant les arguments.")
        print("q8Ex : Affiche un exemple d'exécution pour a^b.")
        print("q9 : Réponse de la question 9 en précisant les arguments.")
        print("q9Ex : Affiche un exemple où il y a du code mort.")
        print("q10 : Réponse de la question 10 en précisant les arguments.")
        print("q10Ex : Affiche un exemple où il y a une simplification du code.")

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
