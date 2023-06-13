import { useState, useCallback } from 'react';
import formatCommanderName from '../helpers/formatCommanderName';

export default function useReductions(commanderName, count = 100) {
    const [reductions, setReductions] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const BASE_URL = "https://api.cardcognition.com";

    const fetchReductions = useCallback(async (name = commanderName) => {
        setIsLoading(true);
        try {
            const response = await fetch(`${BASE_URL}/${formatCommanderName(name)}/reductions/${count}`);
            const data = await response.json();

            const reductionsData = data.reductions.map(({name, percentage, score, scryfall_id}) => {
                return [name, percentage, score, scryfall_id];
            });

            // Remove duplicates
            const uniqueReductions = reductionsData.filter((reduction, index, self) => {
                return index === self.findIndex((s) => (
                    s[0] === reduction[0] && s[1] === reduction[1] && s[2] === reduction[2]
                ));
            });

            setReductions(uniqueReductions);
        } catch (error) {
            setError(error.message);
        } finally {
            setIsLoading(false);
        }
    }, [commanderName, count]);

    return { reductions, isLoading, error, fetchReductions };
}
