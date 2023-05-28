const fetchCardData = async (scryfallId) => {
    const response = await fetch(`https://api.scryfall.com/cards/${scryfallId}`);
    const data = await response.json();

    return data;
};

export default fetchCardData;