from LanggraphSingleAgent import ProfileGeneratorAgent
from LanggraphAgentic import LanggraphAgent

from chroma.ChromaDatabase import internal_search

def main():

    prompt = """Write a report of the Crowdstrike incident."""
    detailed_instructions = """
        Step 1. Conduct an online search of externally available data.
        Step 2. Conduct an internal search of data in our internal database.
        Step 3. Combine the results of the above two steps into a report. Separate the information gathered externally from the information gathered internally.
    """
    pf = LanggraphAgent(prompt, detailed_instructions)
    pf.start()

    # print(internal_search("Dario Amodei"))
    
main()