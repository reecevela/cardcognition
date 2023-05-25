import React, { useState, useRef, useEffect } from 'react';
import useAutocomplete from '../hooks/useAutocomplete';
import useSuggestions from '../hooks/useSuggestions';
import Card from './Card';

function DeckOptimizer() {
    const [format, setFormat] = useState("commander");
    const [commander, setCommander] = useState("");
    const [decklist, setDecklist] = useState("");

    const { suggestions, isLoading } = useAutocomplete(commander);
    const { suggestions: cardSuggestions, fetchSuggestions } = useSuggestions(commander, 100);

    const commanderRef = useRef();

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (commander !== "") {
            await fetchSuggestions();
        }
    };

    const handleCommanderInputBlur = async (e) => {
        // Set the commander to the most likely suggestion
        const commanderSuggestions = suggestions.filter(
            (suggestion) => suggestion.toLowerCase().startsWith(commander.toLowerCase())
        );
    
        let finalCommander = commander;
    
        if (commanderSuggestions.length > 0) {
            finalCommander = commanderSuggestions[0];
        } else if (suggestions.length > 0) {
            finalCommander = suggestions[0];
        }
    
        setCommander(finalCommander);
        // Fetch suggestions for the most likely suggestion
        await fetchSuggestions(finalCommander);
    };
    
    
    const handleCommanderChange = (e) => {
        setCommander(e.target.value);
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
            <div className="deck-entry">
                <h2>Deck Optimizer</h2>
                <form onSubmit={handleSubmit}>
                    <label htmlFor="format">Format:</label>
                    <select name="format" id="format" value={format} onChange={handleFormatChange}>
                        <option value="commander">Commander</option>
                        <option value="modern">Modern (Currently Unsupported)</option>
                        <option value="legacy">Legacy (Currently Unsupported)</option>
                    </select>
                    <label htmlFor="commander">Commander:</label>
                    <div className="autocomplete">
                        <input 
                            list="commanders" 
                            name="commander" 
                            id="commander" 
                            value={commander} 
                            onChange={handleCommanderChange} 
                            ref={commanderRef} 
                            onBlur={handleCommanderInputBlur} 
                            onKeyDown={(e) => { if (e.keyCode === 13) handleCommanderInputBlur(e); }}
                        />
                        <datalist id="commanders">
                            {suggestions.map((suggestion, index) => (
                                <option value={suggestion} key={index} />
                            ))}
                        </datalist>
                    </div>
                    <label htmlFor="decklist">Enter your deck list: (Optional)</label>
                    <textarea name="decklist" id="decklist" cols="30" rows="10" placeholder="Lightning Bolt" value={decklist} onChange={(e) => setDecklist(e.target.value)}></textarea>
                    <input type="submit" value="Generate" />
                </form>
            </div>
            <div className="card-suggestions">
                <div className="card-list">
                    {cardSuggestions
                        .filter(([name]) => !decklist.toLowerCase().split('\n').includes(name.toLowerCase())) // Exclude cards already in decklist
                        .slice(0, 12)
                        .map(([card, score, scryfall_id], index) => (
                            <Card key={index} name={card} score={score} scryfall_id={scryfall_id} />
                        ))
                    }
                    {
                        (cardSuggestions.length === 0 && !isLoading) && (
                            <Card name="No Suggestions to Display" score={0} scryfall_id="aaafb9bc-7cea-4624-a227-595544fa42b0" />
                        )
                    }
                </div>
            </div>
        </section>
    );
}

export default DeckOptimizer;
