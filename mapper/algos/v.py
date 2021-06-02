#todo: make it so the closest node is the goal node
#      verify h(n)
#      Fix start/end if floats or outside area
#      

from typing import Dict

from mapper.core.map import Map
from mapper.core.node import Node
from mapper.core.edge import Edge, DiagonalEdge
from mapper.core.tile import Tile, Quarantine, Vaccine, PlayGround
from mapper.core.pqueue import PriorityQueue
from mapper.algos.base import HeuristicAStar


class RoleVAlgo(HeuristicAStar):
    """

    Implement A* heuristic search for Role V

    """
    def __init__(self, cov_map: Map):
        super().__init__(cov_map)
        self.queue: PriorityQueue = PriorityQueue()
        self.d_map: Dict[str, int] = {}
        self.__create_d_map()

     #!!This assumes end point is well placed
    def __update_start(self):
        if isinstance(self.start_node.col_idx, float) and isinstance(self.start_node.row_idx, float):
            new_row_idx = int(self.start_node.row_idx) + 1
            new_col_idx = int(self.start_node.col_idx)
            self.start_node = self.map.get_node(new_row_idx, new_col_idx)

    
    def __create_d_map(self):
        """ creates distance to goal for each node """
        goal_map = {}
        # collect all goal nodes
        for i, row in enumerate(self.map.get_node_grid()):
            for j, node in enumerate(row):
                if node.borders_tile_of_type(Vaccine):
                    goal_map[node.get_name()] = (i, j)
        
        # calculate euclidian to closest goal node from each node
        for i, row in enumerate(self.map.get_node_grid()):
            for j, node in enumerate(row):
                distances = [
                    (abs(i - y) ** 2 + abs(j - x) ** 2) ** 0.5
                    for node_name, (y, x) in goal_map.items()
                ]
                self.d_map[node.get_name()] = min(distances)

    def search(self):
        self.queue.queue(0, InfoContainer(self.start_node, []))
        success_info = None
        closed_list = []
        while not self.queue.empty():
            node_info = self.queue.dequeue()
            node_info.path.append(node_info.node)
            closed_list.append(node_info.node.get_name())
            if node_info.node.borders_tile_of_type(Vaccine):
                success_info = node_info
                break

            for edge in node_info.node.edges:
                other_node = edge.get_other_node(node_info.node)

                # all paths are allowed
                if(other_node.get_name() in closed_list):
                  continue

                priority = self.__calculate_f(other_node, edge, node_info.cost)
                self.queue.queue(
                    priority,
                    InfoContainer(other_node, node_info.path + [edge], node_info.cost + self.__edge_cost(edge))
                )
        if success_info is None:
            print('\n NO PATH FOUND')
        else:
            nodes = [node.get_name() for node in success_info.path if isinstance(node, Node)]
            print(f'\n PATH FOUND:\n   Path: {" --> ".join(nodes)}\n   Cost: {success_info.cost}')

    def __calculate_f(self, node: Node, edge: Edge, current_cost: float) -> float:
        g_n = current_cost + self.__edge_cost(edge)
        h_n = self.__calculate_h(node)
        return g_n + h_n

    def __edge_cost(self, edge: Edge) -> float:
        if isinstance(edge, DiagonalEdge):
            #list of edges without diagonal

            #############3
            # print("Node ", edge.node_one.name, " to ", edge.node_two.name)
            ############
            node_1_edges = edge.node_one.edges
            node_2_edges = edge.node_two.edges
            for i in node_1_edges:
              if isinstance(i, DiagonalEdge):
                node_1_edges.remove(i)
            
            for i in node_2_edges:
              if isinstance(i, DiagonalEdge):
                node_2_edges.remove(i)

            edge_lst = []
            
            ###########
            # print(edge.node_one.name, " <--> ", edge.node_two.name)
            # print(edge.node_one.name, " edges:", str(len(node_1_edges)))
            # for i in node_1_edges:
            #   print(i.node_one.name, "<--->", i.node_two.name)
            # print(edge.node_two.name, " edges:", str(len(node_2_edges)))
            # for i in node_2_edges:
            #   print(i.node_one.name, "<--->", i.node_two.name)
            ###########
            #list of edges with transitive points

            for edge_1 in node_1_edges:
              for edge_2 in node_2_edges:
                if edge_1.node_one.name == edge_2.node_one.name or edge_1.node_one.name == edge_2.node_two.name or edge_2.node_one.name ==  edge_1.node_two.name or edge_2.node_two.name == edge_1.node_two.name:
                  ###########
                  # print("Point found")
                  ###########
                  result = (self.__edge_cost(edge_1) ** 2 + self.__edge_cost(edge_2) ** 2) ** 0.5
                  ###########
                  # print(result)
                  ###########
                  edge_lst.append(result)

            ###########
            # print("List Size: ", len(edge_lst), "\nMax from list: ", max(edge_lst))
            ###########
            return max(edge_lst)
        elif edge.tile_one is None:
            return self.__tile_cost(edge.tile_two)
        elif edge.tile_two is None:
            return self.__tile_cost(edge.tile_one)
        else:
            return (self.__tile_cost(edge.tile_one) + self.__tile_cost(edge.tile_two)) / 2


    def __tile_cost(self, tile: Tile) -> int:
        if isinstance(tile.tile_type, Vaccine):
            return 0
        elif isinstance(tile.tile_type, PlayGround):
            return 1
        elif isinstance(tile.tile_type, Quarantine):
            return 3
        else:
            return 2

    def __calculate_h(self, node: Node) -> float:
        return self.d_map[node.get_name()]


class InfoContainer:
    """ Helper data class for search """
    def __init__(self, node: Node, path_to: list, cost: int = 0):
        self.node: Node = node
        self.path: list = path_to
        self.cost: int = cost
