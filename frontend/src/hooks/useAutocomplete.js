import { useState, useEffect, useCallback } from 'react';
import debounce from 'lodash/debounce';

export default function useAutocomplete(query) {
    const [suggestions, setSuggestions] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    const fetchSuggestions = useCallback(debounce(async (query) => {
        setIsLoading(true);
        if (query.length >= 2) {
            const response = await fetch(
                `https://api.scryfall.com/cards/search?q=${encodeURIComponent(
                `(${query}) (t:creature t:legendary or t:planeswalker)`
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
    }, 100), []); // debounce time is 100ms

    useEffect(() => {
        fetchSuggestions(query);
    }, [query, fetchSuggestions]);

    return {suggestions, isLoading};
}
