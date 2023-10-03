from music21 import *
import os
import glob
from music21 import *
import subprocess
import json


def transpose_midi_to_c_major(input_midi_path, output_midi_path):
    """
    Transpose a MIDI file to the key of C Major.

    Parameters:
    input_midi_path (str): Path to the input MIDI file.
    output_midi_path (str): Path to save the output transposed MIDI file.
    """
    try:
        # Parse the MIDI file
        score = converter.parse(input_midi_path)

        # Get the key of the score
        key = score.analyze("key")
        print(f"Original Key: {key}")

        # Calculate the interval between the original key and C Major
        transposition_interval = interval.Interval(key.tonic, pitch.Pitch("C"))

        # Transpose the score to C Major
        transposed_score = score.transpose(transposition_interval)

        # Write the transposed score to MIDI format
        transposed_score.write("midi", fp=output_midi_path)

        # Print the path to the transposed MIDI file
        print(f"Transposed score written to: {output_midi_path}")

    except Exception as e:
        print(f"An error occurred: {e}")


def midi_to_abc(midi_file_path, abc_file_path):
    """
    Convert a MIDI file to ABC format using the midi2abc tool.

    Parameters:
    midi_file_path (str): Path to the input MIDI file.
    abc_file_path (str): Path to the output ABC file.
    """
    try:
        # Run midi2abc command
        subprocess.run(
            ["midi2abc", midi_file_path, "-o", abc_file_path], check=True
        )
        print(f"ABC file successfully created at {abc_file_path}")
    except subprocess.CalledProcessError:
        print("Error occurred while converting MIDI to ABC")
    except FileNotFoundError:
        print(
            "midi2abc not found. Please ensure it's installed and available in your system's PATH"
        )


# Usage example
input_midi_file = "../data/external/ps01_01_C_Major.mid"
output_abc_fie = "../data/external/ps01_01_C_Major.abc"
midi_to_abc(input_midi_file, output_abc_fie)


def abc_newline_to_dollar(abc_file_path, output_file_path):
    """
    Replace newline characters in an ABC file with the $ sign.

    Parameters:
    abc_file_path (str): Path to the input ABC file.
    output_file_path (str): Path to save the output text file.
    """
    try:
        # Read the content of the ABC file
        with open(abc_file_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Handle lines that end with a backslash
        content = content.replace("\\\n", " ")

        # Replace newline characters with $
        modified_content = content.replace("\n", " $ ")

        # Write the modified content to the output file
        with open(output_file_path, "w", encoding="utf-8") as output_file:
            output_file.write(modified_content)

        print(f"Modified content written to: {output_file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")


def abc_to_json(abc_file_path, json_file_path):
    """
    Read ABC content from a text file and create a JSON object.

    Parameters:
    abc_file_path (str): Path to the input text file containing ABC content.
    json_file_path (str): Path to save the output JSON file.
    """
    try:
        # Read the content of the text file
        with open(abc_file_path, "r", encoding="utf-8") as file:
            abc_content = file.read()

        # Create JSON object
        json_object = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a music AI that generates melodies in the ABC format.",
                },
                {"role": "user", "content": "Generate a short melody for me."},
                {
                    "role": "assistant",
                    "content": f"ABC notation: {abc_content}",
                },
            ]
        }

        # Write the JSON object to the output file
        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json.dump(json_object, json_file, ensure_ascii=False, indent=4)

        print(f"JSON object written to: {json_file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")


def process_all_midi_files(root_dir, interim_dir):
    """
    Process all MIDI files in the specified directory and its subdirectories.

    Parameters:
    root_dir (str): The root directory containing the MIDI files.
    interim_dir (str): Directory to save all interim files generated in the process.
    """
    # Create interim directory if it doesn't exist
    if not os.path.exists(interim_dir):
        os.makedirs(interim_dir)

    # Iterate over all MIDI files in the specified directory and its subdirectories
    for midi_file in glob.glob(
        os.path.join(root_dir, "**/*.mid"), recursive=True
    ):
        print(f"Processing {midi_file}...")

        # Define paths for interim files
        base_name = os.path.splitext(os.path.basename(midi_file))[0]
        transposed_midi_path = os.path.join(
            interim_dir, f"{base_name}_C_Major.mid"
        )
        abc_path = os.path.join(interim_dir, f"{base_name}_C_Major.abc")
        txt_path = os.path.join(interim_dir, f"{base_name}_C_Major.txt")
        json_path = os.path.join(interim_dir, f"{base_name}_C_Major.json")

        # Apply your functions to each MIDI file
        transpose_midi_to_c_major(midi_file, transposed_midi_path)
        midi_to_abc(transposed_midi_path, abc_path)
        abc_newline_to_dollar(abc_path, txt_path)
        abc_to_json(txt_path, json_path)


def create_final_json(interim_dir, final_json_path):
    """
    Combine all JSON objects in the interim directory into a single JSON file.

    Parameters:
    interim_dir (str): Directory containing the interim JSON files.
    final_json_path (str): Path to save the final combined JSON file.
    """
    data_points = []

    # Iterate over all JSON files in the interim directory
    for json_file in glob.glob(os.path.join(interim_dir, "*.json")):
        with open(json_file, "r", encoding="utf-8") as file:
            data_point = json.load(file)
            data_points.append(data_point)

    # Write all data points to the final JSON file
    with open(final_json_path, "w", encoding="utf-8") as final_json_file:
        json.dump(data_points, final_json_file, ensure_ascii=False, indent=4)


# Usage example
root_directory = "data/external"
interim_directory = "data/interim"
final_json_file_path = "data/interim/final_dataset.json"

process_all_midi_files(root_directory, interim_directory)
create_final_json(interim_directory, final_json_file_path)
