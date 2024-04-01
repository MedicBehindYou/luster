from langcodes import Language

def lang_tag(language_name):
    try:
        lang = Language.find(language_name)
        if lang:
            return lang
        else:
            return False
    except ValueError:
        return False
