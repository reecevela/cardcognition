import { useState, useEffect, useCallback } from 'react';
import debounce from 'lodash/debounce';

export default function useAutocomplete(query, commander = true) {
    const [suggestions, setSuggestions] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    const fetchSuggestions = useCallback(
        debounce(async (query) => {
            setIsLoading(true);
            let apiUrl;
            if (commander) {
                apiUrl = `https://api.scryfall.com/cards/search?q=${encodeURIComponent(
                    `(${query}) (is:commander game:paper -is:digital)`
                )}&unique=cards&order=edhrec`;
            } else {
                apiUrl = `https://api.scryfall.com/cards/autocomplete?q=${encodeURIComponent(
                    query
                )}`;
            }
            const response = await fetch(apiUrl);
            const data = await response.json();
            if (data.data) {
                if (commander) {
                    setSuggestions(data.data.map((card) => card.name));
                } else {
                    // Assuming the card autocomplete returns an array of strings
                    setSuggestions(data.data);
                }
            } else {
                setSuggestions([]);
            }
            setIsLoading(false);
        }, 50),
        [commander]
    ); // debounce time is 50ms

    useEffect(() => {
        fetchSuggestions(query);
    }, [query, fetchSuggestions]);

    return { suggestions, isLoading };
}
