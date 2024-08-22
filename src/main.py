from ProfileGeneratorAgent_v2 import ProfileGeneratorAgent

from chroma.ChromaDatabase import internal_search

def main():

    prompt = """Write a report of the Crowdstrike incident."""
    detailed_instructions = """
        Step 1. Write a preliminary version of the report, using only externally available data provided by the search_and_crawl tool. Preface this report with the words '**EXTERNAL INFORMATION**'.
        Step 2. Write a second version of the report, using only internally available data provided by the internal_search tool. Preface this report with the words '**INTERNAL INFORMATION**'.
        Step 3. Combine the first two versions of the report into a third version. Preface this report with the words '**COMBINED REPORT**'.
        DO NOT REPEAT ANY OF THE PREVIOUS STEPS OR TOOL CALLS UNNECESSARILY.
    """
    pf = ProfileGeneratorAgent(prompt, detailed_instructions)
    pf.start()

    # print(internal_search("Dario Amodei"))
    
main()