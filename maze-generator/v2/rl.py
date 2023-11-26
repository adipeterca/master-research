from amazed.modules.maze import Maze
from amazed.modules.build import hunt_and_kill

import numpy as np

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Activation, LeakyReLU
# from keras.layers import Conv2D, MaxPooling2D # will be used in the future

class Memory():
    def __init__(self, size : int):
        self.size = size
        self.data = []
    
    def add(self, episode : tuple):
        # Delete the oldest episode
        if len(self.data) >= self.size:
            del self.data[0]
        
        self.data.append(episode)

    def get(self, episode_count : int) -> tuple:
        '''
        Returns a pair of input/output values for the model to train on.
        '''

        total_count = min(episode_count, len(self.data))
        
        inputs = np.zeros(shape=(total_count, self.data[0][0].shape[1]))
        targets = np.zeros(shape=(total_count, 4))

        memory_sequence = np.random.choice(range(len(self.data)), total_count, replace=False)
        for count in range(total_count):
            memory_index = memory_sequence[count]

            state, action, reward, state_next = self.data[memory_index]

            inputs[count] = state
            targets[count] = model.predict(state)

            # max_a' Q(s', a')
            q_next = np.max(model.predict(state_next))

            # Ar trebui sa las asa sau sa modific asta?
            targets[count][action] = reward + GAMMA * q_next
        
        return inputs, targets


def create() -> Sequential:

    model = Sequential()
    model.add(Dense(128, input_shape=(4096+2,)))
    model.add(LeakyReLU())
    model.add(Dense(64))
    model.add(LeakyReLU())
    model.add(Dense(32))
    model.add(LeakyReLU())
    model.add(Dense(16))
    model.add(LeakyReLU())
    model.add(Dense(4))

    model.compile(optimizer='adam', loss='mse', metrics=['accuracy'])

    return model

maze = Maze(64, 64)
hunt_and_kill(maze)

end = (maze.rows-1, maze.columns-1)

model = create()

GAMES = 100
MAX_STEPS = 1_000_000
EXPLORATION_CHANCE = 0.25   # epsilon
GAMMA = 0.9
LEARNING_RATE = 0.5

memory = Memory(10_000)
step = 0

maze_array = maze.array()

state = np.zeros((1, maze.rows * maze.columns + 2))
state[0, 0:4096] = maze_array

state_next = np.zeros((1, maze.rows * maze.columns + 2))
state_next[0, 0:4096] = maze_array


for game in range(GAMES):
    print(f"[INFO] Currently at game iteration {game}")

    game_over = False
    visited_cells = []
    current_position = (0, 0)

    while not game_over:
        step += 1
        visited_cells.append(current_position)
        action_list = maze.possible_actions(current_position[0], current_position[1])

        if action_list is None:
            game_over = True
            break

        # First method: just bind all values togheter and hope for the best!
        state[0, -2] = current_position[0]
        state[0, -1] = current_position[1]


        # # Second method: embed the position in the given array
        # # However, things could get messy once I normalize the inputs.
        # state = maze.array()
        # state[current_position[0] * maze.rows + current_position[1]] += 100

        # Third method:
        # modify the cells as "visited" (by making them negative) and "unvisited" (by making them positive).

        # Forth method:
        # second + third method combined.

        # Add plus one because, for some unknown reason, I've set the default value for NORTH to be 1 instead of 0.
        if np.random.random() < EXPLORATION_CHANCE:
            action = action_list[np.random.randint(0, len(action_list))]
        else:
            action = np.argmax(model.predict(state))
        
        
        print(f"[INFO][e: {game}][s: {step}] Selected action {action}")

        # Apply the action
        (x, y) = current_position
        if action == Maze.NORTH:
            next_position = (x-1, y)
        elif action == Maze.EAST:
            next_position = (x, y+1)
        elif action == Maze.SOUTH:
            next_position = (x+1, y)
        elif action == Maze.WEST:
            next_position = (x, y-1)
        else:
            raise ValueError(f"Incorrect value for action! Provided value: <{action}>")

        reward = None
        # Get the reward
        if next_position == (maze.rows-1, maze.columns-1):
            game_over = True
            reward = 1
        elif next_position in visited_cells:
            reward = -0.3
        elif maze.is_valid_position(next_position[0], next_position[1]):
            reward = -0.05
        else:
            # For future improvement, maybe re-stablize the maze, undo the action, but leave only the reward?
            game_over = True
            reward = -1
        
        state_next[0, -2] = next_position[0]
        state_next[0, -1] = next_position[1]

        memory.add((state, action, reward, state_next))
    
        inputs, targets = memory.get(1000)
        model.fit(inputs, targets, epochs=8, batch_size=16, verbose=0)
        # loss = model.evaluate(inputs, targets)

model.save("tmp/rl_model.h5")

