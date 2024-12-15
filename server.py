# Made by Kiwi! 

import mesa
from model import Simulation

def get_misinformed_agents(model):
    """
    Display a text count of how many agents are misinformed.
    """
    return f"Misinformed Humans: {model.totalMisinformedHumans}"

def get_num_malicious(model):
    """
    Display the number of malicious LLM agents.
    """
    return f"Number of Malicious LLM Agents: {model.totalMaliciousLLMs}"

def get_num_benign(model):
    """
    Display the number of benign LLM agents.
    """
    return f"Number of benign LLM Agents: {model.totalBenignLLMs}"

def get_num_trusting(model):
    """
    Display the number of trusting humans.
    """
    return f"Number of Trusting Humans: {model.totalTrustingHumans}"

def get_num_untrusting(model):
    """
    Display the number of untrusting humans.
    """
    return f"Number of Untrusting Humans: {model.totalUntrustingHumans}"

def get_num_semi_trusting(model):
    """
    Display the number of semi-trusting humans.
    """
    return f"Number of Semi-Trusting Humans: {model.totalSemiTrustingHumans}"

def schelling_draw(agent):
    """
    Portrayal Method for canvas
    """
    if agent is None:
        return
    portrayal = {"Shape": "circle", "r": 1, "Filled": "true", "Layer": 0}

    if agent.type == 'trusting':
        portrayal["Color"] = "#0000FF"  # Dark Blue
    elif agent.type == 'semi-trusting':
        portrayal["Color"] = "#808080"  # Gray
    elif agent.type == 'untrusting':
        portrayal["Color"] = "#FF0000"  # Dark Red

    elif agent.type == 'benign':
        portrayal["Color"] = "#00FF00" # Dark Green
    elif agent.type == 'malicious':
        portrayal["Color"] = "#000000" # Black
    
    if agent.output == 1: 
        portrayal["r"] = 0.5

    return portrayal

canvas_element = mesa.visualization.CanvasGrid(
    portrayal_method=schelling_draw,
    grid_width=50,
    grid_height=50,
    canvas_width=800,
    canvas_height=800,
)

model_params = {
    "height": 50,
    "width": 50,
    "density": mesa.visualization.Slider(
        name="Agent density", value=0.8, min_value=0.1, max_value=1.0, step=0.1
    ),
    "trustingHumans": mesa.visualization.Slider(
        name="Proportion of Trusting Humans", value=0.4, min_value=0.00, max_value=1.0, step=0.1
    ),
    "untrustingHumans": mesa.visualization.Slider(
        name="Proportion of Untrusting Humans", value=0.4, min_value=0.00, max_value=1.0, step=0.1
    ),
    "proportionLLMs": mesa.visualization.Slider(
        name="LLM Presence", value=0.05, min_value=0.01, max_value=0.1, step=0.01
    ),
    "maliciousLLMs": mesa.visualization.Slider(
        name="Malicious LLM Agents", value=0.5, min_value=0.0, max_value=1.0, step=0.1
    ),
    "radius": mesa.visualization.Slider(
        name="Search Radius", value=1, min_value=1, max_value=5, step=1
    ),
    "inconvenienceThreshold": mesa.visualization.Slider(
        name="Inconvenience Threshold", value=1, min_value=1, max_value=5, step=1
    ),
    "resistance": mesa.visualization.Slider(
        name="Resistance to Misinformation", value=.5, min_value=.1, max_value=1, step=.1
    ),
    "maxIterations": mesa.visualization.Slider(
        name="Iterations", value=100, min_value=100, max_value=1000, step=100
    ),
}

misinformed_chart = mesa.visualization.ChartModule([{"Label": "totalMisinformedHumans", "Color": "Black"}])

server = mesa.visualization.ModularServer(
    model_cls=Simulation,
    visualization_elements = [
        canvas_element,
        get_misinformed_agents,
        misinformed_chart,
        get_num_malicious,
        get_num_benign,
        get_num_trusting,
        get_num_untrusting,
        get_num_semi_trusting
        ],
    name="Communities with Malicious Agents",
    model_params=model_params,
)