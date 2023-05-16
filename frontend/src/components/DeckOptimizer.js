import React, { useState, useRef } from 'react';
import useAutocomplete from './useAutocomplete';

function DeckOptimizer() {
    const [format, setFormat] = useState("commander");
    const [commander, setCommander] = useState("");
    const [decklist, setDecklist] = useState("");
    const [isDropdownVisible, setDropdownVisibility] = useState(false);

    const { suggestions, isLoading } = useAutocomplete(commander);

    const commanderRef = useRef();

    const handleSubmit = (e) => {
        e.preventDefault();
        console.log(format, commander, decklist);
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
            commanderRef.current.style.display = "none";
        } else {
            commanderRef.current.style.display = "block";
        }
    };

    return (
        <section className="optimizer">
            <h2>Deck Optimizer</h2>
            <div className="deck-entry">
                <form onSubmit={handleSubmit}>
                    <select name="format" id="format" value={format} onChange={handleFormatChange}>
                        <option value="commander">Commander</option>
                        <option value="modern">Modern</option>
                        <option value="legacy">Legacy</option>
                    </select>
                    <label htmlFor="commander">Commander:</label>
                    <div className="autocomplete">
                        <input type="text" name="commander" id="commander" value={commander} onChange={handleCommanderChange} ref={commanderRef} />
                        {isDropdownVisible && !isLoading && (
                            <div className="autocomplete-dropdown">
                                {
                                    suggestions.length === 0 ? (
                                        <div>No suggestions</div>
                                    ) : (
                                        suggestions.map((suggestion, index) => (
                                            <div key={index} onClick={() => handleSuggestionClick(suggestion)}>
                                                {suggestion}
                                            </div>
                                        ))
                                    )
                                }
                            </div>
                        )}
                    </div>
                    <label htmlFor="decklist">Enter your deck list:</label>
                    <textarea name="decklist" id="decklist" cols="30" rows="10" placeholder="Lightning Bolt" value={decklist} onChange={(e) => setDecklist(e.target.value)}></textarea>
                    <input type="submit" value="Generate" />
                </form>
            </div>
        </section>
    );
}

export default DeckOptimizer;
