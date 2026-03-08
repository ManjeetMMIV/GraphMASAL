import os
import re
from typing import List

# very simplified concept extraction for demonstration.
# In a real-world scenario, you might use an LLM or SpaCy to extract
# key terms and the prerequisite relationships. Here, we'll
# establish some base concepts based on the OSTEP content.

class OstepParser:
    def __init__(self, data_directory: str):
        self.data_directory = data_directory

    def extract_concepts(self) -> List[dict]:
        """
        Parses Markdown files to extract concepts and prerequisites.
        For this prototype, we'll seed it with known concepts from OS.
        In a full implementation, you'd run NLP over self.data_directory.
        """
        print(f"Parsing directory: {self.data_directory}")

        # Seed data based on generally known OS concepts
        # and inferred from the syllabus
        concepts = [
            {
                "id": "computer-architecture",
                "name": "Computer Architecture",
                "description": "Basic structure of computers, CPU, Memory, I/O.",
                "prerequisites": [],
                "domain": "Operating Systems"
            },
            {
                "id": "cpu-virtualization",
                "name": "CPU Virtualization",
                "description": "How the OS provides the illusion of many CPUs.",
                "prerequisites": ["computer-architecture"],
                "domain": "Operating Systems"
            },
            {
                "id": "processes",
                "name": "Processes",
                "description": "The abstraction of a running program.",
                "prerequisites": ["cpu-virtualization"],
                "domain": "Operating Systems"
            },
            {
                "id": "scheduling",
                "name": "Process Scheduling",
                "description": "Policies to determine which process runs next.",
                "prerequisites": ["processes"],
                "domain": "Operating Systems"
            },
            {
                "id": "memory-virtualization",
                "name": "Memory Virtualization",
                "description": "How the OS provides the illusion of infinite memory.",
                "prerequisites": ["computer-architecture"],
                "domain": "Operating Systems"
            },
            {
                "id": "paging",
                "name": "Paging",
                "description": "Dividing memory into fixed-size pages.",
                "prerequisites": ["memory-virtualization"],
                "domain": "Operating Systems"
            },
            {
                "id": "concurrency",
                "name": "Concurrency",
                "description": "Execution of multiple instruction sequences at the same time.",
                "prerequisites": ["processes", "memory-virtualization"],
                "domain": "Operating Systems"
            },
            {
                "id": "threads",
                "name": "Threads",
                "description": "Multiple independent execution units within a single process.",
                "prerequisites": ["concurrency"],
                "domain": "Operating Systems"
            },
            {
                "id": "locks",
                "name": "Locks",
                "description": "Synchronization mechanisms to protect critical sections.",
                "prerequisites": ["threads"],
                "domain": "Operating Systems"
            },
            {
                "id": "persistence",
                "name": "Persistence",
                "description": "Storing data long-term, beyond the life of a process.",
                "prerequisites": ["computer-architecture"],
                "domain": "Operating Systems"
            },
            {
                "id": "file-systems",
                "name": "File Systems",
                "description": "OS abstractions for persistent storage (files, directories).",
                "prerequisites": ["persistence"],
                "domain": "Operating Systems"
            },
            {
                "id": "data-integrity",
                "name": "Data Integrity and Protection",
                "description": "Ensuring data is safe from failures (RAID, checksums).",
                "prerequisites": ["file-systems"],
                "domain": "Operating Systems"
            }
        ]
        
        # Example of how you'd dynamically parse (skipped for brevity/accuracy in this seeding tool)
        # for filename in os.listdir(self.data_directory):
        #     if filename.endswith(".md"):
        #         with open(os.path.join(self.data_directory, filename), 'r', encoding='utf-8') as f:
        #             text = f.read()
        #             # (Run NLP / regex here)
        
        return concepts

if __name__ == "__main__":
    parser = OstepParser("data_md")
    concepts = parser.extract_concepts()
    print(f"Extracted {len(concepts)} concepts for the graph.")
