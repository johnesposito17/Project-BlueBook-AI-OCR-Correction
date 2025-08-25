import pandas as pd

INPUT_FILE = "/Users/johnesposito/Documents/GitHub/Project-BlueBook-AI-OCR-Correction/OCR Evaluation/Results/OCR_vs_Human_CER.csv"

df = pd.read_csv(INPUT_FILE)
    
cer_values = df["CER"].dropna()
    
mean_cer = cer_values.mean()
std_cer = cer_values.std()
    
print(f"Average CER: {mean_cer:.6f}")
print(f"Standard Deviation CER: {std_cer:.6f}")

