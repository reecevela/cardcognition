import React, { useEffect } from "react";
import Card from "./Card";
import "./CommanderFacts.css"
import formatCommanderName from "../helpers/formatCommanderName";
import { Link } from "react-router-dom";

function CommanderFacts({name}) {
    const [scryfallId, setScryfallId] = React.useState("");
    const [avgSynergyScore, setAvgSynergyScore] = React.useState("");
    const [similarCommanders, setSimilarCommanders] = React.useState([]);

    useEffect(() => {
        const fetchCommanderFacts = async () => {
            const response = await fetch(`https://api.cardcognition.com/${formatCommanderName(name)}/info`);
            const data = await response.json();

            setScryfallId(data.scryfall_id);
            setAvgSynergyScore(data.avg_synergy_score);
            setSimilarCommanders(data.similar_commanders);
        };

        fetchCommanderFacts();
    }, [name]);

    const explainScore = (score) => {
        let phrase = "";
        if (score < 2 ) {
            phrase = `${name} has a synergy score of ${score}, meaning there are not commander-specific "must-include" cards and players building this deck generally pick from a similar card pool. This could mean that it's built with generically powerful cards, or that it supports a wide variety of strategies.`;
        } else if (score < 4) {
            phrase = `${name} has a synergy score of ${score}, indicating that while there are some specific cards that synergize well with this commander, a significant portion of the deck is composed of cards that could fit into many other decks. This could mean that the commander is flexible in terms of strategy, or that there are several staple cards that fit well in the deck.`;
        } else if (score < 6) {
            phrase = `${name} has a synergy score of ${score}, suggesting a balanced mix of commander-specific and general-purpose cards. This could suggest a unique yet flexible strategy where the deck is built around the commander's abilities or a central theme, but not in such a way that excludes staple cards.`;
        } else if (score < 8) {
            phrase = `${name} has a synergy score of ${score}, showing a strong focus on commander-specific cards. This could suggest that the deck has a very focused strategy based on the commander's abilities or a focused synergy. Cards in this deck are likely to be very specific to the deck's strategy, and may not be useful in other decks.`;
        } else {
            phrase = `${name} has a synergy score of ${score}, meaning that it uses a very off-the wall and uncommon strategy. You'll find unusual cards in this deck, which may support a very linear deckbuilding plan. It's also possible that the theme this commander supports does not have a large card pool, meaning the few relevant cards are present in most instances of this deck.`;
        }
        return phrase;  
    }    

    return (
        <section className="commander-facts">
            <h2>Commander Facts</h2>
            <div class="commander-facts-data">
                <div class="center">                
                    <Card name={name} scryfall_id={scryfallId} />
                </div>
                <div>
                    <p>{explainScore(Math.round(avgSynergyScore * 100) / 100)}</p>
                    <p>Similar Commanders: (% Similarity)</p>
                    <ul>
                        {similarCommanders && similarCommanders.map((commander, index) => (
                            <li key={index}>
                                <Link to={`/commander/${commander.card_name}`} className="commander-link">
                                    {commander.card_name} - {Math.round(commander.overlap_percentage * 10) / 10}%
                                </Link>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        </section>
    );
}

export default CommanderFacts;
