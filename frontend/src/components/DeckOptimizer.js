import React, { useState, useRef, useEffect, Component } from 'react';
import { useParams } from 'react-router-dom';
import Card from './Card';
import useAutocomplete from '../hooks/useAutocomplete';
import useSuggestions from '../hooks/useSuggestions';
import useReductions from '../hooks/useReductions';
import CommanderFacts from './CommanderFacts';

function DeckOptimizer() {
    const [format, setFormat] = useState("commander");
    const [commander, setCommander] = useState("");
    const [decklist, setDecklist] = useState("");
    const [cardCount, setCardCount] = useState(12);
    const [normalizedDecklist, setNormalizedDecklist] = useState("");
    const [showDeckEntry, setShowDeckEntry] = useState(false);

    const { suggestions, isLoading } = useAutocomplete(commander);
    const { suggestions: cardSuggestions, fetchSuggestions } = useSuggestions(commander, 100);
    const { reductions, isLoading: isReducing, fetchReductions } = useReductions(commander, 100);
    const { name: commanderFromUrl } = useParams(); // From the URL

    const commanderRef = useRef();
    const initialized = useRef(false);

    const normalizeCardName = name => name.toLowerCase().replace(/[^a-z0-9]/g, '');
    const normalizeDecklist = list => list.toLowerCase().replace(/[^a-z0-9]/g, '');

    // Handles commander routing from the url directly
    // Also used in the similar commanders
    useEffect(() => {
        if (commanderFromUrl) {
            setCommander(commanderFromUrl);
            fetchSuggestions(commanderFromUrl);
            fetchReductions(commanderFromUrl);
        }
    }, [commanderFromUrl]);

    // Handles changes in the decklist
    useEffect(() => {
        const normalizedList = normalizeDecklist(decklist);
        setNormalizedDecklist(normalizedList);
    }, [decklist]);

    useEffect(() => {
        console.log("Reductions: ", reductions);
    }, [reductions]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (commander !== "") {
            setCardCount(12);
            await fetchSuggestions();
            await fetchReductions();
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
        await fetchReductions(finalCommander);
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
    
    const getRandomCommander = async () => {
        const response = await fetch("https://api.cardcognition.com/random-commander");
        const data = await response.json();
        const randomCommander = data.commander_name;
        setCommander(randomCommander);
        await fetchSuggestions(randomCommander);
        await fetchReductions(randomCommander);
        setCardCount(12);
        return data;
    };

    // init
    useEffect(() => {
        if (!commanderFromUrl && !initialized.current) {
            initialized.current = true;
            getRandomCommander();
        }
    }, []);
    
    return (
        <section className="optimizer">
            <div className="deck-entry">
                <h2>Deck Optimizer</h2>
                <form onSubmit={handleSubmit}>
                    {
                        false && "not implemented yet" && (
                            <>
                            <label htmlFor="format">Format:</label>
                            <select name="format" id="format" value={format} onChange={handleFormatChange}>
                                <option value="commander">Commander</option>
                                <option value="modern">Modern (Currently Unsupported)</option>
                                <option value="legacy">Legacy (Currently Unsupported)</option>
                            </select>
                            </>
                        )
                    }
                    <label htmlFor="commander">Enter any Commander:</label>
                    <div className="autocomplete">
                        <input 
                            list="commanders" 
                            name="commander" 
                            id="commander"
                            placeholder="Urza, Lord High Artificer..."
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
                    <button 
                        type="button"
                        className='button-random'
                        onClick={getRandomCommander}
                    >Pick Random Commander</button>
                    <label htmlFor="decklist">Enter your Decklist: (Optional)</label>
                    <textarea 
                        name="decklist" 
                        id="decklist" 
                        cols="30" 
                        rows={showDeckEntry ? 10 : 1} 
                        placeholder="Enter however you'd like: 1x Sol Ring, Sol Ring, 1 Sol Ring (1), etc." 
                        value={decklist} 
                        onChange={(e) => {setDecklist(e.target.value); (e.target.value !== "") ? setShowDeckEntry(true) : setShowDeckEntry(false);}}
                    ></textarea>
                </form>
            </div>
            <div className="commander-facts">
                {format === "commander" && commander !== "" && (
                    <CommanderFacts name={commander} />
                )}
            </div>
            <div className="card-reductions">
                {reductions.length > 0 && reductions.filter(([name]) => normalizedDecklist.includes(normalizeCardName(name))).length > 0 && (
                    <>
                    <h2>Card Reductions</h2>
                    <p>Here are cards in your deck that are less likely to be included in a {commander} deck than other commanders of the same color identity:</p>
                    </>
                )}
                <div>
                    <ul className='reductions-list'>
                        {reductions
                            .filter(([name]) => normalizedDecklist.includes(normalizeCardName(name))) // Only includes cards in the decklist
                            .map(([card, percentage, score, scryfall_id], index) => (
                                <li key={index}>
                                    <p>{card} -{Math.round((1 - score) * 100)}% frequency</p>
                                </li>
                            ))
                        }
                    </ul>
                    {
                        reductions.length === 0 && (
                            <p>Enter a decklist to see reductions.</p>
                        )
                    }
                </div>
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
