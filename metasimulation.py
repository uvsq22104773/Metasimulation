# mon_programme.py

def fonction1(nom_fichier):
    with open(nom_fichier, 'r') as fichier:
        contenu = fichier.read()
    print("Contenu du fichier :", contenu)

def fonction2(nom_fichier):
    with open(nom_fichier, 'a') as fichier:
        fichier.write("\nNouvelle ligne ajoutée")

def a():
    print("tout le programme executer")

if __name__ == "__main__":
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
            print("Veuillez spécifier un fichier en entrée.")
