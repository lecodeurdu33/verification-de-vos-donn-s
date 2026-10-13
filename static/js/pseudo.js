const form = document.getElementById('pseudo-form');
const resultBox = document.getElementById('result');
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const username = document.getElementById('username').value.trim();
  const consent = document.getElementById('consent').checked;
  if (!username || !consent) return;
  resultBox.hidden = false;
  resultBox.className = 'result';
  resultBox.textContent = 'Scan des profils publics en cours...';
  try {
    const resp = await fetch('/api/pseudo-check', {method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({username, consent:true})});
    const data = await resp.json();
    if (data.error) throw new Error(data.error);
    if (data.found.length === 0) {
      resultBox.className = 'result ok';
      resultBox.textContent = 'Aucun profil public trouve avec ce pseudo sur les plateformes testees.';
    } else {
      resultBox.className = 'result bad';
      resultBox.textContent = 'Ton pseudo est public sur ' + data.found.length + ' plateforme(s) sur ' + data.checked + ' testees :\n\n' +
        data.found.map(f => '- ' + f.platform + ' : ' + f.url).join('\n') +
        '\n\n=> Rends ces profils prives si tu le souhaites, ou change de pseudo pour casser le lien entre eux.';
    }
  } catch (err) {
    resultBox.className = 'result bad';
    resultBox.textContent = 'Erreur : ' + err.message;
  }
});
