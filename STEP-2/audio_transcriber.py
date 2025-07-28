import os
import google.generativeai as genai
import sys
import re

def configure_api():
    """
    Configures the Google Generative AI client using an API key
    from an environment variable. Exits if the key is not found.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set.")
        print("Please get your key from https://aistudio.google.com/app/apikey and set the variable.")
        sys.exit(1)
    genai.configure(api_key=api_key)

def transcribe_audio_to_english(audio_filepath: str):
    """
    Uploads, translates an audio file to pure English, and saves the
    transcription to a text file inside a 'transcripts' subfolder.
    """
    if not os.path.exists(audio_filepath):
        print(f"Error: The file was not found at the path: {audio_filepath}")
        return

    try:
        # --- Step 1: Define output folder and create if it doesn't exist ---
        output_folder = "transcripts"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            print(f"Created a new folder for output: '{output_folder}'")

        # --- Step 2: Extract the date to create the filename ---
        base_filename = os.path.basename(audio_filepath)
        match = re.match(r"^\d{8}", base_filename)
        
        if match:
            date_str = match.group(0)
            txt_filename = f"{date_str}_transcription.txt"
        else:
            print("Warning: Could not find date in filename. Using a generic name.")
            generic_name = os.path.splitext(base_filename)[0]
            txt_filename = f"{generic_name}_transcription.txt"
        
        # Combine folder and filename into a full path
        output_filepath = os.path.join(output_folder, txt_filename)

        # --- Step 3: Configure API and transcribe ---
        configure_api()
        
        print(f"\nUploading file for translation: {base_filename}...")
        audio_file = genai.upload_file(path=audio_filepath)
        print(f"File uploaded successfully.")

        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

        prompt = """
        You are a professional translator for a global financial news agency. Your only job is to translate audio from Indian languages (like Hindi or Hinglish) into perfect, professional English for an international audience.

        **CRITICAL INSTRUCTIONS:**
        1.  Your output MUST be in **100% PURE ENGLISH**.
        2.  You are strictly forbidden from using any Hindi or Hinglish words.
        3.  Translate the meaning and context accurately. Do not just transliterate.

        Failure to follow these rules is not an option. Produce a clean, professional, pure-English transcript of the following audio.
        """

        print("Sending translation request to the AI...")
        response = model.generate_content([prompt, audio_file])
        
        print(f"Deleting uploaded file from the service...")
        genai.delete_file(audio_file.name)

        if not response.parts:
             raise ValueError("The model returned an empty response. The audio might be silent or unsupported.")

        transcribed_text = response.text

        # --- Step 4: Save the transcription to the new path ---
        try:
            with open(output_filepath, 'w', encoding='utf-8') as f:
                f.write(transcribed_text)
            print(f"\n✅ Transcription successfully saved to: {output_filepath}")
        except IOError as e:
            print(f"\nError: Could not save the file. {e}")

        # --- Step 5: Print the transcription to the console ---
        print("\n--- PURE ENGLISH TRANSLATION ---")
        print(transcribed_text)
        print("--------------------------------\n")

    except Exception as e:
        print(f"\nAn error occurred during the translation process: {e}")

if __name__ == "__main__":
    file_path = input("Please enter the full path to the audio file you want to transcribe: ")
    
    if file_path:
        transcribe_audio_to_english(file_path.strip().strip('"'))
    else:
        print("No file path entered. Exiting.")
