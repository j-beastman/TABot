DATA_DICTIONARY = """
    "history[0] (list) but it has like multiple versions (idk),
        content: Holds the question, sometimes has links to documentation** 
                (need to extract)
        subject: Subject of question

    "type": either "note", many others I'm sure

    "tags (list)":
        Not sure what values these could have

    "tag_good (list of dictionaries)":
        list of people that endorsed the question/post/note
            dictionary:
                role: 'ta', 'professor', 'student'

    "children (list of dictionaries)": (possibly answers/followups)
        "subject": this is actually the content of the response
        "created": date created
        "tag_good": endorsements
            role: as above
        "children (list of dictionaries)": a followup to the followup
"""
