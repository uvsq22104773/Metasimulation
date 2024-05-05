# README - Metasimulation

Ce script Python `metasimulation.py` est conçu pour effectuer différentes opérations sur un code de machine RAM (Random Access Machine). Il offre plusieurs fonctionnalités, notamment la conversion de fichiers texte contenant du code RAM en une représentation interne, l'exécution de ce code avec une configuration donnée, l'analyse et la simplification du code, et bien plus encore. 
'''Ce projet à été réalisé par MACHE Ethan et JOLY Théo.'''

## Instructions d'exécution

### Prérequis

Assurez-vous que vous disposez d'une version de Python 3 installée sur votre système.

### Étapes pour exécuter le script

1. **Clonage du dépôt**

   Clonez ce dépôt dans votre répertoire local en utilisant la commande suivante :

   ```bash
   git clone https://github.com/uvsq22104773/Metasimulation/tree/main
   ```

2. **Navigation vers le répertoire**

   Allez dans le répertoire du projet :

   ```bash
   cd metasimulation
   ```

3. **Exécution du script**

   Pour exécuter le script, utilisez la commande suivante :

   ```bash
   python metasimulation.py <nom_fonction> <nom_fichier> <mot_d_entree>
   ```

   Remplacez `<nom_fonction>` par le nom de la fonction que vous souhaitez exécuter (par exemple `q1`, `q2`, `q3`, etc.), `<nom_fichier>` par le chemin du fichier contenant le code RAM, et `<mot_d_entree>` par une liste d'entrée pour la fonction correspondante.

4. **Exemples d'utilisation**

   Voici quelques exemples d'utilisation :

   - Pour afficher toutes les réponses aux questions :
     ```bash
     python metasimulation.py reponses
     ```

   - Pour convertir un fichier de code RAM en une représentation interne et afficher les instructions :
     ```bash
     python metasimulation.py q1 fichier_ram.txt
     ```

   - Pour exécuter le code RAM avec une configuration donnée :
     ```bash
     python metasimulation.py q3 fichier_ram.txt 2,4,6
     ```

   - Pour afficher le graphe orienté du code RAM :
     ```bash
     python metasimulation.py q8 fichier_ram.txt
     ```

   - Pour simplifier le code RAM en supprimant les instructions mortes :
     ```bash
     python metasimulation.py q9 fichier_ram.txt
     ```

   - Pour exécuter toutes les simplifications possibles sur le code RAM :
     ```bash
     python metasimulation.py q10 fichier_ram.txt
     ```

   - Pour voir les fonctions disponibles :
     ```bash
     python metasimulation.py help
     ```

   - Pour voir les exemples de fichiers disponibles dans le dépôt :
     ```bash
     python metasimulation.py file
     ```

## Remarques

- Assurez-vous que le fichier de code RAM est au format texte et qu'il suit la syntaxe correcte attendue par le script.
- Les entrées de données doivent être fournies sous forme de liste pour certaines fonctions qui le nécessitent. Veillez à respecter ce format lors de l'exécution du script.
