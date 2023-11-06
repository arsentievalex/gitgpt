# GitDoc - AI-Powered Code Documentation with Streamlit & Llama-Index

GitDoc is a Streamlit application that leverages the power of GPT models to automatically generate documentation for your code. With GitDoc, you can streamline your documentation process, ensuring that your codebase is always accompanied by up-to-date and comprehensive explanations.

## Features

- **AI-Powered Documentation**: Utilize state-of-the-art large langugage models to create initial drafts or enhance existing documentation.
- **Support for Multiple Languages**: GitDoc can generate documentation for a variety of programming languages.
- **Interactive UI**: Easy-to-use web interface built with Streamlit for a smooth user experience.
- **Customization Options**: Tailor the documentation style for techical or non-technical audiences.
- **Export Functionality**: Export your generated documentation to PDF.

## LLM Architecture
The index embedding & querying is facilitated by LlamaIndex - a flexible framework that enables LLM applications to ingest, structure, access, and retrieve private data sources through Retrieval Augmented Generation (RAG).
![rag](https://blog.streamlit.io/content/images/2023/08/rag-with-llamaindex-1.png)

## Installation

Before you can run GitDoc, you'll need to have Python and Streamlit installed. Follow these steps to get started:

1. **Clone the GitDoc Repository**

   ```bash
   git clone https://github.com/arsentievalex/gitdoc.git
   cd gitdoc
   ```

2. **Set up a Python Environment (Optional but recommended)**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   Certainly! You can add an additional section in the README to inform users about the extra dependencies. Here's how you can update the Installation section to include `graphviz` and `wkhtmltopdf`.

---

## Installation

Before you can run GitDoc, you'll need to have Python, Streamlit, and a couple of additional packages installed. Follow these steps to get started:

1. **Clone the GitDoc Repository**

   ```bash
   git clone https://github.com/your-username/gitdoc.git
   cd gitdoc
   ```

2. **Set up a Python Environment (Optional but recommended)**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**

   Install the required Python packages using `pip`:

   ```bash
   pip install -r requirements.txt
   ```
   
   In addition to Python packages, GitDoc requires `graphviz` and `wkhtmltopdf` to be installed on your system:

   - For **graphviz**:

     - On Ubuntu/Debian:

       ```bash
       sudo apt-get install graphviz
       ```

     - On macOS (using Homebrew):

       ```bash
       brew install graphviz
       ```

     - On Windows (using Chocolatey):

       ```bash
       choco install graphviz
       ```

   - For **wkhtmltopdf**:

     - On Ubuntu/Debian:

       ```bash
       sudo apt-get install wkhtmltopdf
       ```

     - On macOS (using Homebrew):

       ```bash
       brew install wkhtmltopdf
       ```

     - On Windows (using Chocolatey):

       ```bash
       choco install wkhtmltopdf
       ```

     Please visit the official websites for `graphviz` and `wkhtmltopdf` for detailed installation instructions for other operating systems or configurations.

4. **Run the Streamlit App**

   ```bash
   streamlit run app.py
   ```

   The app should now be running and accessible through your web browser at the address indicated by Streamlit (typically `localhost:8501`).

---

Please ensure that all the dependencies are correctly installed for the GitDoc app to function properly.

4. **Run the Streamlit App**

   ```bash
   streamlit run app.py
   ```

   The app should now be running and accessible through your web browser at the address indicated by Streamlit (typically `localhost:8501`).
