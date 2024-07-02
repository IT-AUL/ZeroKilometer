window.Telegram.WebApp.ready();
const initData = Telegram.WebApp.initData || '';
console.log("start");
if (initData) {
    fetch('/auth', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({user_data: initData})
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