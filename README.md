# Streamlit Development Application

This is a [Streamlit](https://streamlit.io/) application showcasing an interactive map to help easilly find touristic activities accross a certain region. 
The virtual assistant modeule is a [RAG](https://www.pinecone.io/learn/retrieval-augmented-generation/) application using a Pinecone index previously created to serve the OpenAI API with content about each place.

## Table of Contents

- [Getting Started](#getting-started)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Getting Started

Install streamlit as explained on the [official website](https://docs.streamlit.io/library/get-started/installation).

## Prerequisites

- Your favorite IDE or text editor
- Python 3.8 - Python 3.11
- PIP
- Pinecone index previously created
- OpenAI API

## Installation

```bash
# Clone the repository
git clone https://github.com/madelinap/lapetitefleur.git

# Change the directory
cd lapetitefleur

# Create a virtual environment (optional but recommended)
python -m venv venv

# Activate the virtual environment (Windows)
venv\Scripts\activate

# Activate the virtual environment (macOS and Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

```
## Usage

```bash
streamlit run aplapetitefleur.py
```

## Contributing

We welcome contributions from the community. If you'd like to contribute to this project, please follow these guidelines:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Create a pull request with a clear description of the changes and their purpose.


## License
This project is licensed under the lapetitefleur License - see the LICENSE file for details.

