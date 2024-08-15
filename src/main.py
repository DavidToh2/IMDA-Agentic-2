from ProfileGeneratorAgent import ProfileGeneratorAgent

from chroma.ChromaDatabase import internal_search

def main():
    # pf = ProfileGeneratorAgent("Generate a list of profiles of all speakers at the ATX Plenary 2024")
    # pf.start()

    internal_search(qn = "Mao Zedong")

main()