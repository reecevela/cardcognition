import React from "react";
import { useEffect } from "react";

function Card({ name, score, scryfall_id }) {
    const [imageUrl, setImageUrl] = React.useState("");
    const [affiliateLink, setAffiliateLink] = React.useState("");

    useEffect(() => {
        const fetchScryfallData = async () => {
            const response = await fetch(`https://api.scryfall.com/cards/${scryfall_id}`);
            const data = await response.json();
            const affiliateCode = "CARDCOGNITION";

            setImageUrl(data.image_uris.normal);
            setAffiliateLink(`https://www.tcgplayer.com/product/${data.tcgplayer_id}?utm_campaign=affiliate&utm_medium=${affiliateCode}&utm_source=${affiliateCode}`);
        };

        fetchScryfallData();
    }, [scryfall_id]);

    const handleClick = () => {
        // Open affiliate link in new tab
        window.open(affiliateLink, "_blank");
    };

    return (
        <div className="card">
            <p>{name} - {score}</p>
            <img src={imageUrl} alt={name} onClick={handleClick} />
            <a href={affiliateLink} target="_blank" rel="noreferrer">Buy on TCGplayer</a>
        </div>
    );
}

export default Card;