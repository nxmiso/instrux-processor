import os
import json
import time
import openai

openai.api_key = os.getenv("OPENAI_KEY")

def inference(prompt, system="You are a helpful assistant. Respond with only what the user asks for and nothing more in JSON format.", model="gpt-4o"):
    for i in range(3):
        try:
            response = openai.chat.completions.create(
                model=model,
                response_format={"type": "json_object"},
                messages=[{
                    "role": "system",
                    "content": system
                }, {
                    "role": "user",
                    "content": prompt
                }]
            )
            # return json.loads(response["choices"][0]["message"]["content"])
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print("Failed to generate response from GPT on attempt:", i+1)
            print(e)
            if i == 2:
                print("Failed to generate response from GPT after 3 attempts")
                raise e
            print("Trying again in 60 seconds...")
            time.sleep(60)