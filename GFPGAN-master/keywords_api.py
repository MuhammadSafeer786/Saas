from openai import OpenAI
from secret_keys import openAI_key
import os
import cv2
import numpy as np
import ast
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/keyword', methods=['POST'])
def keyword_generator():
    url = request.form.get('url')
    if not url:
        return jsonify({"error": "No URL file provided"}), 400

    if url is None:
        return jsonify({'error': 'Invalid url'}), 500

    try:
        client = OpenAI(api_key=openAI_key)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Generate 20 keywords for this image. These should be descriptive e.g. fruit on the tree, unlike fruit, tree etc. please remember to output the list like python list of strings and no starting or trailing text e.g surely there is the list etc",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"{url}",
                            },
                        },
                    ],
                }
            ],
            max_tokens=300,
        )

        # print(response.choices[0])
        content = response.choices[0].message.content

        # Remove the code block markers and clean the content
        cleaned_content = content.strip('`').split('\n', 1)[1].strip()

        # Convert the cleaned content to a Python list
        python_list = ast.literal_eval(cleaned_content)

        return python_list
    except Exception as e:
        return jsonify({"error in try block": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)