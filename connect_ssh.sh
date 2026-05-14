#!/bin/bash

# Configuration
HOST="ssh-payday.alwaysdata.net"
USER="payday"

echo "Connexion à $USER@$HOST..."
echo "Attendez l'apparition du message 'password:', puis tapez votre mot de passe."

# Forcer le mot de passe et ignorer les clés locales pour éviter le blocage
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no "$USER@$HOST"
