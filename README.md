# Misinformation Simulation Model

## Summary

The model.py file contains the implementation of an agent-based simulation model designed to study the spread of misinformation within a community. The model includes both human agents and language model (LLM) agents, which can be either benign or malicious. The simulation tracks how agents interact, move, and influence each other's beliefs over time.

## Details

The simulation is built using the Mesa framework, which facilitates the creation of agent-based models. The key components of the model are:

HumanAgent: Represents a human in the community. Each human agent has attributes such as trust level, confidence, and whether they are misinformed. Human agents can be trusting, semi-trusting, or untrusting towards LLMs.
LLMAgent: Represents a language model agent in the community. LLM agents can be either benign or malicious, influencing human agents based on their type.
Simulation: The main model class that initializes the simulation environment, including the grid, agents, and various parameters such as the proportion of LLMs, the radius of influence, and the density of the community.
Key functionalities include:

Agent Initialization: Agents are placed on a grid with initial attributes based on predefined probabilities.
Agent Interaction: Agents interact with their neighbors, influencing each other's confidence and beliefs. Human agents adjust their trust based on the type and behavior of neighboring agents.
Movement: Trusting human agents move towards LLMs, while untrusting human agents move away from them.
Data Collection: The model collects data on the number of agents, their types, and their states (e.g., misinformed or not) at each step of the simulation.
Output: The simulation outputs data to CSV files, capturing various metrics such as the number of flips in beliefs and the types of agents.

## Installation

To install the dependencies use pip and the requirements.txt in this directory. e.g.

```
    $ pip install -r requirements.txt
```

## How to Run

Directly run the file ``run.py`` in the terminal. e.g.

```
    $ python run.py
```

Then open your browser to [http://127.0.0.1:4545/](http://127.0.0.1:4545/) and press Reset, then Run.

## Files

* ``run.py``: Launches a model visualization server.
* ``model.py``: Contains the agent class, and the overall model class.
* ``server.py``: Defines classes for visualizing the model in the browser via Mesa's modular server, and instantiates a visualization server.

## Further Reading

