# @title Financial Crimes Cases Anonymizer
# Please not that all cases were manually cross-verified and further anonymized after running this version
import pandas as pd
import numpy as np
import requests
import time
from google.colab import userdata
import os

df = pd.read_csv("filepath/fmsb_report_raw_financial_crimes.csv")
DRIVE_FOLDER = "filepath"

def ensure_drive_folder():
    """Ensure the Google Drive folder exists"""
    if not os.path.exists(DRIVE_FOLDER):
        os.makedirs(DRIVE_FOLDER, exist_ok=True)
        print(f"Created folder: {DRIVE_FOLDER}")
    else:
        print(f"Using existing folder: {DRIVE_FOLDER}")

def run_openrouter(prompt, model="llm_model_name"):
    """Send request to OpenRouter API"""
    try:
        api_key = userdata.get('openrouterkey')
    except Exception as e:
        return f"Error accessing Colab secret: {str(e)}"

    if not api_key:
        return "OpenRouter API key not found in Colab secrets"

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

class CaseAnonymizer:
    """Class for anonymizing financial market abuse case texts"""

    def __init__(self):
        ensure_drive_folder()

    def anonymize_case_text(self, original_text):
        """Anonymize sensitive information in case text using LLM"""
        anonymization_prompt = f"""
        Please rewrite the following financial market scenario to focus solely on a neutral description of events. The goal is to anonymize all entities and eliminate any language that suggests a crime, wrongdoing, or regulatory breach. Only describe what happened factually, without implying legality, intent, or morality.

        RULES:
        1. Replace all person names with generic names (e.g., "Individual A", "Trader B").
        2. Replace all company and financial institution names with generic placeholders (e.g., "Company A", "Bank B").
        3. Preserve all financial amounts, dates, instruments, and technical steps exactly as stated.
        4. Remove all definitions, legal references, regulatory actions, or judgments (e.g., “this was illegal,” “this led to enforcement”).
        5. Remove any evaluative or suggestive language indicating misconduct or moral framing (e.g., “wrongfully”, “improper”, “abused”, “violated”).
        6. Only describe what happened in factual, chronological terms, without drawing conclusions.
        7. Do not add extra commentary or summaries.

        Original text:
        {original_text}

        Neutral, anonymized factual narrative:
        """


        return run_openrouter(anonymization_prompt)

    def anonymize_dataframe(self, df):
        """Add anonymized column to DataFrame with progress printing"""
        print("=" * 80)
        print("STARTING ANONYMIZATION PROCESS")
        print("=" * 80)
        df['anon_full_text'] = ""

        for idx, row in df.iterrows():
            print(f"\n--- Processing Row {idx + 1}/{len(df)} ---")
            print(f"ORIGINAL TEXT:\n{row['full_text'][:200]}...")

            # Anonymize the text
            anonymized_text = self.anonymize_case_text(row['full_text'])
            df.at[idx, 'anon_full_text'] = anonymized_text

            print(f"\nANONYMIZED TEXT:\n{anonymized_text}")
            print("-" * 60)
            time.sleep(0.5)

        print("\n" + "=" * 80)
        print("ANONYMIZATION COMPLETE!")
        print("=" * 80)

        # Save anonymized version
        anon_filepath = os.path.join(DRIVE_FOLDER, 'anonymized_fmsb_cases_test.csv')
        df.to_csv(anon_filepath, index=False)
        print(f"\n Saved anonymized cases to {anon_filepath}")
        return df

# Anonymize cases
anonymizer = CaseAnonymizer()
df_anonymized = anonymizer.anonymize_dataframe(df)

