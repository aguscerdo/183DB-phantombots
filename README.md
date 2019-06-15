# PHANTOMBots
On the PHANTOMBots package we provide several tools for Multi-Agent Pursuit Evasion.

### Simulation Environment
On the `environment` directory several tools are available to run simulations under different constraints.
- `env.py` contains the class `Environment` which holds all the functions needed for general simulations. Some noteworthy functions are:
    - `win_condition` returns true if the target robot is on the same  position as a pursuer.
    - `play_round` takes in the actions for all bots and moves them
    - `adjacent` gets all adjacent positions to an XY position
    - `legal_move_pos` checks if given movement is legal (on the grid and no collisions)
    - `animate`makes a video of the current simulation history positions
    - several other functions can be found
- `game.py` contains the class `Game` which runs simulations and returns training samples for ML
    - `get_simulation_history` runs a simulation and returns actions, states and rewards.
- `phantomBot.py` contains the class `PhantomBot` which represents a single bot
    - `move` changes the XY position of the bot
    - `double_move` performs two movements to abstract speed

### Computer Vision
On the `CV` directory the relevant files to run the physical system are present. For setting up robots refer to [Paperbot](https://git.uclalemur.com/mehtank/paperbot).
There are several files which we will not go into detail.
- `config.py` contains configuration info like ip addresses, movement speeds, sleep times, etc.
- `RunProject.py` contains core functions for running the system.
    - `run_system` is the function that initializes everything. The instructions to  simulate are passed here.

For an example on running a system refer to `physicalRun.py` on the main directory.

### Machine Learning
On the `ML` directory we find the machine learning functions and classes.
- `tf_reinforcement.py` contains the ML model used, implemented in TensorFlow.
- `tf_simulator.py` is used to run and train using the file above.

For an example of usage, refer to `learn_simulate.py`.

