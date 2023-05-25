# cardcognition

View Live: https://cardcognition.com

## Introduction:

Cardcognition is a way to find the best cards to add to your Magic: The Gathering Commander deck. You enter your commander, then you can optionally add some cards from your deck. As soon as you click generate, the most synergistic cards for your deck are shown for you. Each card's synergy score is calculated using the following formula:

"How many times more frequently is {selected card} included in a deck helmed by {specific commander}, compared to that card's rate of inclusion in commander decks of the exact same color identity?"

Cards that you already have in your deck are not included in the suggestion. In total, there are over half a million commander-card-score entries!

## How it works:

1. Automated Data Collection/Cleaning: In the backend/app_extras folder, there's a collection of Python scripts that do the following:
- Query the Scryfall API to get a list of every legal commander in existence
- Format all the names and save them in a text file. Ex. "Sephara, Sky's Blade" => "sephara-skys-blade"
- Use the formatted names to go to each commander's EDHREC url, then scrape all of the frequency data for each card on the page
- Run the calculations, and query Scryfall again to get each synergy-card's unique Scryfall ID, saving each relation in a Postgres Database


2. Cloud-Deployed Containerized Backend Architecture: The backend resides on a DigitalOcean server. Here's some cool stuff about it:
- It exposes API endpoints at [https://api.cardcognition.com/{commander-name}/suggestions/{count}](https://api.cardcognition.com/urza-lord-high-artificer/suggestions/30) (you can click that link to test it out)
- Initializing each microservice (Web app, gunicorn, nginx, db, db_volume) is orchestrated via Docker Compose, making it very easy to update and deploy
- The nginx service generates a self-signed certificate each time it starts, which is why the app can be served over HTTPS
- Figuring out CORS, error handling, database connections, and getting it all to run in a Docker network was definitely a learning experience lol


3. React Frontend: The frontend isn't too complex at this point, but it handles client-side tasks such as:
- Fetches data from the backend, and image data by going through: scryfall_id from backend > image_uri from api.scryfall/id > .png from scryfall.io endpoint
- Uses a custom hook for the Commander AutoComplete feature, that only queries for commanders
- I had a bunch of issues with displaying the card suggestions, but the best implementation I've found is by using custom <Card /> components I made


## Future improvements and potential features:

1. Machine Learning: I already know how I'm going to approach this, but I just haven't had time yet. For each commander's cards, I'm going to use the Bag-of-Words technique with the synergy score as a positive reinforcement to create a model for what kinds of cards are synergistic with each commander. Users would be able to get scores for each card in their deck, and even new cards the moment they're released without any playtest data.


2. User interface: In the future, Cardcognition will have a more complex userface with more features, such as user accounts and being able to save your decks. I'd also want to gamify it to get people to use it more, whether it's through points or a leaderboard for usage. Probably even a way to share your suggestions with Twitter.


3. Monetization: Through affiliate marketing with TCGPlayer (Clicking "Buy" on the card suggestions and receiving a commission), advertising, Patreon, however. I just want this to make more money than it costs to host it on DigitalOcean. Just a sidenote here, this is closed-source and I (Reece Vela) own it fully, just in case.
