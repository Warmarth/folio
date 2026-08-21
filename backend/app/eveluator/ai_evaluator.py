import os
from google import genai
from dotenv import load_dotenv
import json


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options={
        "api_version": "v1"
    })


def evaluator_ai(param):
    prompt = f"""
    You are an exercise evaluator.

    Evaluate the student's answer against the exercise.

    Exercise title:{param["title"]}
    Exercise description:{param["description"]}
    Student's answer:{param["answer"]}

    Return ONLY valid JSON in this exact format:

    {{
        "feedback": "short explanation of the result",
        "passed": true
    }}

    Rules:
    - "passed" must be either true or false.
    - Give clear and concise feedback.
    - Do not include markdown.
    """
    print("GEMINI KEY:", "SET" if os.getenv("GEMINI_API_KEY") else "NOT SET")
    interaction = client.interactions.create(
        model="gemini-3.7-flash",
        input=prompt
    )

    result =  json.loads(interaction.output_text)
    return result
