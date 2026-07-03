from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_PATH = BASE_DIR / "data" / "silver_posts.csv"


REQUIRED_COLUMNS = [
    "post_id",
    "source",
    "created_at",
    "match_name",
    "text_clean",
    "language",
    "language_group",
    "is_valid"
]


def validate_input(df: pd.DataFrame) -> None:
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Colonnes manquantes dans le fichier Silver : {missing_columns}")

    if df.empty:
        raise ValueError("Le fichier Silver est vide.")

    if df["post_id"].isna().any():
        raise ValueError("La colonne post_id contient des valeurs nulles.")

    if df["text_clean"].isna().any():
        raise ValueError("La colonne text_clean contient des valeurs nulles.")

    duplicated_posts = df["post_id"].duplicated().sum()
    if duplicated_posts > 0:
        raise ValueError(f"Il y a {duplicated_posts} doublons sur post_id.")

    empty_texts = df["text_clean"].astype(str).str.strip().eq("").sum()
    if empty_texts > 0:
        raise ValueError(f"Il y a {empty_texts} textes vides dans text_clean.")

    print("Validation Silver OK")
    print(f"Nombre total de lignes : {len(df)}")

    if "is_valid" in df.columns:
        valid_count = df[df["is_valid"].astype(str).str.lower() == "true"].shape[0]
        print(f"Nombre de posts valides : {valid_count}")

    print(f"Colonnes disponibles : {list(df.columns)}")


if __name__ == "__main__":
    df = pd.read_csv(INPUT_PATH)
    validate_input(df)