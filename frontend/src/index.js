import './styles.css'
import AIImage1 from './images/ai1.png'
import AIImage2 from './images/ai2.png'
import AIImage3 from './images/ai3.png'
import AIImage4 from './images/ai4.png'
import AIImage5 from './images/ai5.png'
import AIImage6 from './images/ai6.png'
import { initAutocomplete } from './autocomplete'

const images = [
    AIImage1,
    AIImage2,
    AIImage3,
    AIImage4,
    AIImage5,
    AIImage6,
];

const hero = document.querySelector('.hero');

document.addEventListener('DOMContentLoaded', () => {
    initAutocomplete();

    // Hero background image
    const heroLinearGradients = [
        'rgba(0, 0, 0, 1)',
        'rgba(255, 255, 255, 0.3)',
        'rgba(0, 0, 0, 1)',
    ];
    hero.style.backgroundImage = `linear-gradient(${heroLinearGradients.join(', ')}), url(${images[Math.floor(Math.random() * images.length)]})`;
    setInterval(() => {
        hero.style.backgroundImage = `linear-gradient(${heroLinearGradients.join(', ')}), url(${images[Math.floor(Math.random() * images.length)]})`;
    }, 5000);
});

// Deck optimizer section
const deckEntry = document.querySelector('.deck-entry');

/*
<div class="deck-entry">
                <form action="GET">
                    <select name="format" id="format">
                        <option value="commander">Commander</option>
                        <option value="modern">Modern</option>
                        <option value="legacy">Legacy</option>
                    </select>
                    <label for="commander">Commander:</label>
                    <input type="text" name="commander" id="commander">
                    <label for="decklist">Enter your deck list:</label>
                    <textarea name="decklist" id="decklist" cols="30" rows="10" placeholder="Lightning Bolt"></textarea>
                    <input type="submit" value="Generate">
                </form>
            </div>
*/

deckEntry.addEventListener('submit', (e) => {
    e.preventDefault();
    const format = document.querySelector('#format').value;
    const commander = document.querySelector('#commander').value;
    const decklist = document.querySelector('#decklist').value;
    console.log(format, commander, decklist);

});