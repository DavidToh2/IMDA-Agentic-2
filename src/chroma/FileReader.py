
import os
from langchain_community.document_loaders import DirectoryLoader

class FileReader():
    def __init__(self, fpath=None):

        INTERNAL_FILES_DIR = f"{os.getcwd()}/internal_info/"

        # Build the VectorStore from a list of given documents.
        if fpath:
            self.loader = DirectoryLoader(fpath, glob="**/*.txt")
        else:
            self.loader = DirectoryLoader(INTERNAL_FILES_DIR, glob="**/*.txt")
        self.doc_chunks = self.loader.load()

    def get_chunks(self):
        return self.doc_chunks