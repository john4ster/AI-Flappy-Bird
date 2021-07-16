# AI Flappy Bird
AI learns to play flappy bird using the NEAT algorithm. For this implementation, I gave each neural network 4 input nodes, 2 hidden nodes, and 1 output node. Other parameters I have given to the algorithm can be found in the neat_config file.

Inputs:
* Bird's y position
* Distance between bird's y position and bottom pipe's y position
* Distance between bird's y position and top pipe's y position
* Distance between bird and ground

Outputs:
* The bird jumps, or it doesn't

# About NEAT
The NEAT algorithm is a genetic machine learning algorithm that goes through generations of neural networks. Each individual in a generation is running on its own neural network, and the next generation will take the best networks from the previous generation and mutate them. Over time, this results in the neural networks improving. More information on the NEAT algorithm and neat-python can be found here: https://neat-python.readthedocs.io/en/latest/neat_overview.html

# How to use
Simply navigate to the directory where the file is located on your computer, and run ```python flappy.py```, the program will start, and the command prompt will show information on each generation's fitness.

# Screenshots
![image](https://user-images.githubusercontent.com/54284594/125872170-83678f0e-c432-43ed-b5fd-6ef6e19df5b9.png)

![image](https://user-images.githubusercontent.com/54284594/125873079-cd394d2f-ac52-4b5e-a5e2-60a559f0863f.png)

