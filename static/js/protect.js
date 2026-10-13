// Page 1 : verification email via HIBP range API (k-anonymite)
// L'email N'EST JAMAIS envoye au serveur. Hash SHA-1 cote navigateur,
// seul le prefixe de 5 caracteres transite.
const form = document.getElementById('hibp-form');
const resultBox = document.getElementById('result');
const emailInput = document.getElementById('email');
const consentBox = document.getElementById('consent');

async function sha1Hex(str) {
  const buf = await crypto.subtle.digest('SHA-1', new TextEncoder().encode(str));
  return [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, '0')).join('').toUpperCase();
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  if (!consentBox.checked) return;
  const email = emailInput.value.trim().toLowerCase();
  if (!email) return;
  resultBox.hidden = false;
  resultBox.className = 'result';
  resultBox.textContent = 'Verification en cours...';
  try {
    // journaliser le consentement (sans l'email)
    fetch('/api/consent', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({consent:true, purpose:'email_breach_check'})});
    const hash = await sha1Hex(email);
    const prefix = hash.slice(0, 5);
    const suffix = hash.slice(5);
    const resp = await fetch('/api/hibp-range/' + prefix);
    const data = await resp.json();
    if (data.error) throw new Error(data.error);
    const count = data.matches[suffix] || 0;
    if (count > 0) {
      resultBox.className = 'result bad';
      resultBox.textContent = 'Attention : cet email apparait dans ' + count + ' fuite(s) de donnees connues (bases HaveIBeenPwned).\n\n=> Change ton mot de passe active sur cet email, et active la double authentification ou tu le peux.';
    } else {
      resultBox.className = 'result ok';
      resultBox.textContent = 'Bonne nouvelle : aucune fuite connue pour cet email dans les bases HaveIBeenPwned. Continue quand meme a utiliser des mots de passe uniques.';
    }
  } catch (err) {
    resultBox.className = 'result bad';
    resultBox.textContent = 'Erreur lors de la verification : ' + err.message;
  }
});
