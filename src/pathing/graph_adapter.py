import networkx as nx
from src.graph.db import Neo4jConnection

class GraphAdapter:
    def __init__(self, conn: Neo4jConnection):
        self.conn = conn

    def get_networkx_graph(self) -> nx.DiGraph:
        """
        Retrieves all Concepts and IS_PREREQUISITE_FOR relationships
        from Neo4j and builds a directed NetworkX graph.
        """
        G = nx.DiGraph()

        # 1. Fetch all concept nodes
        query_nodes = "MATCH (c:Concept) RETURN c.id AS id, c.name AS name, c.description AS desc"
        nodes = self.conn.query(query_nodes)
        
        for record in nodes:
            # We add nodes with their attributes
            G.add_node(record["id"], name=record["name"], description=record["desc"])

        # 2. Fetch all prerequisite edges
        query_edges = """
        MATCH (source:Concept)-[:IS_PREREQUISITE_FOR]->(target:Concept)
        RETURN source.id AS source_id, target.id AS target_id
        """
        edges = self.conn.query(query_edges)
        
        for record in edges:
            G.add_edge(record["source_id"], record["target_id"])

        print(f"Built NetworkX graph with {G.number_of_nodes()} concepts and {G.number_of_edges()} prerequisites.")
        return G

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    pwd = os.getenv("NEO4J_PASSWORD")

    if uri and user and pwd:
        conn = Neo4jConnection(uri, user, pwd)
        adapter = GraphAdapter(conn)
        
        G = adapter.get_networkx_graph()
        
        # Quick validation
        print("\nGraph Nodes:")
        print(list(G.nodes()))
        print("\nGraph Edges:")
        print(list(G.edges()))
        
        conn.close()
