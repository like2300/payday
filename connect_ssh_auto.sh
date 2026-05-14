#!/bin/bash

# Configuration
HOST="ssh-payday.alwaysdata.net"
USER="payday"
PASS='Brazzaville0!'

# Vérifier si sshpass est installé
if ! command -v sshpass &> /dev/null; then
    echo "Erreur : 'sshpass' n'est pas installé."
    exit 1
fi

echo "Connexion instantanée à $USER@$HOST..."

# -o PubkeyAuthentication=no : ignore les clés locales pour aller plus vite
# -o PreferredAuthentications=password : force le mode mot de passe
# -o StrictHostKeyChecking=no : évite la question de sécurité
sshpass -p "$PASS" ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no -o StrictHostKeyChecking=no "$USER@$HOST"
