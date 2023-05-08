export const initAutocomplete = (function () {
    const commanderInput = document.getElementById("commander");
    const suggestionsList = document.createElement("datalist");
    suggestionsList.id = "suggestions";
    commanderInput.setAttribute("list", "suggestions");
    document.body.appendChild(suggestionsList);

    commanderInput.addEventListener("input", async function (event) {
        const query = event.target.value;
        if (query.length >= 2) {
            const response = await fetch(
                `https://api.scryfall.com/cards/search?q=${encodeURIComponent(
                `(${query}) (t:creature t:legendary or t:planeswalker)`
                )}&unique=cards&order=name&dir=asc`
            );
            const data = await response.json();
            updateSuggestions(data.data.map((card) => card.name));
        } else {
            updateSuggestions([]);
        }
    });

    function updateSuggestions(suggestions) {
    suggestionsList.innerHTML = "";
    suggestions.forEach((suggestion) => {
        const option = document.createElement("option");
        option.value = suggestion;
        suggestionsList.appendChild(option);
    });
    }
});
