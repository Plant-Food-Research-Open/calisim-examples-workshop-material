import mesa_geo as mg
from shapely.geometry import Point
import pandas as pd
from pathlib import Path
import networkx as nx
from copy import deepcopy
import mesa
import mesa_geo as mg
from shapely.geometry import Point

class PersonAgent(mg.GeoAgent):
    """Person Agent."""

    def __init__(
        self,
        model,
        geometry,
        crs,
        agent_type="susceptible",
        mobility_range=100,
        recovery_rate=0.2,
        death_risk=0.1,
        init_infected=0.1,
    ):
        """Create a new person agent.
        :param model:       Model in which the agent runs
        :param geometry:    Shape object for the agent
        :param agent_type:  Indicator if agent is infected
                            ("infected", "susceptible", "recovered" or "dead")
        :param mobility_range:  Range of distance to move in one step
        """
        super().__init__(model, geometry, crs)
        # Agent parameters
        self.atype = agent_type
        self.mobility_range = mobility_range
        self.recovery_rate = recovery_rate
        self.death_risk = death_risk
        self.induced_infections_at_t = 0
        self.infected_others_at_t = False
        self.total_infected_others = 0

        self.node_id = -1
        self.neighbourhood = None

        # Random choose if infected
        if self.random.random() < init_infected:
            self.atype = "infected"
            self.model.counts["infected"] += 1  # Adjust initial counts
            self.model.counts["susceptible"] -= 1

    def move_point(self, dx, dy):
        """Move a point by creating a new one
        :param dx:  Distance to move in x-axis
        :param dy:  Distance to move in y-axis
        """
        return Point(self.geometry.x + dx, self.geometry.y + dy)

    def step(self):
        """Advance one step."""
        self.infected_others_at_t = False
        self.induced_infections_at_t = 0

        # If susceptible, check if exposed
        if self.atype == "susceptible":
            neighbors = self.model.space.get_neighbors_within_distance(
                self, self.model.exposure_distance
            )
            for neighbor in neighbors:
                if not isinstance(neighbor, PersonAgent):
                    continue
                if self.node_id == neighbor.node_id:
                    continue

                if self.model.network_grid_type == "person":
                    from_id = self.node_id
                    to_id = neighbor.node_id
                    from_obj = self
                    to_obj = neighbor

                elif self.model.network_grid_type == "neighbourhood":
                    from_id = self.neighbourhood.node_id
                    to_id = neighbor.neighbourhood.node_id
                    from_obj = self.neighbourhood
                    to_obj = neighbor.neighbourhood

                self.model.network_grid.G.add_edge(
                    from_id,
                    to_id,
                    agent_type=self.model.network_grid_type,
                    from_state=from_obj.atype,
                    to_state=to_obj.atype,
                    contact_type="contacted"
                )

                self.infected_others_at_t = True
                self.induced_infections_at_t += 1
                self.total_infected_others += 1

                self.model.network_grid.G[from_id][to_id].update(
                    {
                        "contact_type": "infected",
                        "to_state": to_obj.atype
                    }
                )

                if (
                    neighbor.atype == "infected"
                    and self.random.random() < self.model.infection_risk
                ):
                    self.atype = "infected"
                    break

        # If infected, check if it recovers or if it dies
        elif self.atype == "infected":
            if self.random.random() < self.recovery_rate:
                self.atype = "recovered"
            elif self.random.random() < self.death_risk:
                self.atype = "dead"

        # If not dead, move
        if self.atype != "dead":
            move_x = self.random.randint(-self.mobility_range, self.mobility_range)
            move_y = self.random.randint(-self.mobility_range, self.mobility_range)
            self.geometry = self.move_point(move_x, move_y)  # Reassign geometry

        self.model.counts[self.atype] += 1  # Count agent type

    def __repr__(self):
        return "Person " + str(self.unique_id)


class NeighbourhoodAgent(mg.GeoAgent):
    """Neighbourhood agent. Changes color according to number of infected inside it."""

    def __init__(self, model, geometry, crs, agent_type="safe", hotspot_threshold=1):
        """Create a new Neighbourhood agent.
        :param unique_id:   Unique identifier for the agent
        :param model:       Model in which the agent runs
        :param geometry:    Shape object for the agent
        :param agent_type:  Indicator if agent is infected
                            ("infected", "susceptible", "recovered" or "dead")
        :param hotspot_threshold:   Number of infected agents in region
                                    to be considered a hot-spot
        """
        super().__init__(model, geometry, crs)
        self.atype = agent_type

        self.node_id = -1

        self.infected_at_t = 0
        self.total_infected = 0

        self.people_at_t = 0
        self.total_visitors = 0
        self.reset_counts()

        self.hotspot_threshold = (
            hotspot_threshold  # When a neighborhood is considered a hot-spot
        )
        self.color_hotspot()

    def reset_counts(self):
        self.counts = {
            "susceptible": 0,
            "infected": 0,
            "recovered": 0,
            "dead": 0,
        }

    def update_person_neighbour(self):
        self.reset_counts()

        neighbors = self.model.space.get_intersecting_agents(self)

        persons = [
            neighbor
            for neighbor in neighbors
            if isinstance(neighbor, PersonAgent)
        ]
        for person in persons:
            person.neighbourhood = self

            self.counts[person.atype] += 1

    def step(self):
        """Advance agent one step."""
        self.infected_at_t = 0
        self.people_at_t = 0

        self.color_hotspot()
        self.model.counts[self.atype] += 1  # Count agent type

    def color_hotspot(self):
        # Decide if this region agent is a hot-spot
        # (if more than threshold person agents are infected)
        neighbors = self.model.space.get_intersecting_agents(self)

        persons  = [
            neighbor for neighbor in neighbors if isinstance(neighbor, PersonAgent)
        ]

        infected_neighbors = [
            person for person in persons if person.atype == "infected"
        ]
        self.people_at_t = len(persons)
        self.total_visitors += self.people_at_t

        self.infected_at_t = len(infected_neighbors)
        self.total_infected += self.infected_at_t

        if len(infected_neighbors) >= self.hotspot_threshold:
            self.atype = "hotspot"
        else:
            self.atype = "safe"

    def __repr__(self):
        return "Neighborhood " + str(self.unique_id)

class GeoSir(mesa.Model):
    """Model class for a simplistic infection model."""

    # Geographical parameters for desired map
    geojson_regions = str(Path("data", "TorontoNeighbourhoods.geojson"))
    unique_id = "HOODNUM"

    def __init__(
        self, pop_size=1000, init_infected=0.2, exposure_distance=100, infection_risk=0.3,
        network_grid_type = 1
    ):
        """Create a new InfectedModel
        :param pop_size:        Size of population
        :param init_infected:   Probability of a person agent to start as infected
        :param exposure_distance:   Proximity distance between agents
                                    to be exposed to each other
        :param infection_risk:      Probability of agent to become infected,
                                    if it has been exposed to another infected
        """
        super().__init__()
        self.space = mg.GeoSpace(warn_crs_conversion=False)
        self.networks = []
        self.states = []
        self.network_grid = None
        network_grid_types=[
            "person",
            "neighbourhood"
        ]
        self.network_grid_type = network_grid_types[round(network_grid_type)]

        self.steps = 0
        self.counts = None
        self.reset_counts()

        # SIR model parameters
        self.pop_size = pop_size
        self.counts["susceptible"] = pop_size
        self.exposure_distance = exposure_distance
        self.infection_risk = infection_risk

        self.running = True
        self.datacollector = mesa.DataCollector(
            {
                "infected": get_infected_count,
                "susceptible": get_susceptible_count,
                "recovered": get_recovered_count,
                "dead": get_dead_count,
            }
        )

        # Set up the Neighbourhood patches for every region in file
        ac = mg.AgentCreator(NeighbourhoodAgent, model=self)
        neighbourhood_agents = ac.from_file(self.geojson_regions)
        self.space.add_agents(neighbourhood_agents)

        # Generate PersonAgent population
        ac_population = mg.AgentCreator(
            PersonAgent,
            model=self,
            crs=self.space.crs,
            agent_kwargs={"init_infected": init_infected},
        )
        # Generate random location and add agent to grid
        for _ in range(pop_size):
            this_neighbourhood = self.random.randint(
                0, len(neighbourhood_agents) - 1
            )  # Region where agent starts
            center_x, center_y = neighbourhood_agents[
                this_neighbourhood
            ].geometry.centroid.coords.xy
            this_bounds = neighbourhood_agents[this_neighbourhood].geometry.bounds
            spread_x = int(
                this_bounds[2] - this_bounds[0]
            )  # Heuristic for agent spread in region
            spread_y = int(this_bounds[3] - this_bounds[1])
            this_x = center_x[0] + self.random.randint(0, spread_x) - spread_x / 2
            this_y = center_y[0] + self.random.randint(0, spread_y) - spread_y / 2
            this_person = ac_population.create_agent(Point(this_x, this_y))
            self.space.add_agents(this_person)
            this_person.neighbourhood = neighbourhood_agents[this_neighbourhood]

        for agent_type in [PersonAgent, NeighbourhoodAgent]:
            for node_id, agent in enumerate(self.agents_by_type[agent_type]):
                agent.node_id = node_id

        self.datacollector.collect(self)

    def add_network(self, agent_type):
        G=nx.Graph()
        self.networks.append(G)

        if self.network_grid is None:
            self.network_grid = mesa.space.NetworkGrid(G)
            for node_id, agent in enumerate(self.agents_by_type[agent_type]):
                agent.node_id = node_id
        else:
            self.network_grid.G = G

        for agent in self.agents_by_type[agent_type]:
            node_id = agent.node_id
            G.add_node(node_id)
            G.nodes[node_id]["agent"] = self.network_grid.default_val()
            agent.pos = None
            self.network_grid.place_agent(agent, node_id)

    def reset_counts(self):
        self.counts = {
            "susceptible": 0,
            "infected": 0,
            "recovered": 0,
            "dead": 0,
            "safe": 0,
            "hotspot": 0,
        }

    def step(self):
        """Run one step of the model."""
        self.reset_counts()

        if self.network_grid_type == "person":
            self.add_network(PersonAgent)
        elif self.network_grid_type == "neighbourhood":
            self.add_network(NeighbourhoodAgent)

        self.agents_by_type[NeighbourhoodAgent].do("update_person_neighbour")
        # Activate PersonAgents in random order
        self.agents_by_type[PersonAgent].shuffle_do("step")
        # For NeighbourhoodAgents the order doesn't matter, since they update independently from each other
        self.agents_by_type[NeighbourhoodAgent].do("step")

        self.datacollector.collect(self)

        # Run until no one is infected
        # if self.counts["infected"] == 0:
        #     self.running = False

        state = self.get_state()
        self.states.append(state)

    def run(self, n_steps) -> None:
        for _ in range(n_steps):
            self.step()

    def get_state(self) -> dict:
        state = deepcopy(self.counts)
        state["t"] = self.steps
        return state

    def get_states(self):
        return self.states

    def get_states_df(self):
        return pd.DataFrame(self.states)

    def get_networks(self):
        return self.networks

    def get_node_df(self):
        rows = []
        for i, G in enumerate(self.networks):
            for node_id in G.nodes:
                node = G.nodes[node_id]
                row = {}
                rows.append(row)
                row["t"] = i + 1

                agent = node["agent"][0]
                row["node_id"] = agent.node_id
                row["state"] = agent.atype
                if self.network_grid_type == "person":
                    row["induced_infections_at_t"] = agent.induced_infections_at_t
                    row["total_infected_others"] = agent.total_infected_others
                    row["x"] = agent.geometry.x
                    row["y"] = agent.geometry.y
                elif self.network_grid_type == "neighbourhood":
                    row["infected_at_t"] = agent.infected_at_t
                    row["total_infected"] = agent.total_infected
                    row["people_at_t"] = agent.people_at_t
                    row["total_people"] = agent.total_visitors
                    x, y =  agent.geometry.centroid.coords.xy
                    row["x"], row["y"] = x[0], y[0]

        df = pd.DataFrame(rows)
        return df

    def get_edge_df(self):
        rows = []
        for i, G in enumerate(self.networks):
            for edge_id in G.edges:
                row = {}
                rows.append(row)
                row["t"] = i + 1

                row["from"], row["to"] = edge_id
                edge = G.edges[edge_id]
                row["agent_type"] = edge["agent_type"]
                row["from_state"] = edge["from_state"]
                row["to_state"] = edge["to_state"]
                row["contact_type"] = edge["contact_type"]

        df = pd.DataFrame(rows)
        return df

# Functions needed for datacollector
def get_infected_count(model):
    return model.counts["infected"]


def get_susceptible_count(model):
    return model.counts["susceptible"]


def get_recovered_count(model):
    return model.counts["recovered"]


def get_dead_count(model):
    return model.counts["dead"]


model = GeoSir()

for t in range(10):
    model.run(1)

node_df = model.get_node_df()
edge_df = model.get_edge_df()
print(node_df)
print(edge_df)
