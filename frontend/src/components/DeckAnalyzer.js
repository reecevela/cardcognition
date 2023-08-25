import React, { useState, useRef, useEffect, Component } from 'react';
import { useParams } from 'react-router-dom';
import Card from './Card';
import useAutocomplete from '../hooks/useAutocomplete';
import formatCommanderName from '../helpers/formatCommanderName';

function DeckAnalyzer() {
    const [commander, setCommander] = useState("");
    const [card, setCard] = useState("");
    const [cardsData, setCardsData] = useState([]);
    const [decklist, setDecklist] = useState([]);
    const { suggestions: commanderAutoSuggestions, isLoading: isCommanderLoading } = useAutocomplete(commander);
    const { suggestions: cardAutoSuggestions, isLoading: isCardLoading } = useAutocomplete(card, false);

    const commanderRef = useRef();
    const cardRef = useRef();

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (commander == "") {
            return;
        }

        // const commander = "Urza, Lord High Artificer"

        const formattedCommander = formatCommanderName(commander);

        const cardsInfo = await fetch(`https://localhost:5000/analyze/${encodeURIComponent(formattedCommander)}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: {
                "values": {
                    "cards": decklist /*
                    "cards": [
                        "Sol Ring",
                        "Mana Crypt",
                        "Mana Vault",
                        "Mox Opal",
                        "Waste Not",
                        "Necropotence",
                        "Lightning Bolt",
                        "Greater Gargadon",
                        "Doomsday",
                        "Honor of the Pure",
                        "Swords to Plowshares",
                        "Mystical Tutor",
                        "Cyclonic Rift", */
                }
            }
        });

        setCardsData(await cardsInfo.json());
    }

    const handleCommanderInputBlur = async (e) => {
        // Set the commander to the most likely suggestion
        const commanderSuggestions = commanderAutoSuggestions.filter(
            (suggestion) => suggestion.toLowerCase().startsWith(commander.toLowerCase())
        );
    
        let finalCommander = commander;
    
        if (commanderSuggestions.length > 0) {
            finalCommander = commanderSuggestions[0];
        } else if (commanderAutoSuggestions.length > 0) {
            finalCommander = commanderAutoSuggestions[0];
        }
    
        setCommander(finalCommander);
    };

    
    const handleCardInputBlur = async (e) => {
        // Set the card to the most likely suggestion
        const cardSuggestions = cardAutoSuggestions.filter(
            (suggestion) => suggestion.toLowerCase().startsWith(card.toLowerCase())
        );

        let finalCard = card;

        if (cardSuggestions.length > 0) {
            finalCard = cardSuggestions[0];
        } else if (cardAutoSuggestions.length > 0) {
            finalCard = cardAutoSuggestions[0];
        }

        setCard("");

        setDecklist([...decklist, finalCard]);
    };

    const handleCommanderChange = (e) => {
        setCommander(e.target.value);
    };

    const handleCardChange = (e) => {
        setCard(e.target.value);
    };

    return (
        <section className="optimizer">
            <div className="deck-entry">
                <h2>Deck Optimizer</h2>
                <form onSubmit={handleSubmit}>
                    <label htmlFor="commander">Enter your Commander:</label>
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
                    </div>
                    <label htmlFor="card">Enter a Card:</label>
                    <div className="autocomplete">
                        <input
                            list="cards"
                            name="card"
                            id="card"
                            placeholder="Sol Ring..."
                            value={card}
                            onChange={handleCardChange}
                            ref={cardRef}
                            onBlur={handleCardInputBlur}
                            onKeyDown={(e) => { if (e.keyCode === 13) handleCardInputBlur(e); }}
                        />
                        <datalist id="cards">
                            {cardAutoSuggestions && cardAutoSuggestions.map((suggestion, index) => (
                                <option value={suggestion} key={index} />
                            ))}
                        </datalist>
                    </div>
                    <label htmlFor="decklist">Your Decklist:</label>
                    {decklist && decklist.map((card, index) => (
                        <div key={index} className=''>{card}</div>
                    ))}
                    <input type="submit" value="Submit" />
                </form>
            </div>
            <div>{cardsData}</div>
        </section>
    )
}

export default DeckAnalyzer;