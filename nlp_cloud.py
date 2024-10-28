# import requests

# url = "https://api.nlpcloud.io/v1/{model}/"
# headers = {
#     "Authorization": "8e970b182096212afe6ab64ff193a0c21fb952bf",
#     "Content-Type": "application/json"
# }
# payload = {
#     "text": "Hi tell me about yourself"
# }

# response = requests.post(url, headers=headers, json=payload)
# print(response.json())



from langchain.chains import LLMChain
from langchain_community.llms import NLPCloud
from langchain_core.prompts import PromptTemplate
import os

os.environ["NLPCLOUD_API_KEY"] = "8e970b182096212afe6ab64ff193a0c21fb952bf"




template = """Question: {question}

Answer: Let's think step by step."""

prompt = PromptTemplate.from_template(template)

llm = NLPCloud()

llm_chain = LLMChain(prompt=prompt, llm=llm)

question = "What NFL team won the Super Bowl in the year Justin Beiber was born?"

result = llm_chain.run(question)

print(result)