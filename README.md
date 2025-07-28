# AI-Powered Stock Recommendation Analyzer

## 📝 Project Objective

This project is a suite of Python-based command-line tools that form a complete pipeline for analyzing stock recommendations from financial news videos. The system automates the process of downloading video audio, transcribing it, using AI to extract actionable data, and backtesting the performance of the recommendations against historical market data.

This project is built entirely as a backend solution with no frontend interface.

---

## 🚀 The Workflow

The project is divided into a four-step, modular pipeline:

###  Tool 1: Audio Downloader (`1_download_audio`)
- **Input:** A YouTube URL.
- **Action:** Uses `yt-dlp` to download the audio-only stream from the video.
- **Output:** An `.mp3` file named with the video's publish date (e.g., `20250725_VideoTitle.mp3`).

### Tool 2: Fast Transcriber (`2_transcribe_audio`)
- **Input:** The path to the downloaded `.mp3` file.
- **Action:** Uses the Google Gemini API to perform a fast and direct translation of the audio into raw English text.
- **Output:** A raw `.txt` transcript file.

### Tool 3: Intelligent Extractor (`3_analyze_transcript`)
- **Input:** The path to the raw `.txt` transcript.
- **Action:** Performs a two-step AI process:
    1.  **Cleans & Edits:** Sends the raw text to the Gemini API to be professionally edited, removing filler words and correcting grammar.
    2.  **Deep Research & Extraction:** Sends the clean text to the Gemini API with a powerful prompt, instructing it to act as a senior financial analyst. It extracts key data points, researches the correct stock tickers, and finds verification sources.
- **Output:** A high-quality `.xlsx` Excel file containing structured recommendation data.

### Tool 4: Performance Analyzer (`4_performance_analyzer`)
- **Input:** The path to the high-quality `.xlsx` file.
- **Action:**
    - For each recommendation, it intelligently finds the stock ticker using Yahoo Finance's search API.
    - It downloads historical price data using `yfinance`.
    - It backtests the recommendation, calculating if the target or stop loss was hit, the final profit/loss, and prices at 2, 4, and 6-week intervals.
    - It calculates an overall accuracy score for each analyst.
- **Output:** A final `Stock_Performance_Report.xlsx` file with a comprehensive analysis of every recommendation.

---

## 🛠️ Technology Stack

- **Language:** Python 3
- **Audio/Video:** `yt-dlp`
- **AI / NLP:** Google Gemini API (`google-generativeai`)
- **Data Handling:** `pandas`
- **Financial Data:** `yfinance`
- **HTTP Requests:** `requests`

---

## ⚙️ Setup & Usage

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git)
    cd YOUR_REPOSITORY_NAME
    ```
2.  **Set up your environment:**
    - Ensure you have Python 3 installed.
    - Install the required libraries for each tool by navigating into its folder and running `pip install -r requirements.txt`. (Note: It's recommended to create a single `requirements.txt` in the root folder for simplicity).
    - Set your Google API Key as an environment variable:
      ```bash
      # On Windows
      setx GOOGLE_API_KEY "YOUR_API_KEY_HERE"

      # On macOS/Linux
      export GOOGLE_API_KEY="YOUR_API_KEY_HERE"
      ```
3.  **Run the pipeline:** Execute the scripts in each folder in sequential order (1 -> 2 -> 3 -> 4), providing the output of the previous step as the input for the next.

---

## ⚠️ Disclaimer

This project is for educational purposes only. The financial data and analysis provided are not investment advice. Trading in financial markets involves risk.