from both import GameMaster
from strategies import Human

game = GameMaster(seed=None)
# game.playerA.set_strategy([_ for _ in "0011001111000000100111"])
game.playerA.set_strategy(strategy=None)
game.playerB.set_strategy(strategy=None)

game.run(rounds=100, training=True)
print(f"Final score for A: {game.playerA.score}")
print(f"Final score for B: {game.playerB.score}")