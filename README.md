# Vérifier vos données (BrixHub Safe)

Moteur de **protection** anti-doxxing, 100% legal et RGPD-friendly.
Pas un moteur de dox : aucune donnee hackee, aucune donnee sensible, suppression gratuite.

Accessible depuis appl-ia.fr/compte-vole (redirection via la variable BRIXHUB_SAFE_URL cote applia).

## Pages (MVP)
1. **/protect** - Verifie si ton email a fui (HaveIBeenPwned, k-anonymite : l'email ne quitte jamais l'appareil, seul un prefixe de hash SHA-1 est envoye)
2. **/pseudo** - Empreinte pseudo : scan de profils deja publics (GitHub, Reddit, Instagram, TikTok, YouTube)
3. **/delete** - Droit a l'oubli gratuit et instantane (RGPD art. 17)
4. **/legal** - Mentions legales, base legale, durees de conservation

## Conformite RGPD integree
- Case "Je certifie que ce sont mes propres donnees" (consentement, art. 6(1)(a))
- Journalisation horodatee des consentements (art. 7(1) : pouvoir demontrer le consentement)
- Minimisation : l'email n'est jamais stocke ni transmis en clair pour la verification
- Hebergement UE requis (Scaleway / OVH) pour la mise en production
- Suppression gratuite (art. 17), sans condition ni paiement

## Stack
- Flask (Python) - meme pattern que tes autres projets, deployable sur Railway ou Scaleway
- Front vanilla : le hash SHA-1 est calcule via WebCrypto dans le navigateur

## Lancer en local
```bash
pip install -r requirements.txt
python app.py
```

## Deploiement et lien avec appl-ia.fr
1. Deployer ce repo sur Railway (ou Scaleway/OVH pour l'hebergement UE)
2. Dans les variables d'environnement du service applia, definir BRIXHUB_SAFE_URL = URL de ce service
3. appl-ia.fr/compte-vole redirige alors automatiquement vers l'outil

## Roadmap
- [ ] Page pseudo : elargir via les donnees publiques WhatsMyName (wmn-data.json)
- [ ] BrixHub OSINT Pro : verification d'entreprises (Pappers.fr - donnees publiques RNE)
- [ ] Rate limiting (Flask-Limiter) avant mise en ligne
