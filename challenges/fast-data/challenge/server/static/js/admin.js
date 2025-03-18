async function getAdminInfo() {
    const rep = await fetch("/api/admin");
    const json = await rep.json();

    const msgElement = document.getElementById("msg");
    msgElement.innerText = json.msg
}

getAdminInfo();
