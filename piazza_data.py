from piazza_api import Piazza
import streamlit as st
import requests
import os
import json
from bs4 import BeautifulSoup
from tqdm import tqdm
import html
from joblib import Memory

memory = Memory("cache/", verbose=0)

CS40 = "lck5atzpw5k69m"
PIAZZA_BASE_LINK = "https://piazza.com/class/"

# Used to download files that are embedded in the Piazza Post
def download_file(url, directory, filename):
    with requests.get(url, stream=True) as response:
        file_path = os.path.join(directory, filename)
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
    return file_path

def get_content(answer, key):
    try:
        return answer[key]
    except:
        return ''
    
def get_history_content(answer, key):
    try:
        return answer["history"][0][key]
    except:
        return ''
    
    
def get_length(answer, key):
    try:
        return len(answer[key])
    except:
        return 0

# We only want to get answers that were endorsed by instructors, otherwise our docs will be filled with gahbhage
@memory.cache  # Cache not tested.
def get_post_answers(answers) -> str:
    answer_string = ""
    for i, answer in enumerate(answers):
        # There are a few place the content can be:
        #   answer["history"][0]["content" OR "subject"]
        #   OR answer["subject"] OR answer ["content"]
        if get_length(answer, "tag_endorse") != 0 or get_length(answer, "tag_good") != 0:
            answer_content = get_history_content(answer, 'subject')
            if answer_content == '':
                answer_string += f"Answer #{i}: \n {get_history_content(answer, 'content')} \n" # this has html in it
            else:
                answer_string += f"Answer #{i}: \n {answer_content} \n" # this has html in it
            # checking in subject and content now
            if answer_content == '':
                answer_content = get_content(answer, 'subject')
                if answer_content == '':
                    answer_string += f"Answer #{i}: \n {get_content(answer, 'content')} \n" # this has html in it
                else:
                    answer_string += f"Answer #{i}: \n {answer_content} \n" # this has html in it
            # TODO: Not doing followup questions within followup questions for now...
    return answer_string

@memory.cache  # Cache not tested.
def get_text(html_text):
    soup = BeautifulSoup(html_text, 'lxml')
    text = soup.get_text()
    return html.unescape(text)

@memory.cache  # Cache not tested.
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
        post_topic = post["history"][0]["subject"]
        post_type = post["type"]
        link_to_post = f"{PIAZZA_BASE_LINK}{CS40}/post/{post['nr']}"
        post_answers = get_post_answers(post["children"])

        # If post did not recieve an answer remove it. If post was a note, we should keep it.
        if post_answers != '':
            try:
                post_content = get_text(post["history"][0]["content"]) # this key config may change?
            except TypeError:
                print("yeap")
            try:
                file_path = f"data/Piazza_docs/{file_string}/{post['nr']}.txt"
                with open(file_path, 'w') as file:
                    file.write(f""" 
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
                        """)
            except: # This exception should be that the file already exists?
                print(f"Could not open file {file_path}")

p = Piazza()

Email, Password = st.secrets["PIAZZA_EMAIL"], st.secrets["PIAZZA_PASSWORD"]

p.user_login(email=Email, password=Password)

cs40 = p.network(CS40)

# post = []
# post.append(cs40.get_post(522))

posts = cs40.iter_all_posts()
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

    "tag_good_arr": contains user ids of those that tagged it as good, length could be a good indicator
        of question importance if we introduce weights into stored files. It's actually the 'good note' button
        store.

    "folders": The list contains a single item, "final_exam", which likely indicates the folder(s) to which the data is categorized or belongs.

    "data": The dictionary contains data related to the main dataset, possibly including embedded links.

    "created": The timestamp "2023-05-03T18:33:03Z" indicates the date and time when the data was created.

    "bucket_order": The number 0 represents the order or priority of the data in a specific bucket or category.

    "no_answer_followup": The number 0 indicates the count of unanswered follow-up interactions or responses.

    "bucket_name": The string "Pinned" represents the name of the bucket or category to which the data is pinned.
    "history": The list contains records of historical versions of the data, including the user, subject, created date, and content of each version.
    "type": The string "note" refers to the type of data, which is a note in this case.
    "tags": The list contains tags associated with the data, such as "final_exam", "instructor-note", and "pin".
    "tag_good": The list contains records of individuals who have endorsed the tags, including their roles, names, and other relevant information.
    "unique_views": The number 145 represents the count of unique views the data has received.
    "children": The list contains nested data items related to the main data, such as follow-up interactions or responses.
    "id": The string "lh81dhg1m0z2ug" represents a unique identifier for the data.
    "status": The string "active" indicates the current status of the data.
    "request_instructor": The number 0 indicates whether there is a request made to the instructor regarding the data (0 for no, 1 for yes).
    "bookmarked": The number 5 represents the count of times the data has been bookmarked.
    "num_favorites": The number 2 represents the count of favorites associated with the data.
"""