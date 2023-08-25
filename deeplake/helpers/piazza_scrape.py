import html
import os

from bs4 import BeautifulSoup
from piazza_api import Piazza
from tqdm import tqdm

from constants import (
    CLASS,
    CS40_ID
)
from credentials import (
    PIAZZA_EMAIL,
    PIAZZA_PASSWORD
)

PIAZZA_BASE_LINK = "https://piazza.com/class/"

# If string has markdown or html stuff in it, it strips
#   and returns the raw text
def get_text(html_text):
    soup = BeautifulSoup(html_text, "lxml")
    text = soup.get_text()
    return html.unescape(text)

# There are a few places where the answer can be unfortunately, so we have
#   have to check all of them. Good thing it's never in 2 places
def get_answer_contents(answer) -> str:
    try:
        return get_text(answer['content'])
    except KeyError:
        try:
            return get_text(answer['subject'])
        except KeyError:
            try:
                return get_text(answer["history"][0]["content"])
            except KeyError:
                try:
                    return get_text(answer["history"][0]["subject"])
                except KeyError:
                    print("Unexpected Behavior, answer lies somewhere else")
                    print("here is the answer", answer)

def get_length(answer, key) -> int:
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

def output_to_file(posts, class_name, class_id) -> None:
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
            # This case was a poll... very interesting
            print(f"{PIAZZA_BASE_LINK}{class_id}/post/{post['nr']}")
            print("neither appeared")
            continue
        post_answers = get_post_answers(post["children"])
        # If post did not receive an answer remove it. If post was a note, we
        # should keep it.
        if post_answers == "":
            continue

        post_folder = " ,".join([folder for folder in post["folders"]])
        post_topic = get_text(post["history"][0]["subject"])
        post_type = post["type"]
        link_to_post = f"{PIAZZA_BASE_LINK}{class_id}/post/{post['nr']}"
        
        try:
            post_content = get_text(post["history"][0]["content"])
        except TypeError:
            print("Key configuration changed")
        
        file_path = f"deeplake/data/{class_name}/Piazza_docs/{sub_directory}/{post['nr']}.txt"
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

def scrape_piazza(class_name: str, class_id:int, email:str, password:str) -> None:
    p = Piazza()
    p.user_login(email="john@bee-haven.com", password="Dana#113")

    class_connection = p.network(class_id)
    posts = class_connection.iter_all_posts(limit=None, sleep=1)
    output_to_file(posts, class_name=class_name, class_id=class_id)

scrape_piazza(CLASS, CS40_ID, PIAZZA_EMAIL, PIAZZA_PASSWORD)
