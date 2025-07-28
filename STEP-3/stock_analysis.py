import os
import google.generativeai as genai
import sys
import re
import json
import pandas as pd
from datetime import datetime

def configure_api():
    """
    Configures the Google Generative AI client using an API key
    from an environment variable. Exits if the key is not found.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)
    genai.configure(api_key=api_key)

def analyze_and_export_to_excel(transcript_filepath: str):
    """
    Reads a transcript file, uses an AI to extract stock recommendations,
    and saves the data to a structured Excel file in a subfolder.
    """
    if not os.path.exists(transcript_filepath):
        print(f"Error: The file was not found at the path: {transcript_filepath}", file=sys.stderr)
        return

    # --- Step 1: Read the transcript file ---
    try:
        with open(transcript_filepath, 'r', encoding='utf-8') as f:
            transcript_text = f.read()
        print(f"Successfully read transcript: {os.path.basename(transcript_filepath)}")
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return

    # --- Step 2: Extract date from filename ---
    base_filename = os.path.basename(transcript_filepath)
    date_str = "Unknown_Date"
    match = re.match(r"^\d{8}", base_filename)
    if match:
        date_obj = datetime.strptime(match.group(0), "%Y%m%d")
        date_str = date_obj.strftime("%Y-%m-%d")

    # --- Step 3: Analyze the transcript with a specific JSON prompt ---
    try:
        configure_api()
        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

        # The prompt is updated to explicitly request "Buy", "Sell", or "Hold"
        prompt = f"""
        You are an expert financial data extraction bot. Your task is to analyze the following 
        transcript from the show 'Khiladi No. 1' and extract every stock recommendation into a structured format.

        The final output MUST be a valid JSON object. This object must contain a single key "recommendations", 
        which is a list of individual stock recommendation objects.

        Each object in the list MUST contain these exact keys:
        - "date": Use the value "{date_str}" for this key.
        - "analyst_name": The name of the person giving the recommendation.
        - "stock_name": The name of the stock being recommended.
        - "recommendation_type": The type of recommendation, either "Buy", "Sell", or "Hold". Use "Not Mentioned" if not explicitly stated.
        - "current_price": The price of the stock when the recommendation was made.
        - "stop_loss": The suggested stop loss price.
        - "target_price": The suggested target price.
        - "holding_period": The suggested holding period (e.g., "Positional", "Intraday", "Not Mentioned").

        **IMPORTANT RULES:**
        1. If any piece of information is not mentioned in the transcript for a specific recommendation, use the string "Not Mentioned" as the value.
        2. Do not make up any data. Only extract what is explicitly stated.
        3. If there are no recommendations, return an empty list for the "recommendations" key.
        4. Your entire response must only be the JSON object, with no other text or explanations.

        Here is the transcript to analyze:
        ---
        {transcript_text}
        ---
        """

        print("Sending transcript to AI for data extraction...")
        response = model.generate_content(prompt)
        
        # Clean the response to ensure it's a pure JSON string
        cleaned_json_text = response.text.strip().replace("```json", "").replace("```", "")
        
        print("Analysis received.")
        analysis_data = json.loads(cleaned_json_text)

        recommendations = analysis_data.get("recommendations", [])

        if not recommendations:
            print("No recommendations were found in the transcript.")
            return

        # --- Step 4: Convert data to a pandas DataFrame and save to Excel ---
        df = pd.DataFrame(recommendations)
        
        # Define the output folder and create it if it doesn't exist
        output_folder = "excel_reports"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            print(f"Created a new folder for reports: '{output_folder}'")

        # Define the output filename and the full path
        excel_filename = f"{date_str.replace('-', '')}_analysis.xlsx"
        full_excel_path = os.path.join(output_folder, excel_filename)
        
        df.to_excel(full_excel_path, index=False)
        
        print(f"\n✅ Success! Data has been saved to: {full_excel_path}")

    except json.JSONDecodeError:
        print("\nError: Failed to decode the AI's JSON response.", file=sys.stderr)
        print(f"Raw response was:\n{response.text}", file=sys.stderr)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    # The script now prompts the user for input instead of checking command-line arguments.
    print("This script analyzes a transcript for stock recommendations and exports them to an Excel file.")
    print("---------------------------------------------------------------------------------------------")
    
    file_path = input("Please enter the full path to the transcript file: ")
    
    # Clean the user-provided path
    analyze_and_export_to_excel(file_path.strip().strip('"'))