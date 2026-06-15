import sys

import mistralai
import mistralai.client
from datetime import datetime


from pathlib import Path

script_dir = Path(__file__).resolve().parent

try:
    with open(script_dir / "api_key.txt", "r") as f:
        API_KEY = f.read().strip()
except Exception as e:
    print("There should be a file named api_key.txt with your API key in it")
    print("Error reading API key from file: ", e)

prompt = """I wrote some personal notes on markdown, they are missing the latex symbols that makes math rendering nice, I would like you to add those to my text. When doing so, do not change what I wrote, even if you think it's bad spelled, or it makes no sense. Answer with only the markdown, do not add any comment, and do not add any text that is not in the markdown. Use align whenever possible. Try to catch all the numbers, math expresions, that needs latex symbols to be properly rendered. Don't' put a space before and after the dollar signs, I mean this $a$, not this $ a $. You sometimes miss isolated integers like 0, or the implies arrows like =>.
"""


def main():
    print("Paste your markdown, then press Ctrl-D when finished:")
    input_content = sys.stdin.read()
    print("Processing your markdown with Mistral...")
    client = mistralai.client.Mistral(api_key=API_KEY)
    response = client.chat.complete(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": prompt + input_content}],
    )
    if response.choices[0].message is not None:
        mistral_answer = response.choices[0].message.content
        file_name = "output" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".md"

        with open(f"{script_dir}/input/{file_name}", mode="w") as f:
            f.write(input_content)
        print(f"Input markdown written on {file_name}")

        with open(f"{script_dir}/output/{file_name}", mode="w") as f:
            f.write(str(mistral_answer))
        print("Mistral answer")
        print(mistral_answer)
        print(f"Mistral answer written on {file_name}")


if __name__ == "__main__":
    main()
