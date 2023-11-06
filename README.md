# GitDoc - AI-Powered Code Documentation with Streamlit & Llama-Index

GitDoc is a Streamlit application that leverages the power of GPT models to automatically generate documentation for your code. With GitDoc, you can streamline your documentation process, ensuring that your codebase is always accompanied by up-to-date and comprehensive explanations.

## Features

- **AI-Powered Documentation**: Utilize state-of-the-art large langugage models to create initial drafts or enhance existing documentation.
- **Support for Multiple Languages**: GitDoc can generate documentation for a variety of programming languages.
- **Interactive UI**: Easy-to-use web interface built with Streamlit for a smooth user experience.
- **Customization Options**: Tailor the documentation style for techical or non-technical audiences.
- **Export Functionality**: Export your generated documentation to PDF.

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

4. **Run the Streamlit App**

   ```bash
   streamlit run app.py
   ```

   The app should now be running and accessible through your web browser at the address indicated by Streamlit (typically `localhost:8501`).
