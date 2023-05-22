import React, { useState, useRef, useEffect } from 'react';
import useAutocomplete from '../hooks/useAutocomplete';
import useSuggestions from '../hooks/useSuggestions';
import Card from './Card';

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
        if (commander !== "") {
            await fetchSuggestions();
        }
    };

    const handleCommanderChange = (e) => {
        setCommander(e.target.value);
        setDropdownVisibility(true);
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
                    <label htmlFor="commander">Commander:</label>
                    <div className="autocomplete">
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
                <div className="card-list">
                    {cardSuggestions
                        .filter(([name]) => !decklist.toLowerCase().split('\n').includes(name.toLowerCase())) // Exclude cards already in decklist
                        .slice(0, 10)
                        .map(([card, score, scryfall_id], index) => (
                            <Card key={index} name={card} score={score} scryfall_id={scryfall_id} />
                        ))
                    }
                </div>
            </div>
        </section>
    );
}

export default DeckOptimizer;
