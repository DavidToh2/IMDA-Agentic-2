
from AutogenAgentic import AutogenAgent
from LanggraphAgentic import LanggraphAgent

from LanggraphSingleAgent import LanggraphSingleAgent

from chroma.ChromaDatabase import internal_search

def main():

    prompt = """Generate a speaker profile for Dario Amodei."""
    detailed_instructions = ""
    pf = AutogenAgent("Dario Amodei")
    pf.start()

    # print(internal_search("Dario Amodei"))
    
main()