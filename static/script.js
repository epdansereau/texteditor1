let currentFilename = null;
let currentPassword = null;

document.getElementById('open-btn').addEventListener('click', async () => {
    const filename = document.getElementById('filename').value;
    const password = document.getElementById('password').value;
    const resp = await fetch('/api/open', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename, password })
    });
    const data = await resp.json();
    if (!resp.ok) {
        alert(data.error);
        return;
    }
    currentFilename = filename;
    currentPassword = password;
    document.getElementById('filename').value = '';
    document.getElementById('password').value = '';
    document.getElementById('auth').style.display = 'none';
    document.getElementById('editor').style.display = 'block';
    document.getElementById('text').value = data.content || '';
});

document.getElementById('save-btn').addEventListener('click', () => save(currentFilename, currentPassword));

document.getElementById('saveas-btn').addEventListener('click', async () => {
    const filename = prompt('File name:');
    const password = prompt('Password:');
    if (!filename || !password) return;
    currentFilename = filename;
    currentPassword = password;
    await save(filename, password);
});

document.getElementById('new-btn').addEventListener('click', () => {
    currentFilename = null;
    currentPassword = null;
    document.getElementById('text').value = '';
    document.getElementById('editor').style.display = 'none';
    document.getElementById('auth').style.display = 'block';
});

async function save(filename, password) {
    const content = document.getElementById('text').value;
    const resp = await fetch('/api/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename, password, content })
    });
    const data = await resp.json();
    if (!resp.ok) {
        alert(data.error);
    } else {
        alert('Saved');
    }
}
