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
                <p></p>
                <p>For instance, "Atraxa, Praetor's Voice" should be formatted as "atraxa-praetors-voice".</p>
                <p>The base URL for all API requests is <code>https://api.cardcognition.com</code>.</p>
            </header>
            <section>
                <h2>API Endpoints</h2>
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
                <p>Example usage: <code>https://api.cardcognition.com/urza-lord-high-artificer/suggestions/3</code></p>
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
