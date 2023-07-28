import html
import os

import requests
import streamlit as st
from bs4 import BeautifulSoup
from joblib import Memory
from piazza_api import Piazza
from tqdm import tqdm

memory = Memory("cache/", verbose=0)

CLASS = "cs40"
CS40 = "lck5atzpw5k69m"
PIAZZA_BASE_LINK = "https://piazza.com/class/"

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

def get_content(answer, key):
    try:
        return get_text(answer[key])
    except BaseException:
        return ""

def get_history_content(answer, key):
    try:
        return get_text(answer["history"][0][key])
    except BaseException:
        return ""

def get_answer_contents(answer):
    try:
        return get_text(answer['content'])
    except:
        try:
            return get_text(answer['subject'])
        except:
            try:
                return get_text(answer["history"]["0"]["content"])
            except:
                try:
                    return get_text(answer["history"]["0"]["subject"])
                except:
                    print("Unexpected Behavior, answer lies somewhere else")

def get_length(answer, key):
    try:
        return len(answer[key])
    except BaseException:
        return 0

def get_post_answers(answers) -> str:
    answer_string = ""
    for i, answer in enumerate(answers):
        # There are a few place the content can be:
        #   answer["history"][0]["content" OR "subject"]
        #   OR answer["subject"] OR answer ["content"]
        if (
            get_length(answer, "tag_endorse") != 0
            or get_length(answer, "tag_good") != 0
        ):
            answer_content = get_history_content(answer, "subject")
            if answer_content == "":
                # this has html in it
                answer_string += (
                    f"Answer #{i}: \n {get_history_content(answer, 'content')} \n"
                )
            else:
                # this has html in it
                answer_string += f"Answer #{i}: \n {answer_content} \n"
            # checking in subject and content now
            if answer_content == "":
                answer_content = get_text(get_content(answer, "subject"))
                if answer_content == "":
                    # this has html in it
                    answer_string += (
                        f"Answer #{i}: \n {get_content(answer, 'content')} \n"
                    )
                else:
                    # this has html in it
                    answer_string += f"Answer #{i}: \n {answer_content} \n"
            # TODO: Not doing followup questions within followup questions for
            # now...
    return answer_string


# @memory.cache  # Cache not tested.
def output_to_file(posts):
    for post in tqdm(posts):
        instructor, student = False, False
        file_string = ""
        for tag in post["tags"]:
            if tag == "instructor-note":
                instructor = True
                file_string = "admin_posts"
            elif tag == "student":
                student = True
                file_string = "student_posts"
        if student and instructor:
            print("something went wrong, both tags appeared")
            exit()
        if not (student or instructor):
            # This case was a poll... vewy interesting
            print(f"{PIAZZA_BASE_LINK}{CS40}/post/{post['nr']}")
            print("neither appeared")
            # exit()

        post_folder = " ,".join([folder for folder in post["folders"]])
        post_topic = get_text(post["history"][0]["subject"])
        post_type = post["type"]
        link_to_post = f"{PIAZZA_BASE_LINK}{CS40}/post/{post['nr']}"
        post_answers = get_post_answers(post["children"])

        # If post did not recieve an answer remove it. If post was a note, we
        # should keep it.
        if post_answers != "":
            try:
                # this key config may change?
                post_content = get_text(post["history"][0]["content"])
            except TypeError:
                print("yeap")
            try:
                file_path = f"data/{CLASS}/Piazza_docs/{file_string}/{post['nr']}.txt"
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
            except (
                BaseException
            ):  # This exception should be that the file already exists?
                print(f"Could not open file {file_path}")


p = Piazza()

Email, Password = st.secrets["PIAZZA_EMAIL"], st.secrets["PIAZZA_PASSWORD"]

p.user_login(email=Email, password=Password)

cs40 = p.network(CS40)

# post = []
# post.append(cs40.get_post(522))

posts = cs40.iter_all_posts(sleep=1)
# print(json.dumps(cs40.get_post(620), indent=4))
output_to_file(posts)


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
