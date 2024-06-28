window.Telegram.WebApp.ready();
const initData = Telegram.WebApp.initData || '';
const initDataUnsafe = Telegram.WebApp.initDataUnsafe || {};
console.log("start");
if (initData) {
    console.log("receive");
    fetch('/auth', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(initData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                document.getElementById('message').textContent = `Welcome, ${data.username}`;
                document.getElementById('edit-username').style.display = 'block';
            } else {
                document.getElementById('message').textContent = data.message;
            }
        });
}