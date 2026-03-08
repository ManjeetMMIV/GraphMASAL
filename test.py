import os
from dotenv import load_dotenv
from src.graph.db import Neo4jConnection

load_dotenv()
conn = Neo4jConnection(os.getenv('NEO4J_URI'), os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))

# First check if the index exists
q1 = "SHOW VECTOR INDEXES"
print("Indexes:")
for r in conn.query(q1):
    print(r)

# Then test query
cypher = """
CALL db.index.vector.queryNodes('concept_embedding', $top_k, $embedding)
YIELD node AS concept, score AS similarity
RETURN concept.id, similarity
"""
params = {'top_k': 3, 'embedding': [0.1]*384}
print("\nTesting Query:")
res = conn.query(cypher, params)
if res is not None:
    for r in res:
        print(r)
conn.close()
