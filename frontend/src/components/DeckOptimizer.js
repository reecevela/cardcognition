import React, { useState, useRef } from 'react';
import useAutocomplete from './useAutocomplete';
import useSuggestions from './useSuggestions';

function DeckOptimizer() {
    const [format, setFormat] = useState("commander");
    const [commander, setCommander] = useState("");
    const [decklist, setDecklist] = useState("");
    const [isDropdownVisible, setDropdownVisibility] = useState(false);

    const { suggestions, isLoading } = useAutocomplete(commander);
    const { suggestions: cardSuggestions, fetchSuggestions } = useSuggestions(commander, 100);

    const commanderRef = useRef();

    const handleSubmit = async (e) => {
        e.preventDefault();
        await fetchSuggestions();
    };

    const handleCommanderChange = (e) => {
        setCommander(e.target.value);
        setDropdownVisibility(true);
    };

    const handleSuggestionClick = (suggestion) => {
        setCommander(suggestion);
        setDropdownVisibility(false);
    };

    const handleFormatChange = (e) => {
        setFormat(e.target.value);
        if (e.target.value === "commander") {
            commanderRef.current.style.display = "block";
        } else {
            commanderRef.current.style.display = "none";
        }
    };

    return (
        <section className="optimizer">
            <h2>Deck Optimizer</h2>
            <div className="deck-entry">
                <form onSubmit={handleSubmit}>
                    <label htmlFor="format">Format:</label>
                    <select name="format" id="format" value={format} onChange={handleFormatChange}>
                        <option value="commander">Commander</option>
                        <option value="modern">Modern (Currently Unsupported)</option>
                        <option value="legacy">Legacy (Currently Unsupported)</option>
                    </select>
                    <div className="autocomplete">
                        <label htmlFor="commander">Commander:</label>
                        <input list="commanders" name="commander" id="commander" value={commander} onChange={handleCommanderChange} ref={commanderRef} />
                        <datalist id="commanders">
                            {suggestions.map((suggestion, index) => (
                                <option value={suggestion} key={index} />
                            ))}
                        </datalist>
                    </div>
                    <label htmlFor="decklist">Enter your deck list:</label>
                    <textarea name="decklist" id="decklist" cols="30" rows="10" placeholder="Lightning Bolt" value={decklist} onChange={(e) => setDecklist(e.target.value)}></textarea>
                    <input type="submit" value="Generate" />
                </form>
            </div>
            <div className="card-suggestions">
                <h2>Recommended Cards</h2>
                {
                    cardSuggestions
                    .filter(([card]) => !decklist.toLowerCase().split('\n').includes(card.toLowerCase())) // Exclude cards already in decklist
                    .slice(0, 3) // Take top 3
                    .map(([card, score], index) => (
                        <div key={index}>
                            <p>{card} - Score: {score}</p>
                        </div>
                    ))
                }
            </div>
        </section>
    );
}

export default DeckOptimizer;
