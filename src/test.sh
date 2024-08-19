QUERY="Generate a profile of all speakers at the ATX Plenary 2024
Generate a profile template
Find a list of all speakers by performing an online search using the search_and_crawl tool
For each speaker, perform an online search using the search_and_crawl tool
For each speaker, perform an internal search using the internal_search tool
Synthesize the profiles of all speakers"
QUERY_BASIC="Generate profiles of all speakers at the ATX Plenary 2024"

echo $QUERY_BASIC | python3 ./src/main.py