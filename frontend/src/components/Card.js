import React from "react";
import { useEffect } from "react";

function Card({ name, score, scryfall_id }) {
    const [imageUrl, setImageUrl] = React.useState("");

    useEffect(() => {
        const fetchImage = async () => {
            const imgResponse = await fetch(`https://api.scryfall.com/cards/${scryfall_id}`);
            const imgData = await imgResponse.json();

            setImageUrl(imgData.image_uris.normal);
        };

        fetchImage();
    }, [scryfall_id]);

    return (
        <div className="card">
            <p>{name} - {score}</p>
            <img src={imageUrl} alt={name} />
        </div>
    );
}

export default Card;