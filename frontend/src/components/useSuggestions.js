import { useState, useEffect } from 'react';

export default function useSuggestions(commanderName, count = 100) {
    const [suggestions, setSuggestions] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const BASE_URL = "https://api.cardcognition.com";

    const formatCommanderName = (name) => {
        let formattedName = name.split(' // ')[0];
        if (formattedName.startsWith('A-')) {
            formattedName = formattedName.slice(2);
        }
        formattedName = formattedName.replace(/\s/g, '-');
        formattedName = formattedName.toLowerCase().replace(/[\s,"'.\u200B]/g, '');
        return formattedName;
    };

    const fetchSuggestions = async () => {
        setIsLoading(true);
        try {
            const response = await fetch(`${BASE_URL}/${formatCommanderName(commanderName)}/suggestions/${count}`);
            const data = await response.json();
            setSuggestions(data.suggestions);
        } catch (error) {
            setError(error.message);
        } finally {
            setIsLoading(false);
        }
    };
    
    useEffect(() => {
        fetchSuggestions();
    }, [commanderName, count]);

    return { suggestions, isLoading, error, fetchSuggestions };
}
