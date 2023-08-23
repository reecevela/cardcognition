import React, { useState, useRef, useEffect, Component } from 'react';
import { useParams } from 'react-router-dom';
import Card from './Card';
import useAutocomplete from '../hooks/useAutocomplete';

function DeckAnalyzer() {
    const [commander, setCommander] = useState("");
    const [card, setCard] = useState("");
    const [decklist, setDecklist] = useState("");
    const { suggestions, isLoading } = useAutocomplete(commander);
    const { cardAutoSuggestions, isCardLoading } = useAutocomplete(card, false);

    const commanderRef = useRef();
    const cardRef = useRef();

    const handleSubmit = async (e) => {
        e.preventDefault();
    }

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
    };

    const handleCommanderChange = (e) => {
        setCommander(e.target.value);
    };

    const handleCardChange = (e) => {
        setCard(e.target.value);
    };

    const handleCardInputBlur = async (e) => {
        // Set the card to the most likely suggestion
        const cardSuggestions = cardAutoSuggestions.filter(
            (suggestion) => suggestion.toLowerCase().startsWith(card.toLowerCase())
        );

        let finalCard = card;

        if (cardSuggestions.length > 0) {
            finalCard = cardAutoSuggestions[0];
        } else if (suggestions.length > 0) {
            finalCard = cardAutoSuggestions[0];
        }

        setCard(finalCard);

        setDecklist(decklist + "\n" + finalCard);
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
                            {cardAutoSuggestions.map((suggestion, index) => (
                                <option value={suggestion} key={index} />
                            ))}
                        </datalist>
                    </div>
                    <label htmlFor="decklist">Enter your Decklist:</label>
                    <textarea 
                        name="decklist" 
                        id="decklist" 
                        cols="30" 
                        rows="10"
                        placeholder="Enter however you'd like: 1x Sol Ring, Sol Ring, 1 Sol Ring (1), etc." 
                        value={decklist} 
                        onChange={(e) => setDecklist(e.target.value)}
                    ></textarea>
                    <input type="submit" value="Submit" />
                </form>
            </div>
        </section>
    )
}

export default DeckAnalyzer;
