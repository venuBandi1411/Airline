import pandas as pd
from langchain.chains import LLMChain
from langchain_community.llms import NLPCloud
from langchain_core.prompts import PromptTemplate
import os

# Set your API key
os.environ["NLPCLOUD_API_KEY"] = "8e970b182096212afe6ab64ff193a0c21fb952bf"

# Load CSV data
csv_data = pd.read_csv('Airlinesdetails.csv')

# Define the template
template = """
We have the following traveler details:
{data}

Question: {question}

"""

prompt = PromptTemplate.from_template(template)

# Create the LLMChain
llm = NLPCloud()
llm_chain = LLMChain(prompt=prompt, llm=llm)

# Define the question
question = "Provide the traveler detail about Karthik"

# Function to search for traveler data in the CSV
def search_traveler_details(traveler_name, csv_data):
    # Assuming the traveler name is in a column named 'Name'
    traveler_data = csv_data[csv_data['first_name'].str.contains(traveler_name, case=False)]
    
    if not traveler_data.empty:
        # Convert traveler data to a string format to pass into the prompt
        data_string = traveler_data.to_string(index=False)
        return data_string
    else:
        return "No details found for the requested traveler."

# Search the CSV file for Karthik's details
traveler_data = search_traveler_details("Karthik", csv_data)

# Run the LLMChain with the traveler data and the question
if traveler_data != "No details found for the requested traveler.":
    result = llm_chain.run({"data": traveler_data, "question": question})
else:
    result = traveler_data

print(result)
