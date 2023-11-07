import streamlit as st
import pickle
import os
import openai
import graphviz
import re
from llama_index import download_loader, VectorStoreIndex, ServiceContext
from llama_hub.github_repo import GithubClient, GithubRepositoryReader
from llama_index.llms import OpenAI
import io
import pdfkit
import base64
import markdown

st.set_page_config(page_title="GitDoc", page_icon="✨", layout="wide", menu_items=None)


@st.cache_resource(show_spinner=False)
def get_loader():
    download_loader("GithubRepositoryReader")


def load_index(docs):
    service_context = ServiceContext.from_defaults(llm=OpenAI(model=st.session_state.model, temperature=0,
                                                              system_prompt="You are a software development expert who is helping write code documentation for different audiences"))

    index = VectorStoreIndex.from_documents(docs, service_context=service_context)
    return index


@st.cache_data
def load_docs(owner, repo, branch):
    """
    Load the documents from the Github repository.
    """
    github_client = GithubClient(os.getenv("GITHUB_TOKEN"))
    loader = GithubRepositoryReader(
        github_client,
        owner=owner,
        repo=repo,
        filter_file_extensions=([".py"], GithubRepositoryReader.FilterType.INCLUDE),
        verbose=True,
        concurrent_requests=10,
    )

    docs = loader.load_data(branch=branch)

    return docs


def _process_code_block(block):
    """
    Process a code block so it can be executed by Streamlit.
    Args:
    - block (str): The extracted code block
    Returns:
    - str: Processed code block
    """

    block = block.replace('python', '').strip()

    # if there are lines that start with dot.save, dot.render or dot.view, remove them
    block = re.sub(r'dot\.(save|render|view)\(.*?\)', '', block)

    # add st.header('Flowchart Diagram') as the first line of the extracted code
    block = 'st.write("")\n' + 'st.header("Flowchart Diagram")\n' + block

    # add the following lines to the end of the extracted code to save the graphviz as png
    block += "\nimage_filename = 'flowchart'"
    block += "\ndot.format = 'png'"
    block += "\ndot.render(filename=image_filename, view=False)"

    if 'st.graphviz_chart(dot, use_container_width=True)' not in block:
        # add to the end of the extracted code
        # show the graphviz chart in Streamlit
        block += '\nst.graphviz_chart(dot, use_container_width=True)'
        # save dot object to session state
        block += '\nst.session_state.dot = dot'

    return block


def extract_code(gpt_response):
    """
    Extract code or SQL query from a GPT response.
    Args:
    - gpt_response (str): The string response from GPT
    Returns:
    - str: Extracted code or SQL query
    """

    # Search for text blocks enclosed by ```
    pattern = r'```(.*?)```'
    extracted_code_list = re.findall(pattern, gpt_response, re.DOTALL)

    # If no code blocks are found, return an empty string
    if not extracted_code_list:
        return ""

    # If there's only one block, process and return it
    if len(extracted_code_list) == 1:
        return _process_code_block(extracted_code_list[0])

    # If bash is in the first code block (indicating pip install or similar commands),
    # and there's a second block, return the second block
    if "bash" in extracted_code_list[0] and len(extracted_code_list) > 1:
        return _process_code_block(extracted_code_list[1])

    # In other cases, just return the first block
    return _process_code_block(extracted_code_list[0])


def on_submit_button_click():

    # set the openai api key and github token
    openai.api_key = st.session_state.gpt_key
    os.environ['GITHUB_TOKEN'] = st.session_state.github_token

    # parse the github url
    try:
        parse_github_url(st.session_state['github_url'])
    except:
        st.error("Please enter a valid Github URL.")
        return

    docs = load_docs(owner=st.session_state.owner, repo=st.session_state.repo, branch=st.session_state.branch)

    index = load_index(docs)
    chat_engine = index.as_chat_engine(chat_mode='context')
    # save chat engine to session state
    st.session_state.chat_engine = chat_engine

    doc_prompt = f"""
    Generate clear, concise, and comprehensive documentation for the code in context ensuring you explain its
    functionality, usage, parameters, and any potential edge cases or limitations. Also, make sure to include any dependencies,
    data sources or APIs that are used.
    The documentation should be written for a {st.session_state.audience} audience.
    """

    doc_response = chat_engine.stream_chat(doc_prompt)

    full_response = []

    for token in doc_response.response_gen:
        full_response.append(token)
        result = "".join(full_response).strip()
        with streaming_box.container():
            st.markdown(result)

    # Concatenate and store the streamed chunks to a full response
    st.session_state.output_text = "".join(full_response).strip()


def generate_graph():
    with st.spinner('Generating flowchart diagram...⏳'):
        diagram_prompt = f"""
        Create flowchart diagram for the code in context using Graphviz in Python.
        Ensure that the diagram is clear and shows the most important parts of the code.
        Use common naming conventions, and DO NOT render the dot variable.
        DO NOT include pip install steps.
        The diagram should be written for a {st.session_state.audience} audience.
        """

        # call LLM to get the diagram response
        diagram_response = st.session_state.chat_engine.chat(diagram_prompt)

        # extract code from response
        extracted_code = extract_code(diagram_response.response)

        try:
            exec(extracted_code)
            st.session_state['generated_graph'] = True
        except Exception as e:
            pass


def get_binary_file_downloader_html(bin_file, file_label='File'):
    """function to create a URL for the user to download a file"""

    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,' \
           f'{bin_str}" download="{os.path.basename(bin_file)}">{file_label}</a>'

    return href


def parse_github_url(url):
    # Regex pattern to match the structure of GitHub URL
    pattern = re.compile(r"https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)(/tree/(?P<branch>[^/]+))?")

    match = pattern.match(url)
    if not match:
        raise ValueError("Invalid GitHub URL")

    # Extract the components from the URL
    st.session_state.owner = match.group('owner')
    st.session_state.repo = match.group('repo')
    st.session_state.branch = match.group('branch') if match.group('branch') else 'main'


# download github loader
get_loader()

# check if the session state variables are initialized
if "chat_engine" not in st.session_state:
    st.session_state.chat_engine = None
if "generated_graph" not in st.session_state:
    st.session_state.generated_graph = False
if 'owner' not in st.session_state:
    st.session_state.owner = None
if 'repo' not in st.session_state:
    st.session_state.repo = None
if 'branch' not in st.session_state:
    st.session_state.branch = None
if 'gpt_key' not in st.session_state:
    st.session_state.gpt_key = None
if 'github_token' not in st.session_state:
    st.session_state.github_token = None
if 'model' not in st.session_state:
    st.session_state.model = None

st.title('GitDoc - Generate Code Documentation In a Snap')

file_types_list = [
    ".py",    # Python scripts
    ".js",    # JavaScript files
    ".html",  # HTML files
    ".css",   # CSS files
    ".c",     # C source code files
    ".cpp",   # C++ source code files
    ".java",  # Java source code files
    ".php",   # PHP scripts
    ".rb",    # Ruby scripts
    ".ts",    # TypeScript files
    ".txt",  # Text files
    ".md",  # Markdown files
]

with st.sidebar:
    st.subheader('Authentication')
    with st.expander('Enter your API keys'):
        st.session_state.gpt_key = st.text_input("OpenAI API Key", placeholder='**-************************************************')
        st.session_state.github_token = st.text_input("GitHub Token", placeholder='***_************************************')

    st.subheader('GitHub Repository')
    st.session_state['github_url'] = st.text_input("GitHub URL",  help="Enter the URL of the GitHub repository you want to generate documentation for.")

    st.write('')
    with st.expander('Advanced'):
        file_types = st.multiselect(label='File Types', options=file_types_list, default='.py')
        st.session_state.model = st.selectbox('Model', ['gpt-4', 'gpt-4-1106-preview', 'gpt-3.5-turbo'])
        st.session_state.audience = st.selectbox('Audience', ['technical', 'non-technical'])

    st.write('')
    run_button = st.button('Generate Documentation', on_click=on_submit_button_click)

# For Showing the Streaming Output
streaming_box = st.empty()

# For Showing the Completed Output
if 'output_text' in st.session_state:
    st.markdown(st.session_state['output_text'])

    # if graph is generated, show it
    if st.session_state['generated_graph'] == True:
        try:
            st.write('')
            st.header("Flowchart Diagram")
            st.write('')
            st.graphviz_chart(st.session_state.dot, use_container_width=True)
        except:
            pass
    else:
        st.write('')
        generate_graph()

    # download pdf button
    with st.sidebar:
        download_button = st.button('Download PDF')

        if download_button:

            #config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")

            # convert markdown to html for pdf export
            html_output = markdown.markdown(st.session_state['output_text'])

            # check if flowchart.png exists
            if os.path.exists('flowchart.png'):
                #append diagram image to html
                image_path = "flowchart.png"

                # Convert image to base64 encoding
                with open(image_path, "rb") as image_file:
                    encoded_image_data = base64.b64encode(image_file.read()).decode('utf-8')

                # Embed the base64 encoded image in HTML
                html_output += f'<img src="data:image/png;base64,{encoded_image_data}" alt="Flowchart diagram" />'

            file_name = f"{st.session_state.owner}_{st.session_state.repo}_{st.session_state.branch}.pdf"
            pdfkit.from_string(html_output, file_name)

            # with open('output.pdf', 'rb') as f:
            #     st.download_button(label="Download PDF", data=f, file_name='output.pdf', mime='application/pdf')

            st.markdown(get_binary_file_downloader_html(file_name, file_name), unsafe_allow_html=True)

            # clean up
            os.remove(file_name)
            os.remove('flowchart.png')
            os.remove('flowchart')





