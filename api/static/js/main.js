window.Telegram.WebApp.ready();
const initData = Telegram.WebApp.initData || '';
const initDataUnsafe = Telegram.WebApp.initDataUnsafe || {};

if (initData) {
    fetch('/auth', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(initDataUnsafe)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'authenticated') {
            document.getElementById('message').textContent = `Welcome, ${data.username}`;
            document.getElementById('edit-username').style.display = 'block';
        } else {
            document.getElementById('message').textContent = data.message;
        }
    });
}

function updateUsername() {
    const newUsername = document.getElementById('username').value;
    fetch('/update_username', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({username: newUsername})
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            document.getElementById('message').textContent = `Username updated to ${data.username}`;
        } else {
            document.getElementById('message').textContent = data.message;
        }
    });
}
