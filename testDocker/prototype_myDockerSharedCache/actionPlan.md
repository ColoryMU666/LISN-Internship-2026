# Action plan

## Overall plan

Quand on reçoit la requête on zip notre cache et on l'envoie à notre client.
Le client l'unzip et il a son cache tout propre

## Server side

Quand on reçoit la requête elle contient un lockfile d'uv. On va d'abord le télécharger et créer un venv temporaire dans lequel on va télécharger toutes les librairies demandées pour forcer uv à les mettre dans le cache. Comme le cache est dans le volume utilisateur, les autres conteneur y ont aussi accès. 

## Client side

Le client demande des paquets au server en lui envoyant l'uv.lock de l'environement qu'il demande.

La réponse à se requête est le signal que le cache dans le volume utilisateur est rempli avec les données nécéssaire à la contruction/utilisation des paquets demandés.

## Asumptions made 

Dans ce plan d'action on estime que le client se fiche de la taille du cache qu'il va recevoir, lui il veut juste pouvoir contruire les paquets qu'il demande. De plus on ne se soucis pas encore de la sécurité (le zip que je reçoit contient bien un cache uv tout ce qu'il y a de plus normal et il n'y a pas de risque qu'il contienne des paquets vérolés.). Enfin on suppose que le client et le serveur tournent sour la même distrib du même os, ou au moins que le cache uv du server est exploitable sur le client.