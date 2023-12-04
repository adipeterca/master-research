from amazed.modules.maze import Maze
from amazed.modules.build import hunt_and_kill

import numpy as np
import time

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Activation, LeakyReLU
import keras.backend as K
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

    def get(self, model : Sequential, episode_count : int) -> tuple:
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
            targets[count] = model.predict(state, verbose=0)

            if reward == 1 or reward == -1:
                targets[count][action] = reward
            else:
                # max_a' Q(s', a')
                q_next = np.max(model.predict(state_next, verbose=0))
                targets[count][action] = reward + GAMMA * q_next

            # Inspired by Waterworld
            # train the model for each input/target pair
            # can also add a TNN which will be copied before 'for'
            # to predict q_next
            # model.fit(x=state, y=targets[count].reshape(1, -1), verbose=0)
        
        return inputs, targets


def create() -> Sequential:

    model = Sequential()
    model.add(Dense(128, input_shape=(4096+2,)))
    model.add(LeakyReLU())
    model.add(Dense(64))
    model.add(LeakyReLU())
    model.add(Dense(4))

    model.compile(optimizer='adam', loss='mse', metrics=['accuracy'])

    return model

maze = Maze(64, 64)
hunt_and_kill(maze)
maze.export(output="tmp/rl_maze.png", show=False)

end = (maze.rows-1, maze.columns-1)

model = create()

GAMES = 10
MAX_STEPS = 1_000_000
EXPLORATION_CHANCE_MAX = 0.99   # epsilon
EXPLORATION_CHANCE_MIN = 0.1
GAMMA = 0.9
LEARNING_RATE = 0.5

memory = Memory(10_000)
step = 0

maze_array = maze.array()

state = np.zeros((1, maze.rows * maze.columns + 2))
state[0, 0:4096] = maze_array

state_next = np.zeros((1, maze.rows * maze.columns + 2))
state_next[0, 0:4096] = maze_array

exp_chance = EXPLORATION_CHANCE_MAX

for game in range(GAMES):
    print("\n" * 5)
    print(f"[INFO] Currently at game iteration {game}")

    game_over = None
    visited_cells = []
    x = 0
    y = 0
    loss = []

    total_reward = 0

    while game_over is None:
        step += 1
        if (x, y) not in visited_cells:
            visited_cells.append((x, y))
        action_list = maze.possible_actions(x, y)

        if action_list is None:
            game_over = 'no-more-actions'
            break

        # First method: just bind all values togheter and hope for the best!
        state[0, -2] = x
        state[0, -1] = y


        # # Second method: embed the position in the given array
        # # However, things could get messy once I normalize the inputs.
        # state = maze.array()
        # state[x * maze.rows + y] += 100

        # Third method:
        # modify the cells as "visited" (by making them negative) and "unvisited" (by making them positive).

        # Forth method:
        # second + third method combined.

        # Add plus one because, for some unknown reason, I've set the default value for NORTH to be 1 instead of 0.
        if step < 1000:
            action = action_list[np.random.randint(0, len(action_list))]
        else:
            if np.random.random() < exp_chance:
                exp_chance = max(exp_chance * 0.95, EXPLORATION_CHANCE_MIN)
                action = action_list[np.random.randint(0, len(action_list))]
                print(f"[INFO][e: {game}][s: {step}][{x}, {y}][EXPLORE] Selected action {action}")
            else:
                actions = model.predict(state, verbose=0)
                action = np.argmax(actions)
                print(f"[INFO][e: {game}][s: {step}][{x}, {y}][THINK  ] Selected action {action} out of possible actions {actions}")
        
        # Apply the action
        x_new = x
        y_new = y
        if action == Maze.NORTH:
            x_new = x - 1
        elif action == Maze.EAST:
            y_new = y + 1
        elif action == Maze.SOUTH:
            x_new = x + 1
        elif action == Maze.WEST:
            y_new = y - 1
        else:
            raise ValueError(f"Incorrect value for action! Provided value: <{action}>")

        reward = None
        # Get the reward
        if (x_new, y_new) == (maze.rows-1, maze.columns-1):
            game_over = 'win'
            reward = 1
        elif (x_new, y_new) in visited_cells:
            reward = -0.3
        elif maze.is_valid_position(x_new, y_new):
            
            if maze.is_wall(x, y, x_new, y_new):
                game_over = 'illegal-move'
                reward = -1
            else:
                # [IDEA] add a positive reward which should make the bot make the distance to the end of the maze smaller
                prev_distance = ((x - 63)**2 + (y - 63)**2) ** (0.5)
                next_distance = ((x_new - 63)**2 + (y_new - 63)**2) ** (0.5)
                if prev_distance > next_distance:
                    reward = 0.002
                    # reward = 0.005
                    # reward = 0.01     # Too big
                    # reward = 0.001     # Too small
                else:
                    # reward = -0.05 
                    reward = -0.001
        else:
            # For future improvement, maybe re-stablize the maze, undo the action, but leave only the reward?
            game_over = 'outside-of-maze'
            reward = -1
        
        state_next[0, -2] = x_new
        state_next[0, -1] = y_new

        memory.add((state, action, reward, state_next))
        total_reward += reward

        if step >= 1000:
            
            start_time = time.time()
            inputs, targets = memory.get(model, 200)
            total_time = time.time() - start_time

            model.fit(inputs, targets, epochs=8, batch_size=16, verbose=0)
            print(f"[INFO] Trained for {total_time} s")

            loss.append(model.evaluate(inputs, targets))

        x = x_new
        y = y_new

    print(f"Finished game with \n \
          \tstatus <{game_over}>\n \
          \tin possition [{x}, {y}]\n \
          \twith score <{total_reward}>\n \
          \tand total step count of {len(visited_cells)}\n \
          \tLoss : {loss}\n")
    

model.save("tmp/rl_model.h5")
