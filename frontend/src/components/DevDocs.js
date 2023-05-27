import './DevDocs.css';

function DevDocs() {
    return (
        <article className="api-docs">
            <header>
                <h1>Card Cognition API Documentation</h1>
                <p>
                    Welcome to the developer documentation for the Card Cognition REST API. This API is currently in beta, and we appreciate your understanding that changes may be implemented during this phase.
                </p>
                <p>
                    For proper use of this API, it's important to format commander names correctly: 
                </p>
                <ol>
                    <li>Remove all non-alphanumeric characters</li>
                    <li>Replace spaces with hyphens</li>
                    <li>Convert to lowercase</li>
                </ol>
                <ul>
                    <li>"Atraxa, Praetor's Voice" =&gt; "atraxa-praetors-voice"</li>
                    <li>"Esika God of the Tree // the Prismatic Bridge" =&gt; "esika-god-of-the-tree"</li>

                </ul>
                <p>The base URL for all API requests is <code>https://api.cardcognition.com</code>.</p>
            </header>
            <section>
                <h2>API Endpoints</h2>
                <h3>GET /dbinfo</h3>
                <p>Returns the average synergy score (by card and by commander), the number of commanders, the number of card-commander pairs, and the number of unique cards in the database.</p>
                <pre>
                    <code> 
                        {
`{
    "avg_commander_synergy_score": "6.4862930421185716",
    "avg_synergy_score": "5.9592683877016941",
    "card_commander_pairs_count": 454339,
    "commander_count": 1706,
    "unique_card_count": 18032
}`
                        }
                    </code>
                </pre>

                <h3>GET /:formatted-commander-name/info</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Parameter</th>
                            <th>Type</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>:formatted-commander-name</td>
                            <td>String</td>
                            <td>The name of the commander, properly formatted as outlined above.</td>
                        </tr>
                        <tr>
                            <td>info</td>
                            <td>Endpoint</td>
                            <td>Endpoint that returns the commander's information including its average synergy score, the number of associated cards, and similar commanders.</td>
                        </tr>
                    </tbody>
                </table>
                <p>Example usage: <pre><code>https://api.cardcognition.com/urza-lord-high-artificer/info</code></pre></p>
                <h4>Response Structure</h4>
                <p>The API response is structured as a JSON object. The similar commanders are sorted by overlapping cards percentage in descending order.</p>
                <pre>
                    <code>
                        {
`{
    "avg_synergy_score": "2.9328719723183391",
    "card_count": 289,
    "name": "urza-lord-high-artificer",
    "scryfall_id": "9e7fb3c0-5159-4d1f-8490-ce4c9a60f567",
    "similar_commanders": [
        {
            "name": "the-reality-chip",
            "overlap_count": 207,
            "overlap_percentage": "71.6262975778546713",
            "scryfall_id": "d859de3a-0be1-4e66-b438-1c3d4ee756cd"
        },
        {
            "name": "emry-lurker-of-the-loch",
            "overlap_count": 202,
            "overlap_percentage": "69.8961937716262976",
            "scryfall_id": "20fec02d-77af-4975-b410-7097c7c28e7e"
        },
        ...
    ]
}`
                        }
                    </code>
                </pre>

                <h3>GET /:formatted-commander-name/suggestions/:count/</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Parameter</th>
                            <th>Type</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>:formatted-commander-name</td>
                            <td>String</td>
                            <td>The name of the commander, properly formatted as outlined above.</td>
                        </tr>
                        <tr>
                            <td>suggestions</td>
                            <td>Endpoint</td>
                            <td>Endpoint that returns card suggestions for the given commander.</td>
                        </tr>
                        <tr>
                            <td>:count</td>
                            <td>Integer</td>
                            <td>The desired number of card suggestions to be returned.</td>
                        </tr>
                    </tbody>
                </table>
                <p>Example usage: <pre><code>https://api.cardcognition.com/urza-lord-high-artificer/suggestions/3</code></pre></p>
                <h4>Response Structure</h4>
                <p>The API response is structured as a JSON object. Suggestions are sorted by score in descending order. In an upcoming update, a "next" key will be included for easy pagination.</p>
                <pre>
                    <code>
                        {
`{
    "count": "3",
    "suggestions": [
        {
            "name": "Arcum's Astrolabe",
            "score": "11.5",
            "scryfall_id": "c2462fdf-a594-47d0-8e10-b55901e350d9"
        },
        {
            "name": "Static Orb",
            "score": "10.6",
            "scryfall_id": "86bf43b1-8d4e-4759-bb2d-0b2e03ba7012"
        },
        {
            "name": "Darksteel Relic",
            "score": "10.0",
            "scryfall_id": "0fd8c918-62d9-41be-a3e1-32ddac71b7e7"
        }
    ]
}`
                        }
                    </code>
                </pre>
            </section>
        </article>
    );
};

export default DevDocs
