import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download required NLTK resources (safe to call every time — skips if already downloaded)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('omw-1.4', quiet=True)

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()


def clean_text(text):
    """
    Cleans a single piece of email text:
    - Lowercases
    - Masks URLs and emails with placeholder tokens
    - Removes non-alphabetic characters
    - Removes stopwords and short tokens
    - Lemmatizes remaining words
    Always returns a string (never NaN/float), even for empty/invalid input.
    """
    if pd.isna(text) or text is None:
        return ""

    text = str(text).lower()

    # Mask URLs and emails before stripping punctuation, so we don't lose the signal entirely
    text = re.sub(r'http\S+|www\S+', ' URLTOKEN ', text)
    text = re.sub(r'\S+@\S+', ' EMAILTOKEN ', text)

    # Remove anything that isn't a letter or whitespace
    text = re.sub(r'[^a-z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    if not text:
        return ""

    tokens = text.split()
    tokens = [
        lemmatizer.lemmatize(w)
        for w in tokens
        if w not in stop_words and len(w) > 2
    ]

    cleaned = ' '.join(tokens)
    return cleaned if cleaned else ""


def load_and_clean(path):
    """
    Loads the combined dataset CSV, cleans text, and removes any rows
    that end up with empty/invalid clean_text after processing.
    """
    df = pd.read_csv(path)

    # Drop rows with no label — useless for training
    df = df.dropna(subset=['label'])

    # Ensure subject/body columns exist even if missing from source data
    if 'subject' not in df.columns:
        df['subject'] = ''
    if 'body' not in df.columns:
        df['body'] = ''

    df['subject'] = df['subject'].fillna('')
    df['body'] = df['body'].fillna('')

    # Combine subject + body into one text field
    df['text'] = df['subject'].astype(str) + " " + df['body'].astype(str)

    # Apply cleaning
    df['clean_text'] = df['text'].apply(clean_text)

    # Safety net: force any stray NaN to empty string, then drop empty rows
    df['clean_text'] = df['clean_text'].fillna('').astype(str)
    df = df[df['clean_text'].str.strip() != '']

    # Remove duplicate cleaned emails
    df = df.drop_duplicates(subset=['clean_text'])

    # Reset index after filtering/dropping rows
    df = df.reset_index(drop=True)

    return df


if __name__ == "__main__":
    input_path = "data/raw/combined_dataset.csv"
    output_path = "data/processed/cleaned_emails.csv"

    print(f"Loading and cleaning dataset from {input_path} ...")
    df = load_and_clean(input_path)

    print("\nFinal shape:", df.shape)
    print("\nLabel distribution:")
    print(df['label'].value_counts())

    nan_count = df['clean_text'].isna().sum()
    empty_count = (df['clean_text'].str.strip() == '').sum()
    print(f"\nSanity check -> NaN in clean_text: {nan_count}, Empty strings: {empty_count}")

    df.to_csv(output_path, index=False)
    print(f"\nSaved cleaned data to {output_path}")