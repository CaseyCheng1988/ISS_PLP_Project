import os

################################################
# Shortcut for project directory here
################################################
PROJ_DIR = os.path.abspath(os.path.dirname(__file__))
NER_MODEL = os.path.join(PROJ_DIR, 'TitleNER', 'title_model')

if __name__ == '__main__':
    print(PROJ_DIR)