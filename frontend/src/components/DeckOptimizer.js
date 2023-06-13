import React, { useState, useRef, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import useAutocomplete from '../hooks/useAutocomplete';
import useSuggestions from '../hooks/useSuggestions';
import useReductions from '../hooks/useReductions';
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
    const { reductions, isLoading: isReducing, fetchReductions } = useReductions(commander, 100);
    const { name: commanderFromUrl } = useParams(); // From the URL

    const commanderRef = useRef();

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
                        onClick={() => {
                            // Pick a random commander from this array:
                            const randomCommanders = [
                                "Urza, Lord High Artificer",
                                "K'rrik, Son of Yawgmoth",
                                "Niv-Mizzet Reborn",
                                "Kess, Dissident Mage",
                                "Yarok, the Desecrated",
                                "Armix, Filigree Thrasher",
                                "Atraxa, Praetors' Voice",
                                "Okaun, Eye of Chaos",
                                "Araumi of the Dead Tide",
                                "Purphoros, God of the Forge",
                                "Korvold, Fae-Cursed King",
                                "Queen Marchesa",
                                "Alela, Artful Provocateur",
                                "Phenax, God of Deception",
                                "Aegar, the Freezing Flame",
                                "Zndrsplt, Eye of Wisdom",
                                "Yahenni, Undying Partisan",
                                "Klothys, God of Destiny",
                                "Archangel Avacyn",
                                "Kozilek, Butcher of Truth",
                                "Kumena, Tyrant of Orazca",
                                "Rosheen Meanderer",
                            ];
                            const randomIndex = Math.floor(Math.random() * randomCommanders.length);
                            const randomCommander = randomCommanders[randomIndex];
                            setCommander(randomCommander);
                            fetchSuggestions(randomCommander);
                        }}
                    >Pick Random Commander</button>
                    <label htmlFor="decklist">Enter your deck list: (Optional)</label>
                    <textarea 
                        name="decklist" 
                        id="decklist" 
                        cols="30" 
                        rows="10" 
                        placeholder="Enter however you'd like: 1x Sol Ring, Sol Ring, 1 Sol Ring (1), etc." 
                        value={decklist} 
                        onChange={(e) => setDecklist(e.target.value)}
                    ></textarea>
                    <input type="submit" value="Generate" />
                </form>
            </div>
            <div className="commander-facts">
                {format === "commander" && commander !== "" && (
                    <CommanderFacts name={commander} />
                )}
            </div>
            <div className="card-reductions">
                <h2>Card Reductions</h2>
                <div>
                    {reductions.length > 0 && (
                        <p>Here are cards in your deck that are less likely to be included in a {commander} deck than other commanders of the same color identity:</p>
                    )}
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
