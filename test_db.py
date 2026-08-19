import os
from dotenv import load_dotenv

load_dotenv()

# Test Neo4j
from neo4j import GraphDatabase
uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USERNAME")
pwd = os.getenv("NEO4J_PASSWORD")

try:
    driver = GraphDatabase.driver(uri, auth=(user, pwd))
    driver.verify_connectivity()
    print("Neo4j Connected Successfully!")
except Exception as e:
    print(f"Neo4j Connection Failed: {e}")

# Test Mongo
from pymongo import MongoClient
mongo_uri = os.getenv("MONGO_URI")
try:
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    client.server_info()
    print("MongoDB Connected Successfully!")
except Exception as e:
    print(f"MongoDB Connection Failed: {e}")
