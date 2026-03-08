import networkx as nx
import math
from typing import List, Dict, Set

from src.pathing.graph_adapter import GraphAdapter
from src.pathing.state import StateModeler
from src.graph.student import StudentManager

class MSMSOptimizer:
    def __init__(self, 
                 graph: nx.DiGraph, 
                 sources: List[str], 
                 sinks: List[str], 
                 mastery: Dict[str, float],
                 lam1: float = 0.5, 
                 lam2: float = 0.3, 
                 lam3: float = 0.2):
        """
        Implementation of the Multi-Source Multi-Sink optimal learning path algorithm.
        lam1, lam2, lam3 are weights for mastery, difficulty, and fanout respectively.
        """
        self.G = graph
        self.sources = set(sources)
        self.sinks = set(sinks)
        self.mastery = mastery
        
        # Hyperparameters
        self.lam1 = lam1
        self.lam2 = lam2
        self.lam3 = lam3
        
        # We need difficulty approximations. In a real system, this is stored on the Concept.
        # We'll approximate this by looking at how many prerequisites a node requires recursively
        # (deeper nodes = higher difficulty).
        self.difficulty = self._compute_recursive_difficulty()

    def _compute_recursive_difficulty(self) -> Dict[str, float]:
        """Approximates difficulty by counting ancestors in the prerequisite DAG."""
        diff = {}
        for node in self.G.nodes():
            # ancestors() counts all indirect prerequisites
            ancestor_count = len(nx.ancestors(self.G, node))
            max_possible = len(self.G.nodes()) - 1
            # Normalize bounded to 0.0 - 1.0 (avoiding div by zero)
            diff[node] = ancestor_count / max_possible if max_possible > 0 else 0.5
        return diff

    def _cost_function(self, u: str, v: str, edge_data: dict) -> float:
        """
        Calculates the traversal cost to learn node 'v' from node 'u'.
        Cost function c(v) = λ1(1 - mastery) + λ2(difficulty) + λ3(fanout)
        """
        m = self.mastery.get(v, 0.0)
        
        # Difficulty penalty
        d = self.difficulty.get(v, 0.5)
        
        # Fanout penalty: out-degree of v. High out-degree means learning this concept
        # unlocks many future concepts, so we actually want to *reward* this (lower penalty).
        # We invert it: (1 - out_degree / max_nodes)
        out_degree = self.G.out_degree(v)
        max_nodes = len(self.G.nodes())
        f = 1.0 - (out_degree / max_nodes)

        # Core cost
        cost = self.lam1 * (1.0 - m) + self.lam2 * d + self.lam3 * f
        
        # Edge weights must be strictly > 0 for Dijkstra
        return max(cost, 0.001)

    def compute_all_shortest_paths(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Runs optimal Dijkstra from every source to every sink.
        Returns paths: dict[source] -> dict[sink] -> [path_nodes]
        """
        paths = {}
        for source in self.sources:
            paths[source] = {}
            for sink in self.sinks:
                try:
                    # networkx dijkstra
                    path = nx.dijkstra_path(self.G, source, sink, weight=self._cost_function)
                    paths[source][sink] = path
                except nx.NetworkXNoPath:
                    # Not all nodes are connected in DAGs
                    pass
        return paths

    def greedy_set_cover(self) -> List[List[str]]:
        """
        Selects the minimal set of optimal paths to cover all sink concepts.
        """
        all_paths = self.compute_all_shortest_paths()
        
        # Flatten paths into a list of tuples: (path_list, covered_sinks_set)
        candidate_paths = []
        for src, dests in all_paths.items():
            for sink, path in dests.items():
                # A path covers all nodes inside it that are sinks
                covered = set(path).intersection(self.sinks)
                
                # Calculate cost of the entire path
                total_cost = 0.0
                for i in range(len(path) - 1):
                    total_cost += self._cost_function(path[i], path[i+1], {})
                    
                candidate_paths.append({
                    "path": path,
                    "covered": covered,
                    "cost": total_cost
                })

        # Greedy selection
        uncovered_sinks = set(self.sinks)
        selected_paths = []
        
        while uncovered_sinks:
            # Find the path that covers the most remaining uncovered sinks, 
            # breaking ties by cheapest cost
            best_candidate = None
            best_coverage = 0
            best_cost = float('inf')
            
            for candidate in candidate_paths:
                coverage_count = len(candidate["covered"].intersection(uncovered_sinks))
                
                if coverage_count > best_coverage:
                    best_coverage = coverage_count
                    best_candidate = candidate
                    best_cost = candidate["cost"]
                elif coverage_count == best_coverage and coverage_count > 0:
                    if candidate["cost"] < best_cost:
                        best_candidate = candidate
                        best_cost = candidate["cost"]

            if not best_candidate:
                # no more sinks can be covered (disconnected components)
                break
                
            selected_paths.append(best_candidate["path"])
            uncovered_sinks -= best_candidate["covered"]

        return selected_paths

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from src.graph.db import Neo4jConnection
    
    load_dotenv()
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    pwd = os.getenv("NEO4J_PASSWORD")

    if uri and user and pwd:
        conn = Neo4jConnection(uri, user, pwd)
        adapter = GraphAdapter(conn)
        G = adapter.get_networkx_graph()
        
        manager = StudentManager(conn)
        modeler = StateModeler(manager)
        
        mastery = manager.get_student_mastery("student_123")
        sources, sinks = modeler.get_sources_and_sinks("student_123", list(G.nodes()))
        
        print(f"\nAlice wants to learn OS. Sources: {sources}. Sinks to cover: {sinks}")
        
        optimizer = MSMSOptimizer(G, sources, sinks, mastery)
        optimal_paths = optimizer.greedy_set_cover()
        
        print("\n=== Optimal MSMS Learning Paths Generated ===")
        if not optimal_paths:
            print("No paths could be found connecting the known sources to the unknown sinks.")
        for idx, path in enumerate(optimal_paths, 1):
            names = [G.nodes[node]['name'] for node in path]
            print(f"Path {idx}: {' -> '.join(names)}")
            
        conn.close()
