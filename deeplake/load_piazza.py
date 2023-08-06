from piazza_api import Piazza
import streamlit as st

from helpers.piazza_helpers import output_to_file

from credentials import EMAIL, PASSWORD

CLASSES = {
    "cs40": {
        "id": "lck5atzpw5k69m",
    }
}

p = Piazza()


p.user_login(email=EMAIL, password=PASSWORD)

for cs_class in CLASSES:
    class_connection = p.network(CLASSES[cs_class]["id"])
    posts = class_connection.iter_all_posts(limit=None, sleep=1)
    output_to_file(posts, cs_class, CLASSES[cs_class]["id"])
