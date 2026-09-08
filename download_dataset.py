from datasets import load_dataset
import pandas as pd
import os


os.makedirs("data/raw", exist_ok=True)

print("Downloading zefang-liu/phishing-email-dataset from Hugging Face...")
ds = load_dataset("zefang-liu/phishing-email-dataset")


df = ds['train'].to_pandas()

print("\nDataset shape:", df.shape)
print("\nColumns:", df.columns.tolist())
print("\nFirst 5 rows:")
print(df.head())

print("\nLabel value counts:")
label_col = [c for c in df.columns if 'type' in c.lower() or 'label' in c.lower()][0]
print(df[label_col].value_counts())


df.to_csv("data/raw/zefang_phishing_email.csv", index=False)
print("\nSaved to data/raw/zefang_phishing_email.csv")