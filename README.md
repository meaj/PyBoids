# PyBoids

### Description
PyBoids is a [software toy](https://en.wikipedia.org/wiki/Toy_program "The heck is that?") that attempts to demonstrate flocking behavior, heavily inspired by Craig Reynolds' [simulation](https://www.red3d.com/cwr/boids/ "Mr. Reynold's boids").
The goal of this project is to produce flocking simulations with A.I. algorithms such as the genetic algorithm and NEAT.
These simulations will then be compared to my implementation of the model devised by Mr. Reynolds.
This is a highly experimental project and contents may change suddenly.

### Prerequisites
* **pygame**: Used for displaying the simulation


### Roadmap
0. Cleanup code and adopt best practices when possible
1. ~~Build engine to display and move boids and determine what is a flock~~
2. ~~Build monitoring system to display data about each flock~~
3. Implement Mr. Reynolds' version of boids using PyBoids engine
<ol start = 4>
    <li> Build wrapping needed to record generations of AI models and display Neural Networks and other data</li>
    <ol start = i>
        <li>Build system to allow each generation to be tested on the same permutation of random values</li>
        <li>Build system for N.N. based models that will show the nodes as they activate</li>
    </ol>
    <li>Train AI models to produce simulations</li>
</ol>



### Contents
* **PyBoids.py**: The driver for this project
* **GameManager.py**: This controls the display of all the boids as well as the other managers and simulation objects.
* **FlockManager.py**: This controls the collections of boid objects
* **Entities.py**: This is the class that boid objects are instantiated from
* **Goal.py**: This is the class that goal objects are instantiated from
* **LICENSE**: This is the license for the project

### License
This project is licensed under the MIT License