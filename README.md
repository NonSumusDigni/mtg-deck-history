# mtg-deck-history
A collection of MTG decks from tournament results across time.

There are two goals for this project:
1. A person can download this repository and browse the formats and decks without any extra tooling or technical skills required.
2. A person can use the data programmatically. The structure of this repository is in service of the first goal, primarily, so tooling will need to be built that generates JSON or other useful formats.

In order to serve both goals, the directory names, file names, and file structures must adhere to a strict specification. Currently, this structure is only implied, but a more formal specification is TODO.

Currently, this is very much a work in progress. I am in the process of adding decks from every GP top 8, PT/MC top 8, and any equivalent level top 8 (Masters, Nationals, etc.). I am up to (chronologically) 2001 Nationals season. The focus at the moment is adding decks. Future work will involve tools and visualizations based on the data.

## TODO list
(1. Add all the decks)
- Sort out STN-2001-04-7ED archetype names - Fires vs. No Fires, Machine Head vs. Void, Orbosition vs. Opp-Orb 
- Get exact dates for epoch boundaries (to the extent possible)
- Write specification (file names, deck names, folder structure, etc.)
- Write CONTRIBUTING.md to guide possible helpers
- Set up webhooks to run validation on PRs
- Set up webhooks to trigger builds of a JSON version of the collection
- Look into automatic ingestion of contemporary results (from MTG Goldfish or MTG Top 8 maybe)
