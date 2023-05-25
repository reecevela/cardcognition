import { useState, useEffect, useCallback } from 'react';
import debounce from 'lodash/debounce';

export default function useAutocomplete(query) {
    const [suggestions, setSuggestions] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    const fetchSuggestions = useCallback(debounce(async (query) => {
        setIsLoading(true);
        if (query.length >= 1) {
            const response = await fetch(
                `https://api.scryfall.com/cards/search?q=${encodeURIComponent(
                `(${query}) (is:commander game:paper -is:digital)`
                )}&unique=cards&order=name&dir=asc`
            );
            const data = await response.json();
            if (data.data) {
                setSuggestions(data.data.map((card) => card.name));
            } else {
                setSuggestions([]);
            }
        } else {
            setSuggestions([]);
        }
        setIsLoading(false);
    }, 50), []); // debounce time is 50ms

    useEffect(() => {
        fetchSuggestions(query);
    }, [query, fetchSuggestions]);

    return {suggestions, isLoading};
}
