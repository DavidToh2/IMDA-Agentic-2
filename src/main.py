
from AutogenSeqChatAgentic import AutogenSeqChatAgent

from chroma.ChromaDatabase import internal_search

def main():
    # Cache 103 AutogenGroupChat for demo
    autogen = AutogenSeqChatAgent("Mira Murati")
    autogen.start()

    prompt = """Write a profile of Mira Murati."""
    detailed_instructions = """
        Step 1. Conduct an online search of externally available data using the search_and_query tool, passing in search arguments in the external_search_query parameter.
        Step 2. Disregard all information irrelevant to the main task. Summarise the relevant websearch results into a preliminary report. Preface this report with the words 'EXTERNAL REPORT'.
        Step 3. Conduct an internal search of data in our internal database using the internal_search tool, passing in search arguments in the internal_search_query parameter.
        Step 4. Disregard all internal results irrelevant to the main task. Summarise the relevant internal information into a second report. Preface this report with the words 'INTERNAL REPORT'. If there is no relevant information in the internal database, skip the internal report and proceed directly to step 5.
        Step 5. Using your summary skills, write a combined report that includes only the information relevant to the main task. Preface this report with the words 'COMBINED REPORT'. Output the words 'DONE' to end off your report.

        Ensure you use the correct tool calling syntax. If your tool call returns with no output, it means you have failed to use the correct syntax: fix your syntax and try again.
        All your reports should be in paragraph form, and not in point form.
    """

    
main()