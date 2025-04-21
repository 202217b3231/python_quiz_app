import json
import re

def extract_data_from_text(filepath):
    """
    Extracts question, options, answer, and explanation from a text file and returns them as a list of dictionaries.

    Args:
        filepath: The path to the text file.

    Returns:
        A list of dictionaries, where each dictionary represents a question and its associated data.
    """

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return []
    except UnicodeDecodeError:
        print(f"Error: Unable to decode file as UTF-8 at {filepath}. Please ensure the file is encoded in UTF-8.")
        return []
    questions_data = []
    question_blocks = re.split(r'(?=NEW QUESTION \d+)', text)  # Split into question blocks based on "NEW QUESTION"
    question_counter = 1 #Initialize question counter

    for block in question_blocks:
        block = block.strip()
        if not block:
            continue

        question_match = re.search(r'NEW QUESTION \d+\s*-\s*\((.+?)\)\s*(.+?)(?=[A-Z]\.)', block, re.DOTALL)
        if not question_match:
          continue
        
        # question_number = question_match.group(1) # remove question number extraction
        topic = question_match.group(1)
        question_text = question_match.group(2).strip()

        options = {}
        option_matches = re.findall(r'([A-D])\.\s*(.+?)(?=(?:\s+[A-Z]\.\s+|\s+Answer:|$))', block, re.DOTALL) # find options.
        for option_match in option_matches:
            option_key = option_match[0]
            option_value = option_match[1].strip()
            options[option_key] = option_value

        answer_match = re.search(r'Answer:\s*([A-D])', block)
        answer = answer_match.group(1) if answer_match else None

        explanation_match = re.search(r'Explanation:\s*\n*(.+)', block, re.DOTALL)
        explanation = explanation_match.group(1).strip() if explanation_match else None

        questions_data.append({
            "question_number": question_counter, #add new question number
          
            "question": question_text,
            "options": options,
            "answer": answer,
            "explanation": explanation,
        })
        question_counter+=1 # increment question counter

    return questions_data


def save_to_json(data, output_filepath):
    """
    Saves the provided data to a JSON file.

    Args:
        data: The data to save (list of dictionaries).
        output_filepath: The path to the output JSON file.
    """
    with open(output_filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


# Example usage:
filepath = "cdl2.txt"  # Replace with your file path
output_filepath = "cdl_questions.json"  # Replace with your desired output path

questions_data = extract_data_from_text(filepath)
save_to_json(questions_data, output_filepath)

print(f"Successfully extracted {len(questions_data)} questions and saved them to {output_filepath}")

