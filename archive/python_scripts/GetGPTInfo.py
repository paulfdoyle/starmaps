import json
import os
import openai
from openai import OpenAI
from openai.types.chat.chat_completion import Choice as CompletionChoice
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
print("Environment loaded")

# Retrieve the OpenAI API key from the environment
api_key = os.getenv("OPENAI_API_KEY")
print(api_key)

if api_key is None:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

# Set the API key for the openai client
openai.api_key = api_key

# Setting the default system message for the LLM API
DEFAULT_SYSTEM_MESSAGE = ('You are a scientist at a planetarium, who excels at educating the general '
                          'public on astronomy. Give the following facts: the star name and size relative to the Sun, '
                          'the distance from Earth, and one interesting fact which the public might find interesting. '
                          'Users will give you the proper name of a star and a HIP or HD reference, and you will '
                          'provide them with this information. Keep your answers under 50 words, '
                          'don’t prompt for more questions.')

@dataclass
class LLMAPIResponse:
    system_message: str
    query: str
    response: CompletionChoice

    def __repr__(self):
        return (f"System Message:\r\n"
                f"===============\r\n{self.system_message}"
                "\r\n\r\n"
                f"Query:"
                f"===============\r\n{self.query}"
                "\r\n\r\n"
                f"Response:"
                f"===============\r\n{self.response}"
                )


class LLMAPIClient:
    _client: openai.Client = None
    _system_message: str = None

    def __init__(self):
        self._client = OpenAI()
        self._system_message = DEFAULT_SYSTEM_MESSAGE

    def get_info(self, proper_name: str) -> str:
        completion = self._client.chat.completions.create(
          model="gpt-4o-mini",
          messages=[
            {"role": "system", "content": self._system_message},
            {"role": "user", "content": proper_name}
          ]
        )
        return completion.choices[0].message.content
    

client = LLMAPIClient()
print(os.environ.get('OPENAI_API_KEY'))


# Load the JSON file from the specified path
json_file_path = '../datasets/merged_star_exo_data.json'  # Updated path to your JSON file
with open(json_file_path, 'r') as file:
    stars_data = json.load(file)

# Loop through each star in the JSON file
for star in stars_data:
    proper_name = star['proper']
    hip_id = star['hip']
    hd_ref = star['hd']

    # Create a string that includes the proper name, HIP ID, and HD reference
    star_info = f"Star: {proper_name}, HIP ID: {hip_id}, HD Reference: {hd_ref}"

    # Call the get_info method with the combined star information
    response = client.get_info(star_info)
    print(f"Response for {star_info}:\n{response}\n")
