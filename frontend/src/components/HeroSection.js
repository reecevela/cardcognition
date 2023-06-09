import React, { useEffect, useState } from 'react';
import AIImage1 from '../images/ai1.webp';
import AIImage2 from '../images/ai2.webp';
import AIImage3 from '../images/ai3.webp';
import AIImage4 from '../images/ai4.webp';
import AIImage5 from '../images/ai5.webp';
import AIImage6 from '../images/ai6.webp';
import { Link } from 'react-router-dom';

const images = [
    AIImage1,
    AIImage2,
    AIImage3,
    AIImage4,
    AIImage5,
    AIImage6,
];

function HeroSection() {
    const [backgroundImage, setBackgroundImage] = useState('');

    useEffect(() => {
        const updateBackgroundImage = () => {
            const image = images[Math.floor(Math.random() * images.length)];
            setBackgroundImage(`linear-gradient(to right, rgba(0, 0, 0, 1), rgba(0, 0, 0, 0)), url(${image})`);
        }

        updateBackgroundImage();
        const interval = setInterval(updateBackgroundImage, 5000);

        return () => clearInterval(interval);
    }, []);

    return (
        <section className="hero" style={{ backgroundImage }}>
            <div className="left">
                <h1>Card Cognition</h1>
                <p>Upload some or all of your deck. Instantly get suggestions on what to add or remove. Make better decks and have fun winning more games!</p>
            </div>
            <div className="right">
                <Link to="/" className="cta">Optimize your deck</Link>
            </div>
        </section>
    );
}

export default HeroSection;