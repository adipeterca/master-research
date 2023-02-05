# Cellular automata forest
A simple CA inspired by the [forest-fire](https://en.wikipedia.org/wiki/Forest-fire_model) model.
Implemented using [p5.js](https://p5js.org/).

## Rules
1. There are only 3 types of trees:
	* green tree
	* burning tree
	* empty cell (no tree)
2. For each generation:
	* a **burning tree** will become an **empty cell**
	* an **empty cell** will become a **green tree** with probability `grow_chance`
	* a **green tree** with at least a **burning tree** adjacent to it ([Moore distance](https://en.wikipedia.org/wiki/Moore_neighborhood)) has probability `burning_chance` of catching on fire
	* a **green tree* which does not catch on fire has probability `thunder_chance` to be struck by lightning and catch of fire
	
## Interaction
The user can click on any **green** square to start a fire. Subsequent clicks also start other fires, but usually the automaton handles itself after the initial cell has been selected.