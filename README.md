# PyBoids

### Description
PyBoids is a [software toy](https://en.wikipedia.org/wiki/Toy_program "The heck is that?") that attempts to demonstrate flocking behavior, heavily inspired by Craig Reynolds' [simulation](https://www.red3d.com/cwr/boids/ "Mr. Reynold's boids").
The goal of this project is to produce flocking simulations with A.I. algorithms such as the genetic algorithm and NEAT.
These simulations will then be compared to my implementation of the model devised by Mr. Reynolds.
This is a highly experimental project and contents may change suddenly.

### Prerequisites
* **pygame**: Used for displaying the simulation


### Roadmap
<ol start = 0>
	<li> Cleanup code and adopt best practices when possible</li>
	<li><strike>Build engine to display and move boids and determine what is a flock</strike></li>
	<li><strike>Build monitoring system to display data about each flock</strike></li>
	<li><strike>Implement Mr. Reynolds' version of boids using PyBoids engine</strike></li>
    <li> Build wrapping needed to record generations of AI models and display Neural Networks and other data</li>
    <ol start = i>
        <li>Build system to allow each generation to be tested on the same permutation of random values</li>
        <li>Build system for N.N. based models that will show the nodes as they activate</li>
    </ol>
    <li>Train AI models to produce simulations</li>
</ol>



### Contents
* **PyBoids.py**: The driver for this project
* **Entities.py**: This is the class that entities are instantiated from. Entities include boid objects and the goal tokens they search for.
* **DisplayManager.py**: This controls the display of all components of the simulation.
* **FlockManager.py**: This class controls the collections of boids that are able to interact with each other.
* **SimulationManager.py**: This controls the other managers and simulation objects and serves to connect them.
* **Vector2D.py**: This is the class that 2D vectors are instantiated from
* **ReynoldsControl.py**: This contains methods to control boid movement based on those used in Craig Reynold's original simulation
* **LICENSE**: This is the license for the project

### License
This project is licensed under the MIT License