import React from "react";
import { useEffect } from "react";

function Card({ name, score, scryfall_id }) {
    const [imageUrl, setImageUrl] = React.useState("");
    const [affiliateLink, setAffiliateLink] = React.useState("");
    const [cardPrice, setCardPrice] = React.useState(0);

    useEffect(() => {
        const fetchScryfallData = async () => {
            const response = await fetch(`https://api.scryfall.com/cards/${scryfall_id}`);
            const data = await response.json();
            const affiliateCode = "CARDCOGNITION";

            setImageUrl(data.image_uris.normal);
            setCardPrice(data.prices.usd);
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
            <a href={affiliateLink} target="_blank" rel="noreferrer">Buy on TCGplayer - ${cardPrice}</a>
        </div>
    );
}

export default Card;