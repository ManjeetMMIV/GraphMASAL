import networkx as nx
from src.graph.db import Neo4jConnection

class GraphAdapter:
    def __init__(self, conn: Neo4jConnection):
        self.conn = conn

    def get_networkx_graph(self, student_id: str = None) -> nx.DiGraph:
        """
        Retrieves Concepts and IS_PREREQUISITE_FOR relationships
        from Neo4j. If student_id is provided, only retrieves concepts
        extracted by that student.
        """
        G = nx.DiGraph()

        # 1. Fetch concept nodes
        if student_id:
            query_nodes = """
            MATCH (s:Student {id: $student_id})-[:HAS_EXTRACTED]->(c:Concept)
            RETURN c.id AS id, c.name AS name, c.description AS desc
            """
            params = {"student_id": student_id}
        else:
            query_nodes = "MATCH (c:Concept) RETURN c.id AS id, c.name AS name, c.description AS desc"
            params = {}
            
        nodes = self.conn.query(query_nodes, params)
        
        # Track valid IDs for this student to filter edges later
        valid_ids = set()
        for record in (nodes or []):
            G.add_node(record["id"], name=record["name"], description=record["desc"])
            valid_ids.add(record["id"])

        # 2. Fetch all prerequisite edges
        query_edges = """
        MATCH (source:Concept)-[:IS_PREREQUISITE_FOR]->(target:Concept)
        RETURN source.id AS source_id, target.id AS target_id
        """
        edges = self.conn.query(query_edges)
        
        for record in (edges or []):
            # Only add edges where both endpoints are in our subset (if filtering)
            if not student_id or (record["source_id"] in valid_ids and record["target_id"] in valid_ids):
                G.add_edge(record["source_id"], record["target_id"])

        print(f"Built NetworkX graph for student {student_id} with {G.number_of_nodes()} concepts and {G.number_of_edges()} prerequisites.")
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
