import openai
import os

secret_key = "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"
org_id = "org-vfd8r9HMpyfo3R6jLWd9oEWE"

openai.organization = org_id
openai.api_key = secret_key
openai.Model.list()

response = openai.Completion.create(
  model="text-davinci-003",
  prompt="Say this is a test",
  max_tokens=7,
  temperature=0
)

print(response)

