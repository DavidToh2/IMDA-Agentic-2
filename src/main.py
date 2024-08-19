from ProfileGeneratorAgent import ProfileGeneratorAgent

from chroma.ChromaDatabase import internal_search

def main():

    prompt = input()
    pf = ProfileGeneratorAgent(prompt)
    pf.start()

main()