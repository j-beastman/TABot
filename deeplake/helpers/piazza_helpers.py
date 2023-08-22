import html
import os
import requests

from bs4 import BeautifulSoup
from joblib import Memory
from tqdm import tqdm

PIAZZA_BASE_LINK = "https://piazza.com/class/"

memory = Memory("cache/", verbose=0)


def download_file(url, directory, filename):
    with requests.get(url, stream=True) as response:
        file_path = os.path.join(directory, filename)
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
    return file_path

# If string has markdown or html stuff in it, it strips
#   and returns the raw text
def get_text(html_text):
    soup = BeautifulSoup(html_text, "lxml")
    text = soup.get_text()
    return html.unescape(text)

# There are a few places where the answer can be unfortunately, so we have
#   have to check all of them. Good thing it's never in 2 places
def get_answer_contents(answer):
    try:
        return get_text(answer['content'])
    except:
        try:
            return get_text(answer['subject'])
        except:
            try:
                return get_text(answer["history"][0]["content"])
            except:
                try:
                    return get_text(answer["history"][0]["subject"])
                except:
                    print("Unexpected Behavior, answer lies somewhere else")
                    print("here is the answer", answer)

def get_length(answer, key):
    try:
        return len(answer[key])
    except BaseException:
        return 0

def get_post_answers(answers) -> str:
    answer_string = ""
    for i, answer in enumerate(answers):
        if (
            get_length(answer, "tag_endorse") != 0
            or get_length(answer, "tag_good") != 0
        ):
            answer_content = get_answer_contents(answer)
            answer_string += (
                f"Answer #{i}: \n {answer_content} \n"
            )
            # TODO: Not doing followup questions within followup questions for
            # now...
    return answer_string

def output_to_file(posts, class_name, class_id):
    for post in tqdm(posts):
        instructor, student = False, False
        sub_directory = ""
        for tag in post["tags"]:
            if tag == "instructor-note":
                instructor = True
                sub_directory = "admin_posts"
            elif tag == "student":
                student = True
                sub_directory = "student_posts"
        if not (student or instructor):
            # This case was a poll... vewy interesting
            print(f"{PIAZZA_BASE_LINK}{class_id}/post/{post['nr']}")
            print("neither appeared")
            continue
        post_answers = get_post_answers(post["children"])
        # If post did not recieve an answer remove it. If post was a note, we
        # should keep it.
        if post_answers == "":
            continue

        post_folder = " ,".join([folder for folder in post["folders"]])
        post_topic = get_text(post["history"][0]["subject"])
        post_type = post["type"]
        link_to_post = f"{PIAZZA_BASE_LINK}{class_id}/post/{post['nr']}"
        
        try:
            # this key config may change?!
            post_content = get_text(post["history"][0]["content"])
        except TypeError:
            print("yeap it changed")
        
        file_path = f"data/{class_name}/Piazza_docs/{sub_directory}/{post['nr']}.txt"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as file:
            file.write(
                f"""
                The topic for this {post_type} is {post_topic} \n
                This {post_type} is from the {post_folder} folder \n
                Here is the {post_type} (delimited by '```') \n
                ```
                {post_content}
                ``` \n
                Here is are the follow-ups to the {post_type}, also delimited by '```'
                ```
                {post_answers}
                ```
                Link--> >:) {link_to_post}
                """
            )



DATA_DICTIONARY = """
    "history[0] (list) but it has like multiple versions (idk),
        content: Holds the question, sometimes has links to documentation** (need to extract)
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
