const form = document.getElementById('delete-form');
const resultBox = document.getElementById('result');
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const email = document.getElementById('email').value.trim();
  if (!email) return;
  resultBox.hidden = false;
  resultBox.className = 'result';
  resultBox.textContent = 'Envoi...';
  try {
    const resp = await fetch('/api/delete-request', {method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({email})});
    const data = await resp.json();
    if (data.error) throw new Error(data.error);
    resultBox.className = 'result ok';
    resultBox.textContent = data.message + ' Gratuit, sans condition.';
  } catch (err) {
    resultBox.className = 'result bad';
    resultBox.textContent = 'Erreur : ' + err.message;
  }
});
