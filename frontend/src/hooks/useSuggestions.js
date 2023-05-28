import { useState, useCallback } from 'react';
import formatCommanderName from '../helpers/formatCommanderName';

export default function useSuggestions(commanderName, count = 100) {
    const [suggestions, setSuggestions] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const BASE_URL = "https://api.cardcognition.com";

    const fetchSuggestions = useCallback(async (name = commanderName) => {
        setIsLoading(true);
        try {
            const response = await fetch(`${BASE_URL}/${formatCommanderName(name)}/suggestions/${count}`);
            const data = await response.json();

            const suggestionsData = data.suggestions.map(({name, score, scryfall_id}) => {
                return [name, score, scryfall_id];
            });

            // Remove duplicates
            const uniqueSuggestions = suggestionsData.filter((suggestion, index, self) => {
                return index === self.findIndex((s) => (
                    s[0] === suggestion[0] && s[1] === suggestion[1] && s[2] === suggestion[2]
                ));
            });

            setSuggestions(uniqueSuggestions);
        } catch (error) {
            setError(error.message);
        } finally {
            setIsLoading(false);
        }
    }, [commanderName, count]);

    return { suggestions, isLoading, error, fetchSuggestions };
}
