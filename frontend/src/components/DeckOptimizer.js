import React, { useState, useRef, useEffect } from 'react';
import useAutocomplete from '../hooks/useAutocomplete';
import useSuggestions from '../hooks/useSuggestions';
import Card from './Card';
import CommanderFacts from './CommanderFacts';

function DeckOptimizer() {
    const [format, setFormat] = useState("commander");
    const [commander, setCommander] = useState("");
    const [decklist, setDecklist] = useState("");
    const [cardCount, setCardCount] = useState(12);
    const [normalizedDecklist, setNormalizedDecklist] = useState("");

    const { suggestions, isLoading } = useAutocomplete(commander);
    const { suggestions: cardSuggestions, fetchSuggestions } = useSuggestions(commander, 100);

    const commanderRef = useRef();

    const normalizeCardName = name => name.replace(/[^a-z0-9]/g, '');
    const normalizeDecklist = list => list.toLowerCase().replace(/[^a-z0-9]/g, '');

    useEffect(() => {
        const normalizedList = normalizeDecklist(decklist);
        setNormalizedDecklist(normalizedList);
    }, [decklist]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (commander !== "") {
            setCardCount(12);
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
        setCardCount(12);
        // Fetch suggestions for the most likely suggestion
        await fetchSuggestions(finalCommander);
    };

    const loadMore = () => {
        setCardCount(cardCount + 12);
    };
    
    
    const handleCommanderChange = (e) => {
        setCommander(e.target.value);
        setCardCount(12);
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
            <div className="commander-facts">
                {format === "commander" && commander !== "" && (
                    <CommanderFacts name={commander} />
                )}
            </div>
            <div className="card-suggestions">
                <h2>Card Suggestions</h2>
                <div className="card-list">
                    {cardSuggestions
                        .filter(([name]) => !normalizedDecklist.includes(normalizeCardName(name.toLowerCase()))) // Exclude cards already in decklist
                        .slice(0, cardCount)
                        .map(([card, score, scryfall_id], index) => (
                            <Card key={index} name={card} score={score} scryfall_id={scryfall_id} />
                        ))
                    }
                    {
                        cardSuggestions.length === 0 && (
                            <p>No suggestions found.</p>
                        )
                    }
                </div>
            </div>
            <div className='load-more'>
                {cardSuggestions.length > 0 && !isLoading && cardSuggestions.length > cardCount && (
                    <button onClick={loadMore}>Load More</button>
                )}
            </div>
        </section>
    );
}

export default DeckOptimizer;
