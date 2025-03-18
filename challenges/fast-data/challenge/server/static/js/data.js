document.getElementById("btn").addEventListener("click", search);

async function search() {
    const s = document.getElementById("searchValue").value;
    const response = await fetch(`/api/data?s=${s}`);

    const data = await response.json();

    const searchText = document.getElementById("searchText");
    searchText.removeAttribute("hidden");
    searchText.innerHTML = "Results for " + data.search;

    displayData(data.data);
}

function displayData(data) {
    const itemTemplate = document.getElementById("data").cloneNode(true);
    const dataContainer = document.getElementById("dataContainer");
    const title = document.getElementById("title").cloneNode(true);

    while (dataContainer.firstChild) {
        dataContainer.removeChild(dataContainer.firstChild);
    }

    dataContainer.appendChild(title);
    dataContainer.appendChild(itemTemplate)

    data.forEach(element => {
        var newElement = itemTemplate.cloneNode(true);
        newElement.childNodes[1].innerHTML = element[0];
        newElement.childNodes[1].removeAttribute("hidden");
        newElement.childNodes[3].innerHTML = element[1];
        newElement.childNodes[3].removeAttribute("hidden");
        newElement.removeAttribute("hidden");
        dataContainer.appendChild(newElement);
    });
}