import React, { useEffect } from "react";
import { Link } from "react-router-dom";
import Card from "./Card";

function CommanderFacts({name}) {
    const [scryfallId, setScryfallId] = React.useState("");
    const [cardCount, setCardCount] = React.useState("");
    const [avgSynergyScore, setAvgSynergyScore] = React.useState("");
    const [similarCommanders, setSimilarCommanders] = React.useState([]);
    const [cmdImage, setCmdImage] = React.useState("");
    const [imageUris, setImageUris] = React.useState("");

    const formatCommanderName = (name) => {
        let formattedName = name.split(' // ')[0];
        if (formattedName.startsWith('A-')) {
            formattedName = formattedName.slice(2);
        }
        formattedName = formattedName.replace(/\s/g, '-');
        formattedName = formattedName.toLowerCase().replace(/[\s,"'.\u200B]/g, '');
        return formattedName;
    };

    useEffect(() => {
        const fetchCommanderFacts = async () => {
            const response = await fetch(`https://api.cardcognition.com/${formatCommanderName(name)}/info`);
            const data = await response.json();

            setScryfallId(data.scryfall_id);
            setCardCount(data.card_count);
            setAvgSynergyScore(data.avg_synergy_score);
            setSimilarCommanders(data.similar_commanders);
        };

        const fetchScryfallData = async () => {
            const response = await fetch(`https://api.scryfall.com/cards/${scryfallId}`);
            const data = await response.json();

            setCmdImage(data.image_uris.normal);
        };

        fetchCommanderFacts();
    }, [name]);

    return (
        <div>
            <h2>Commander Facts</h2>
            <Card scryfall_id={scryfallId} />
            <p>Average Synergy Score: {Math.round(avgSynergyScore * 100) / 100}</p>
            <p>Similar Commanders:</p>
            <ul>    
                {similarCommanders && similarCommanders.map((commander, index) => (
                    <li key={index}>
                        <p>{commander.name} - {Math.round(commander.overlap_percentage * 10) / 10}% overlap</p>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default CommanderFacts;
