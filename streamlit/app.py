import streamlit as st
from streamlit_chat import message

from helpers.constants import APP_NAME, PAGE_ICON, USAGE_HELP
from helpers.helper import (
    authentication_and_options_side_bar,
    generate_response,
    initialize_session_state,
    update_chain,
)

# default session state variables
initialize_session_state()

# Page options and header
st.set_option("client.showErrorDetails", True)
st.set_page_config(
    page_title=APP_NAME, page_icon=PAGE_ICON, initial_sidebar_state="expanded"
)
st.markdown(
    # I don't know html so if we could make this prettier
    f"""<h1 style='text-align: center;'>{APP_NAME} {PAGE_ICON} </h1>
    <h2 style='text-align: center;'> Skip the queue! </h2>""",
    unsafe_allow_html=True,
)

# container to display infos stored to session state
# as it needs to be accessed from submodules <-- not sure what this does?
st.session_state["info_container"] = st.container()
# container for chat history
response_container = st.container()
# container for text box
text_container = st.container()

# sidebar widget with authentication and options
authentication_and_options_side_bar()

# we initialize chain after authentication is OK
# and upload and data source widgets are in place
if st.session_state["chain"] is None:
    update_chain()

# As streamlit reruns the whole script on each change
# it is necessary to repopulate the chat containers
with text_container:
    with st.form(key="prompt_input", clear_on_submit=True):
        user_input = st.text_area("You:", key="input", height=100)
        col1, col2 = st.columns([3, 1])
        submit_button = col1.form_submit_button(label="Send")
        clear_button = col2.form_submit_button("Clear Conversation")

if clear_button:
    # clear all chat related caches
    st.session_state["past"] = []
    st.session_state["generated"] = []
    st.session_state["chat_history"] = []

if submit_button and user_input:
    text_container.empty()
    output = generate_response(user_input)
    st.session_state["past"].append(user_input)
    st.session_state["generated"].append(output)
    # print(st.session_state["chat_history"])

if st.session_state["generated"]:
    with response_container:
        for i in range(len(st.session_state["generated"])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + "_user")
            message(st.session_state["generated"][i], key=str(i))


# Usage sidebar with total used tokens and costs
# We put this at the end to be able to show usage after the first response
with st.sidebar:
    if st.session_state["usage"]:
        st.divider()
        st.title("Usage", help=USAGE_HELP)
        col1, col2 = st.columns(2)
        col1.metric("Total Tokens", st.session_state["usage"]["total_tokens"])
        col2.metric("Total Costs in $", st.session_state["usage"]["total_cost"])
