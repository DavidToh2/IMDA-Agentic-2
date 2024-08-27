
from AutogenAgentic import AutogenAgent
from LanggraphAgentic import LanggraphAgent

from LanggraphSingleAgent import LanggraphSingleAgent

from chroma.ChromaDatabase import internal_search

def main():

    autogen = AutogenAgent("Dario Amodei", "")
    autogen.start()

    # prompt = """Generate a speaker profile for Dario Amodei."""
    # detailed_instructions = ""
    # langgraph = LanggraphAgent(prompt, detailed_instructions)
    # langgraph.start()
    
main()