import os
# from google import genai
from groq import Groq
from dotenv import load_dotenv
import json

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"),)

def evaluator_ai(param):
    prompt = f"""
You are an exercise evaluator.

Evaluate the user's answer against the exercise.
Exercise title: 
{param["title"]}

Exercise description:
{param["description"]}

User's answer: 
{param["answer"]}
Return ONLY valid JSON in this exact format:

{{
    "passed": true,
    "feedback": "Brief explanation of why the answer passed or failed."
}}

Rules:
- "passed" must be true or false.
- Be fair when evaluating the answer.
- The answer does not need to use the exact wording of the exercise description.
- If the answer demonstrates the required understanding, pass it.
"""
    print("GEMINI KEY:", "SET" if os.getenv("GROQ_API_KEY") else "NOT SET")
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_completion_tokens=500,
        response_format={
            "type": "json_object"
        }
    )
    
    content = completion.choices[0].message.content

    return json.loads(content)


# print(evaluator_ai({
#     'title':"basic print in python",
#     'description':"print a basic hello world",
#     "answer":"print('hello world')"
# }))