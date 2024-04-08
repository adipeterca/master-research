# Requests
1. Closest unknown cell from player
	: Ask for one random cell from the closest unknown position set. For example, if the player knows only North and East, it will take a random cell from [South, West]. However, if all 1-step-away cells are known, then a random cell from 2-step-away cells is selected.
2. DFS Heuristic based
	: At the start of the match, create a DFS heuristic map from start point to finish. At each step, request the next unknown cell in this chain.
3.  Random cell
	: Request a random unknown cell, without any information taken into account.
4. Copy offer
	: If the previous negotiation failed, request the offered cell. Otherwise request a random cell.
5. Full Determined
	: Select an unknown cell at random and request it until get it (even if multiple negotiation sessions are required).
6. Semi Determined
	: Select an unknown cell at random and request it until the current negotiation session ends. 
7. Closest unknown cell from goal
	: The same strategy as _Closest unknown cell from player_ but calculate the distance from the finish goal of the opponent instead of his current position.

# Offers
1. Random cell
	: Offer a random known cell without taking into account any other information.
2. Copy request
	: If the previous negotiation failed, offer the requested cell. Otherwise offer a random cell.
3. Full determined
	: Select a known cell and offer it until it is accepted (even if multiple negotiation sessions are required).
4. Semi determined
	: Select a known cell and offer it until it is accepted or the current negotiation session ends.
5. Closest unknown cell from player
	: Offer the closest known cell to the opponent's position (the same principles with "rings" - **1-step-away**, then **2-step-away** etc.).
6. Closest unknown cell from goal
	: The same strategy as _Closest unknown cell from player_ but calculates the distance from the finish goal of the opponent instead of his current position.
7. Furthest unknown cell from player
	: Offer the furthest known cell to the opponent's position (the same principles with "rings" - **10-step-away**, then **9-step-away** etc.).
8. Furthest unknown cell from goal
	: The same strategy as _furthest unknown cell from player_ but calculates the distance from the finish goal of the opponent instead of his current position.

## Important remarks
* If a player knows the full layout of a maze, it will **not** accept any new negotiation attempts.
* The score of a player represents the total **energy** used over the whole game:
	* For a simple move to a known cell, it will take 1 unit of energy.
	* Negotiation will take 2 units of energy per attempt (each session consists of 3 maximum attempts each).
	* Moving into an unknown cell as a valid move will consume 1 unit of energy.
	* Moving into an unknown cell as an invalid move will consume 3 units of energy, but will mark that cell as discovered.
* A player cannot offer an unknown cell, nor can it request an already known cell.
* A player cannot accept an offered known cell.
* A player cannot predict or know what strategy the other player is using.
* ~~A player will receive 6 units of energy at the start of each round. Unused energy will not carry over to the next round.~~
* Both players will know from the start where the finish point is located.
* At the moment, both players will always want to negociate.