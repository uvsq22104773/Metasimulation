# mon_programme.py
import re

def fonction1(nom_fichier):
    with open(nom_fichier, 'r') as fichier:
        contenu = fichier.read()
    print("Contenu du fichier :", contenu)

def fonction2(nom_fichier):
    with open(nom_fichier, 'a') as fichier:
        fichier.write("\nNouvelle ligne ajoutée")

def a():
    print("tout le programme executer")

def convertTxt(nom_fichier):
    with open(nom_fichier, 'r') as fichier:
        contenu = fichier.readlines()
    res = []
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
                res.append([operation, [operand1]])
                continue
            try:
                operand2 = int(operand2)
            except:
                pass
            try:
                operand3 = int(operand3)
            except:
                pass
            res.append([operation, (operand1, operand2, operand3)])
        else:
            continue
    return res
    

def step(ram, config):
    '''config = [indice, I, R, O]
        avec I la liste d'input du genre [2, a, b]
        R = [k, r1, r2, ..., rk]
        O = [n, o1, ..., on]'''
    instruction = ram[config[0]]
    print(f"Instrution : {instruction}")
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
            c, pos1, pos2 = registre(c, config)
            # ajoute dans la liste O le bon nombre d'emplacement si il y en a pas assez
            if pos1 == 3 and pos2 == 0:
                while (len(config[pos1])-2) != config[pos1][0]:
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


def initializeConfig(ram, mot):
    config = [0, mot, [], [0]]
    config[2].extend([""] * len(set(re.findall(r'r[0-9]+', str(ram)))))
    return config


def execRAM(ram, mot):
    config = initializeConfig(ram, mot)
    while config[0] < len(ram):
        step(ram, config)
    config[-1] = [elem for elem in config[-1] if elem != 0.0]
    config[-1][0] = len(config[-1]) - 1
    print(f"Résultat final : {config[-1]}")


ram = convertTxt("a_power_b.txt")
execRAM(ram, [2, 2, 3])

'''if __name__ == "__main__":
    import sys

    # Mapping entre les arguments de ligne de commande et les fonctions
    fonctions_disponibles = {
        "fonction1": fonction1,
        "fonction2": fonction2
    }

    # Vérification des arguments de ligne de commande
    if len(sys.argv) < 1:
        print("Usage: python mon_programme.py <nom_fichier> <nom_fonction>")
        sys.exit(1)
    
    # Vérification de la présence d'un fichier en entrée
    if len(sys.argv) == 3 and sys.argv[2] in fonctions_disponibles:
        # Exécution de la fonction spécifiée avec le fichier en entrée
        nom_fonction = sys.argv[2]
        fonction_a_executer = fonctions_disponibles[nom_fonction]
        nom_fichier = sys.argv[1]
        fonction_a_executer(nom_fichier)
    elif len(sys.argv) == 2:
        nom_fichier = sys.argv[1]
        a()
    else:
        if len(sys.argv) == 3:
            print("Fonction non disponible.")
        else:
            print("Veuillez spécifier un fichier en entrée.")'''
