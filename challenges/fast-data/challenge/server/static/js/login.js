document.getElementById("connectBtn").addEventListener("click", login);

async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const rep = await fetch("/api/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username,
            password,
        }),
    });

    const data = await rep.json();
    document.getElementById("msg").innerHTML = data.msg;
}
