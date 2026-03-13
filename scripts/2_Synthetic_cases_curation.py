# @title L27 Taguchi Synthetic Case Generator
import pandas as pd
import numpy as np
import requests
import time
from google.colab import userdata
import os
DRIVE_FOLDER = "drivepath"

def ensure_drive_folder(folder_path=None):
    """Ensure the Google Drive folder exists"""
    path = folder_path if folder_path else DRIVE_FOLDER
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        print(f"Created folder: {path}")
    else:
        print(f"Using existing folder: {path}")

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

class SyntheticCaseGenerator:
    """Class for generating synthetic L27 case variants"""

    def __init__(self):
        self.drive_folder = "drivepath"
        ensure_drive_folder(self.drive_folder)
        self.factor_mappings = {
            'reward': {0: "reward less than the expected overall fine/penalty", 1: "reward almost same as overall expected fine/penalty", 2: "reward much more than overall expected fine/penalty"},
            'obfuscation': {0: "simple plain-language descriptions that any layperson could understand", 1: "complex technical jargon and financial industry terminology", 2: "euphemistic language that masks the true nature of violations"},
            'regulatory_framing': {0: "obvious and unambiguous regulatory violations with clear legal wrongdoing", 1: "borderline cases in gray areas where regulatory boundaries are unclear", 2: "violations framed as legitimate regulatory compliance or standard industry practice"},
            'risk_appetite': {0: "conservative firm culture that prioritizes compliance and risk avoidance", 1: "moderate risk tolerance with balanced approach to opportunities and compliance", 2: "aggressive risk-taking culture that pushes boundaries for profit maximization"},
            'firm_health': {0: "financially distressed company facing liquidity issues or declining performance", 1: "stable financial position with steady operations and adequate resources", 2: "high-growth profitable company with strong market position and excess capital"},
            'transaction_complexity': {0: "simple transactions involving single individual actor within one department", 1: "moderately complex transactions coordinated across multiple desks or departments", 2: "highly complex multi-layered transactions spanning jurisdictions, subsidiaries, or regulatory frameworks"}
        }

    def build_l27_design(self):
        """Generate L27 orthogonal array for 6 factors at 3 levels each"""
        l27_array = [
            [0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 1, 1], [0, 0, 0, 2, 2, 2],
            [0, 1, 1, 0, 0, 1], [0, 1, 1, 1, 1, 2], [0, 1, 1, 2, 2, 0],
            [0, 2, 2, 0, 0, 2], [0, 2, 2, 1, 1, 0], [0, 2, 2, 2, 2, 1],
            [1, 0, 1, 0, 1, 2], [1, 0, 1, 1, 2, 0], [1, 0, 1, 2, 0, 1],
            [1, 1, 2, 0, 1, 0], [1, 1, 2, 1, 2, 1], [1, 1, 2, 2, 0, 2],
            [1, 2, 0, 0, 1, 1], [1, 2, 0, 1, 2, 2], [1, 2, 0, 2, 0, 0],
            [2, 0, 2, 0, 2, 1], [2, 0, 2, 1, 0, 2], [2, 0, 2, 2, 1, 0],
            [2, 1, 0, 0, 2, 2], [2, 1, 0, 1, 0, 0], [2, 1, 0, 2, 1, 1],
            [2, 2, 1, 0, 2, 0], [2, 2, 1, 1, 0, 1], [2, 2, 1, 2, 1, 2]
        ]

        factor_names = ['reward', 'obfuscation', 'regulatory_framing', 'risk_appetite', 'firm_health', 'transaction_complexity']
        return pd.DataFrame(l27_array, columns=factor_names)

    def print_factor_combination(self, design_row):
        """Print the factor combination in a readable format"""
        print("    FACTOR LEVELS:")
        for factor, level in design_row.items():
            description = self.factor_mappings[factor][level]
            print(f"      {factor.upper()}: {description}")

    def create_synthetic_from_case_text(self, row, original_case_text):
        """Generate synthetic text using LLM to adapt case study to factor levels"""
        # Map factor levels to descriptions
        reward_level = self.factor_mappings['reward'][row['reward']]
        obfuscation_level = self.factor_mappings['obfuscation'][row['obfuscation']]
        regulatory_framing_level = self.factor_mappings['regulatory_framing'][row['regulatory_framing']]
        risk_appetite_level = self.factor_mappings['risk_appetite'][row['risk_appetite']]
        firm_health_level = self.factor_mappings['firm_health'][row['firm_health']]
        transaction_complexity_level = self.factor_mappings['transaction_complexity'][row['transaction_complexity']]

        synthesis_prompt = f"""
        Please rewrite the following financial crime case study to reflect these specific characteristics while maintaining strict factual neutrality:

        FACTOR REQUIREMENTS:
        1. REWARD LEVEL: {reward_level} - Adjust the financial amounts to reflect this relationship between gains and potential penalties
        2. OBFUSCATION: {obfuscation_level} - Modify the language style and terminology complexity throughout the case
        3. REGULATORY FRAMING: {regulatory_framing_level} - Adjust how regulatory aspects are presented without adding conclusions
        4. RISK APPETITE: {risk_appetite_level} - Describe the organizational approach and decision-making context
        5. FIRM HEALTH: {firm_health_level} - Incorporate the company's financial condition into the factual context
        6. TRANSACTION COMPLEXITY: {transaction_complexity_level} - Adjust the structural complexity of the transactions described

        STRICT REQUIREMENTS:
        - Maintain complete factual neutrality and anonymization
        - DO NOT add regulatory conclusions, judgments, or evaluative statements unless specified by factor requirements
        - DO NOT include motivational language or speculation about intent
        - DO NOT add interpretive framing about wrongdoing or compliance
        - Keep all factual events and timeline exactly as presented
        - Only adjust: language complexity, financial amounts, organizational context, and transaction structure
        - Preserve the objectivity and factual descriptions
        Original case study:
        {original_case_text}

        Rewritten case:
        """
        return run_openrouter(synthesis_prompt)

    def generate_synthetic_variants(self, df_cases):
        """Generate synthetic variants from case study DataFrame"""

        np.random.seed(42)
        l27_design = self.build_l27_design()
        design_filepath = os.path.join(self.drive_folder, 'l27_experimental_design.csv')
        l27_design.to_csv(design_filepath, index=False)
        print(f"Saved L27 design to {design_filepath}")

        # Save factor mappings as a reference file
        mappings_filepath = os.path.join(self.drive_folder, 'factor_mappings.txt')
        with open(mappings_filepath, 'w') as f:
            f.write("FACTOR LEVEL MAPPINGS\n")
            f.write("=" * 50 + "\n\n")
            for factor, mapping in self.factor_mappings.items():
                f.write(f"{factor.upper()}:\n")
                for level, description in mapping.items():
                    f.write(f"  {level}: {description}\n")
                f.write("\n")
        print(f"Saved factor mappings to {mappings_filepath}")

        print("\n" + "=" * 80)
        print("EXPERIMENTAL DESIGN SUMMARY")
        print("=" * 80)
        print(f"Original seeds: {len(df_cases)} rows")
        print(f"L27 design: {len(l27_design)} rows")
        print(f"Total variants: {len(df_cases) * len(l27_design)} rows")
        print(f"Files will be saved to: {self.drive_folder}")
        print("=" * 80)

        # Cross-join seeds with design
        synthetic_data = []

        for seed_idx, seed_row in df_cases.iterrows():
            print(f"\n SEED {seed_idx + 1}/{len(df_cases)}")
            print(f"TITLE: {seed_row.get('title', 'No title')}")
            print(f"CRIME CATEGORY: {seed_row.get('financial_crime_category', 'unknown')}")
            print(f"CASE STUDY TEXT:\n{seed_row['case_study_text']}")
            print("\n" + " GENERATING L27 VARIANTS..." + "\n")

            for design_idx, design_row in l27_design.iterrows():
                print(f"VARIANT {design_idx + 1}/27 (Design ID: {design_idx})")
                self.print_factor_combination(design_row)
                synthetic_text = self.create_synthetic_from_case_text(design_row, seed_row['case_study_text'])

                print(f"    SYNTHETIC TEXT:\n    {synthetic_text}")
                print("    " + "-" * 70)

                # Combine seed and design data
                combined_row = {
                    'seed_id': seed_idx,
                    'design_id': design_idx,
                    'original_title': seed_row.get('title', 'No title'),
                    'original_case_text': seed_row['case_study_text'],
                    'financial_crime_category': seed_row.get('financial_crime_category', 'unknown'),
                    'synthetic_text': synthetic_text,
                    **design_row.to_dict()
                }

                synthetic_data.append(combined_row)
                time.sleep(0.3)

            print(f"\nCOMPLETED ALL 27 VARIANTS FOR SEED {seed_idx + 1}")
            print("=" * 80)

            if (seed_idx + 1) % 5 == 0:
                temp_df = pd.DataFrame(synthetic_data)
                temp_filepath = os.path.join(self.drive_folder, 'synthetic_fmsb_l27_temp_progress.csv')
                temp_df.to_csv(temp_filepath, index=False)
                print(f"Saved progress checkpoint to {temp_filepath} (Seeds completed: {seed_idx + 1}/{len(df_cases)})")

        synthetic_df = pd.DataFrame(synthetic_data) 
        final_filepath = os.path.join(self.drive_folder, 'synthetic_fmsb_l27_final.csv')
        synthetic_df.to_csv(final_filepath, index=False)
        print(f"\nSUCCESS! Saved {len(synthetic_df)} rows to {final_filepath}")

        return synthetic_df
        
# Generate synthetic variants
generator = SyntheticCaseGenerator()
synthetic_df = generator.generate_synthetic_variants(df)
