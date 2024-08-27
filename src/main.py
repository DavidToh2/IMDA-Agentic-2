
from AutogenAgentic import AutogenAgent
from LanggraphAgentic import LanggraphAgent

from LanggraphSingleAgent import LanggraphSingleAgent

from chroma.ChromaDatabase import internal_search

def main():

    # autogen = AutogenAgent("Dario Amodei", "")
    # autogen.start()

    prompt = """Generate a profile of Hu Heng Hua."""
    detailed_instructions = """
        Step 1. Conduct an online search of externally available data, passing in search arguments in the external_search_query parameter.
        Step 2. Conduct an internal search of data in our internal database, passing in search arguments in the internal_search_query parameter.
        Step 3. Using your summary skills, write a combined report using the information from the previous two steps. Preface your report with the words 'COMBINED REPORT'. Output the words 'DONE' to end off your report.
    """
    langgraph = LanggraphSingleAgent(prompt, detailed_instructions)
    langgraph.start()
    
main()