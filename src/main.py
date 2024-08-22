from ProfileGeneratorAgent import ProfileGeneratorAgent

from chroma.ChromaDatabase import internal_search

def main():

    prompt = """Write a profile of Dario Amodei."""
    detailed_instructions = """
        Step 1. Write a preliminary version of the profile, using only externally available data provided by the search_and_crawl tool. Preface this profile with the words '**EXTERNAL INFORMATION PROFILE**'.
        Step 2. Write a second version of the profile, using only internally available data provided by the internal_search tool. Preface this profile with the words '**INTERNAL INFORMATION PROFILE**'.
        Step 3. Combine the first two versions of the profile into a third version. Preface this profile with the words '**COMBINED PROFILE**'.
        DO NOT REPEAT ANY OF THE PREVIOUS STEPS OR TOOL CALLS UNNECESSARILY.
    """
    pf = ProfileGeneratorAgent(prompt, detailed_instructions)
    pf.start()

    # print(internal_search("Dario Amodei"))
    
main()