
from AutogenAgentic import ProfileGeneratorAgent

from chroma.ChromaDatabase import internal_search

def main():

    prompt = """Generate a speaker profile for Dario Amodei."""
    detailed_instructions = ""
    pf = ProfileGeneratorAgent("Dario Amodei")
    pf.start()

    # print(internal_search("Dario Amodei"))
    
main()