# Made by Kiwi! 

import mesa
import random

class HumanAgent(mesa.Agent):
    """
    Class Representing a Human Agent in a society
    """

    def __init__(self, unique_id, model, agent_type):
        """
        Create a new human agent.

        Args:
           unique_id: Unique identifier for the agent.
           x, y: Agent initial location.
           agent_type: Indicator for the agent's type (trusting, semi-trusting, untrusting)
        """
        super().__init__(unique_id, model)
        self.type = agent_type

        # Metrics

        # How much do the humans trust their neighbors
        self.information = 0
        # Confidence is how confident the agent is in their own beliefs
        self.confidence = .5 

        # TODO: Implement functionality to allow for this info 
        # f3.write("type, threshold, startingType, finalType, flipCount, avgFlipTime, numMisinformedNeighbors, numInformedNeighbors, avgAgentsInNeighborhood, numAgentsFlipped\n")
        self.misinformed = False
        # Prevalence estimates vary in this and other sources, 
        # but the proportion who are influenced into sharing false material because they think it is 
        # true might be around 10%.
        # https://crestresearch.ac.uk/resources/disinformation-on-social-media/
        randn = random.random()
        if randn < 0.1:
            self.output = -1
            self.misinformed = True
        else:
            self.output = 1
        self.LLMThatFlipped = None
        self.flipHistory = []
        self.flipCount = 0
        self.justFlipped = False
        self.stepsSinceFlip = 0
        

        self.numNeigborsFlipped = 0
        self.totalNumMoves = 0
        self.happy = True

        self.lastMoveWasRandom = False

        self.numMaliciousLLMNeighbors = 0
        self.numBenignLLMNeighbors = 0
        self.numTrustingHumanNeighbors = 0
        self.numUntrustingHumanNeighbors = 0
        self.numSemiTrustingHumanNeighbors = 0

        # How likely is the agent to trust LLMs
        self.LLMtrustCoefficient = 0
        # https://www.pewresearch.org/short-reads/2024/10/16/republicans-young-adults-now-nearly-as-likely-to-trust-info-from-social-media-as-from-national-news-outlets/
        self.HumanTrustCoefficient = .4
        # 0 is uncaring, 1 is satisfied, -1 is unsatisfied
        # This tells us how much a humanagent trusts LLMs. Humans are trusted to be confidence * .5  
        # LLMs are trusted to be confidence * trustCoefficient
        if agent_type == 'trusting':
            # Generate a random trust value between 0.67 and 1
            self.LLMtrustCoefficient = random.uniform(0.67, 1)
        elif agent_type == 'semi-trusting':
            # Generate a random trust value between 0.34 and 0.66
            self.LLMtrustCoefficient = random.uniform(0.34, 0.66)
        elif agent_type == 'untrusting':
            # Generate a random trust value between 0.01 and 0.33
            self.LLMtrustCoefficient = random.uniform(0.01, 0.33)
        # neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=self.model.radius)

    def step(self):
        shouldMove = False
        LLMInNeighorhood = False
        # Get the neighbors of the agent, radius is the neighborhood to be considered
        # Change radius to different values to see how it affects the model
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=self.model.radius)
        # If the agent is trusting, they will up their trust coefficient if they have a human or LLM neighbor
        numLLMNeighbors = 0
        numHumanNeighbors = 0
        for neighbor in neighbors:
            if isinstance(neighbor, LLMAgent):
                numLLMNeighbors += 1
            else:
                numHumanNeighbors += 1

        # proportionLLMs=0.05,
        # maliciousLLMs=0.5,
        if (numLLMNeighbors + numHumanNeighbors != 0) and numLLMNeighbors / (numLLMNeighbors + numHumanNeighbors) > ((self.model.maliciousLLMs / 10) + self.model.proportionLLMs):
            LLMInNeighorhood = True

        if self.type == 'trusting':
            if not LLMInNeighorhood:
                shouldMove = True
                self.happy = False
        elif self.type == 'untrusting':
            if LLMInNeighorhood:
                shouldMove = True
                self.happy = False
        
        if shouldMove:
            # Trusting Agents will move to a space around an LLM agent. If no spaces are available, they will move to a random space
            moved = False
            # If the agent has moved more than 10 times and the last move was not random, move to a random empty space
            # This simulates a human agent leaving the area
            if self.totalNumMoves > 10 and not self.lastMoveWasRandom:
                # Move to a random empty space
                self.model.grid.move_to_empty(self)
                self.lastMoveWasRandom = True
            
            self.lastMoveWasRandom = False
            if self.type == 'trusting':
                # Move to a space around an LLM agent close to them
                for i in range(1, self.model.InconvenienceThreshold):
                    # Get the neighbors of the agent
                    radiusNeighborhood = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False, radius=i)
                    # Iterate through all empty spaces around the agent
                    # If an LLM exists in the neighborhood of that empty space, move to that space
                    # Otherwise, stay
                    emptySpaces = []
                    for cell in radiusNeighborhood:
                        if self.model.grid.is_cell_empty(cell) is True:
                            emptySpaces.append(cell)
                        
                    for space in emptySpaces:
                        neighbors = self.model.grid.get_neighbors(space, moore=True, include_center=False, radius=self.model.radius)
                        for neighbor in neighbors:
                            if isinstance(neighbor, LLMAgent):
                                self.model.grid.move_agent(self, space)
                                self.model.totalNumMoves += 1
                                self.totalNumMoves += 1
                                moved = True
                                self.happy = True
                            if moved:
                                break
                        if moved:
                            break
                    if moved:
                        break 
            elif self.type == 'untrusting':
                # Move away from an LLM agent close to them
                for i in range(1, self.model.InconvenienceThreshold):
                    if moved:
                        break
                    # Get the neighbors of the agent
                    radiusNeighborhood = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False, radius=i)
                    # Iterate through all empty spaces around the agent
                    # If an LLM exists in the neighborhood of that empty space, move to that space
                    # Otherwise, stay
                    emptySpaces = []
                    for cell in radiusNeighborhood:
                        if self.model.grid.is_cell_empty(cell) is True:
                            emptySpaces.append(cell)
                    
                    for space in emptySpaces:
                        neighbors = self.model.grid.get_neighbors(space, moore=True, include_center=False, radius=self.model.radius)
                        for neighbor in neighbors:
                            if isinstance(neighbor, LLMAgent):
                                continue 
                            else:
                                self.model.grid.move_agent(self, space)
                                self.model.totalNumMoves += 1
                                self.totalNumMoves += 1
                                moved = True
                                self.happy = True
                            if moved:
                                break
                        if moved:
                            break
                    if moved:
                        break

        # We will get the moore neighborhood
        # Humans will be trusted to be output * confidence * .5 
        # Human confidence is between 0 and 1 
        # LLM confidence is 1
        # LLMs will be trusted to be output * confidence * trustCoefficient
        # Output is 1 if informed, -1 if misinformed
        # self.information is the average trust of the agent towards its neighbors
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=self.model.radius)
        set_informed_or_not(self, neighbors)

        # TODO: Maybe have this variable based on confidence
        if self.information > self.model.resistance * 3:
            self.information = self.model.resistance
        elif self.information < -self.model.resistance * 3:
            self.information = -self.model.resistance

        if self.information > 0:
            self.output = 1
            self.misinformed = False
        elif self.information < 0:
            self.output = -1
            self.misinformed = True
        else:
            self.output = 0
            self.misinformed = False

        # Confidence Math

        # If an agent is recently flipped, confidence will be .5
        if self.justFlipped == True:
            self.stepsSinceFlip = 0
            self.confidence = .3
        else:
            self.stepsSinceFlip += 1

        # Check the neighbors of the agent
        # If more than .75 are the same type, increment confidence by .1
        # Otherwise, decrement confidence by .1
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=self.model.radius)

        numSameType = 0
        for neighbor in neighbors:
            if neighbor.output == self.output:
                numSameType += 1

        if len(neighbors) == 0:
            # Isolated members of society will have their confidence decrease
            self.confidence -= .1 if self.confidence > 0 else 0
        elif numSameType / len(neighbors) > .70:
            self.confidence += .1
        else:
            self.confidence -= .1

        if self.confidence > 1:
            self.confidence = 1
        elif self.confidence < 0:
            self.confidence = 0

        self.numMaliciousLLMNeighbors = 0
        self.numBenignLLMNeighbors = 0
        self.numTrustingHumanNeighbors = 0
        self.numUntrustingHumanNeighbors = 0
        self.numSemiTrustingHumanNeighbors = 0
        for neighbor in neighbors:
            if isinstance(neighbor, LLMAgent):
                if neighbor.type == 'malicious':
                    self.numMaliciousLLMNeighbors += 1
                else:
                    self.numBenignLLMNeighbors += 1
            else:
                if neighbor.type == 'trusting':
                    self.numTrustingHumanNeighbors += 1
                elif neighbor.type == 'untrusting':
                    self.numUntrustingHumanNeighbors += 1
                else:
                    self.numSemiTrustingHumanNeighbors += 1

def set_informed_or_not(self, neighbors):
        # Humans will be trusted to be output * confidence * .5 
        # Human confidence is between 0 and 1 
        # LLM confidence is 1
        # LLMs will be trusted to be output * confidence * trustCoefficient
        # Output is 1 if informed, -1 if misinformed
        # self.information is the average trust of the agent towards its neighbors
        oldInformation = self.information
        self.information = 0
        # Pick three random neighbors
        random.shuffle(neighbors)
        influencers = []
        i = 0
        for neighbor in neighbors:   
            if i > 3:
                break
            if isinstance(neighbor, LLMAgent):
                self.information += neighbor.output * (neighbor.confidence + self.LLMtrustCoefficient)
            else:
                self.information += neighbor.output * (neighbor.confidence + self.HumanTrustCoefficient)
            influencers.append(neighbor)
            i += 1
        
        # If the agent was not misinformed and is now misinformed, or vice versa, increment the flip count
        if (self.information > 0 and oldInformation < 0) or (self.information < 0 and oldInformation > 0):
            self.justFlipped = True
            self.flipCount += 1
            # Loop through the influencers and increment their numNeigborsFlipped count
            for influencer in influencers:
                if isinstance(influencer, LLMAgent):
                    influencer.flipped += 1

                    self.LLMThatFlipped = influencer.type
                    self.flipHistory.append({'LLMThatFlipped:': self.LLMThatFlipped, 'flipCount:': self.flipCount}) 
                else: # Human Influencer
                    influencer.numNeigborsFlipped += 1

                    if influencer.LLMThatFlipped != None:
                        self.LLMThatFlipped = influencer.LLMThatFlipped
                        self.flipHistory.append({'LLMThatFlipped:': influencer.LLMThatFlipped, 'flipCount:': self.flipCount}) 

class LLMAgent(mesa.Agent):
    """
    Class Representing an LLM Agent in a society
    """

    def __init__(self, unique_id, model, agent_type):
        """
        Create a new LLM agent.

        Args:
           unique_id: Unique identifier for the agent.
           x, y: Agent initial location.
           agent_type: Indicator for the agent's type, whether it is a malicious or benign LLM agent
        """
        super().__init__(unique_id, model)
        self.type = agent_type
        self.flipped = 0
        self.confidence = 1
        # Metrics

        if self.type == 'benign':
            self.output = 1
        elif self.type == 'malicious':
            self.output = -1

    def step(self):
        pass

class Simulation(mesa.Model):
    """
    Simulation Model for a community with Human Agents and LLM Agents
    """

    def __init__(
        self,
        height=20,
        width=20,
        trustingHumans=0.5,
        untrustingHumans=0.5,
        proportionLLMs=0.05,
        maliciousLLMs=0.5,
        radius=1,
        inconvenienceThreshold=1,
        resistance=0.5,
        density=0.8,
        maxIterations=100,
        seed=None,
    ):
        """
        Create a new Simulation model.

        Args:
            width, height: Size of the space.

            trustingHumans: Percentage of trusting humans in the community
            untrustingHumans: Percentage of untrusting humans in the community

            proportionLLMs: Proportion of LLMs in the community
            maliciousLLMs: Percentage of malicious LLMs in the community, the rest are benign

            radius: How far the agent will obtain information from
            inconvenienceThreshold: The higher the threshold, the farther the agent will look to move
            density: Density of the community
            seed: Seed for random number generation
        """

        super().__init__(seed=seed)
        self.height = height
        self.width = width

        self.informationingHumans = trustingHumans
        self.untrustingHumans = untrustingHumans
        self.maxIterations = maxIterations

        self.proportionLLMs = proportionLLMs
        self.maliciousLLMs = maliciousLLMs

        self.radius = radius
        self.InconvenienceThreshold = inconvenienceThreshold
        self.density = density

        self.iterations = 0
        self.totalNumMoves = 0

        self.totalMaliciousLLMs = 0
        self.totalBenignLLMs = 0
        
        self.totalTrustingHumans = 0
        self.totalUntrustingHumans = 0
        self.totalSemiTrustingHumans = 0

        self.numHumans = 0
        self.numLLMs = 0
        self.numAgents = 0
        self.totalMisinformedHumans = 0
        self.resistance = resistance

        self.schedule = mesa.time.RandomActivation(self)
        self.grid = mesa.space.SingleGrid(width, height, torus=True)

        self.happy = 0
        self.datacollector = mesa.DataCollector(
            model_reporters = {
                                "maliciousLLMs": "totalMaliciousLLMs",
                                "benignLLMs": "totalBenignLLMs",
                                "trustingHumans": "totalTrustingHumans",
                                "untrustingHumans": "totalUntrustingHumans",
                                "semiTrustingHumans": "totalSemiTrustingHumans",
                                "totalMisinformedHumans": "totalMisinformedHumans",
                                "numAgents": "numAgents",
                            },  
        )

        # Set up agents
        # We use a grid iterator that returns the coordinates of a cell as well as its contents. (coord_iter)
        for _, pos in self.grid.coord_iter():
            # Create a new agent
            # Generate a random value
            val = self.random.random()
            # Population size checker
            if val < self.density:
                if val < self.proportionLLMs:
                    agentType = generate_LLM_agent_type(self.maliciousLLMs)
                    self.numLLMs += 1
                    self.numAgents += 1
                    if agentType == 'malicious':
                        self.totalMaliciousLLMs += 1
                    else:
                        self.totalBenignLLMs += 1

                    agent = LLMAgent(self.next_id(), self, agentType)
                else: 
                    agentType = generate_human_agent_type(self.informationingHumans, self.untrustingHumans)
                    self.numHumans += 1
                    self.numAgents += 1
                    if agentType == 'trusting':
                        self.totalTrustingHumans += 1
                    elif agentType == 'untrusting':
                        self.totalUntrustingHumans += 1
                    else:
                        self.totalSemiTrustingHumans += 1
                    agent = HumanAgent(self.next_id(), self, agentType)

                self.grid.place_agent(agent, pos)
                self.schedule.add(agent)

        self.datacollector.collect(self)

    def step(self):
        """
        Run one step of the model.
        """
        if self.iterations == 0:
            output_data_to_file1(self)

        self.totalMisinformedHumans = 0

        self.iterations += 1

        self.schedule.step()

        # Get the number of agents
        

        # Iterate over all agents and calculate the number of happy agents

        for agent in self.schedule.agents:
            if isinstance(agent, HumanAgent):
                if agent.misinformed == True:
                    self.totalMisinformedHumans += 1

        self.datacollector.collect(self)
        #if self.happy == self.schedule.get_agent_count():
        if self.iterations == self.maxIterations or self.happy == self.numHumans:
            output_data_to_file2(self)
            output_data_to_file3(self)
            self.running = False

def output_data_to_file1(model):
    '''
    Output the data to the CSV file
    '''
    f1 = open("model.csv", "w")

    f1.write("Iterations, numAgents, numTrustingHumans, numUntrustingHumans, numSemiTrustingHumans, numBenignLLMs, numMalicious, radius, inconvenienceThreshold, resistance\n")
    f1.write(str(model.maxIterations) + "," + str(model.numAgents) + "," 
             + str(model.totalTrustingHumans) + "," + str(model.totalUntrustingHumans) + "," 
             + str(model.totalSemiTrustingHumans) + "," + str(model.totalBenignLLMs) + "," 
             + str(model.totalMaliciousLLMs) + "," + str(model.radius) + "," 
             + str(model.InconvenienceThreshold) + "," + str(model.resistance) + "\n")

# f2.write("Type of LLM, Flipped\n")
def output_data_to_file2(model):
    '''
    Output the data to the CSV file
    '''
    f2 = open("LLM.csv", "w")
    f2.write("Type of LLM, Flipped\n")
    for agent in model.schedule.agents:
        if isinstance(agent, LLMAgent):
            f2.write(str(agent.type) + "," + str(agent.flipped) + "\n")

def output_data_to_file3(model):
    '''
    Output the data to the CSV file
    '''
    f3 = open("Human.csv", "w")
    # self.confidence
    # self.LLMThatFlipped
    # self.misinformed
    # self.flipCount
    # self.numNeigborsFlipped
    # self.totalNumMoves
    # self.lastMoveWasRandom
    # self.type
    # self.LLMtrustCoefficient
    f3.write("type, confidence, LLMThatFlipped, misinformed, flipCount, numNeigborsFlipped, totalNumMoves, lastMoveWasRandom, LLMtrustCoefficient\n")
    for agent in model.schedule.agents:
        if isinstance(agent, HumanAgent):
            f3.write(str(agent.type) + "," + str(agent.confidence) + "," + str(agent.LLMThatFlipped) + "," 
                     + str(agent.misinformed) + "," + str(agent.flipCount) + "," + str(agent.numNeigborsFlipped) + "," 
                     + str(agent.totalNumMoves) + "," + str(agent.lastMoveWasRandom) + "," + str(agent.LLMtrustCoefficient) + "\n")
            

def generate_LLM_agent_type(malicious):
    '''
    Generate the LLM agent type based on the environment
    Args:
        malicious: Percentage of malicious LLM agents in the community
    All other LLMs are benign
    '''
    curr = random.random()
    
    if malicious == 0:
        return 'benign'
    elif curr < malicious:
        return 'malicious'
    else:
        return 'benign'

def generate_human_agent_type(trusting, untrusting):
    '''
    Generate the human agent type based on the society
    Args:
        trusting: Percentage of trusting humans in the community
        untrusting: Percentage of untrusting humans in the community
    '''
    curr = random.random()
    
    if curr < trusting:
        return 'trusting'
    elif curr < trusting + untrusting:
        return 'untrusting'
    else:
        return 'semi-trusting'