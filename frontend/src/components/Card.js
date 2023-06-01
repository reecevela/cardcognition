import React, { useEffect} from "react";
import { logEvent } from "firebase/analytics";
import { analytics } from "../index";
import fetchCardData from "../helpers/fetchCardData";

function Card({ name, score, scryfall_id }) {
    const [imageUrl, setImageUrl] = React.useState("");
    const [affiliateLink, setAffiliateLink] = React.useState("");
    const [cardPrice, setCardPrice] = React.useState(0);
    const [foilCardPrice, setFoilCardPrice] = React.useState(0);

    useEffect(() => {
        const fetchScryfallData = async () => {
            const data = await fetchCardData(scryfall_id);
            const affiliateCode = "CARDCOGNITION";

            setImageUrl(data.image_uris.normal);
            setCardPrice(data.prices.usd);
            setFoilCardPrice(data.prices.usd_foil);
            setAffiliateLink(`https://www.tcgplayer.com/product/${data.tcgplayer_id}?utm_campaign=affiliate&utm_medium=${affiliateCode}&utm_source=${affiliateCode}`);

        };

        fetchScryfallData();
    }, [scryfall_id, name]);

    const handleClick = () => {
        // Analytics through google
        logEvent(analytics, "card_click", {
            name: name,
            time: new Date().toString(),
        });

        window.open(affiliateLink, "_blank");
    };

    return (
        <div className="card">
            {
                score ? (
                    <p>{name} - {score}x</p>
                ) : (
                    <p>{name}</p>
                )
            }
            <img src={imageUrl} alt={name} onClick={handleClick} />
            <a href={affiliateLink} target="_blank" rel="noreferrer">Click to Buy: ${(cardPrice !== null) ? cardPrice : (foilCardPrice) ? foilCardPrice : "Price unavailable"}</a>
        </div>
    );
}

export default Card;