import pandas as pd

from services.save_post import save_post


def load_enriched_posts(csv_path):

    df = pd.read_csv(csv_path)

    for _, row in df.iterrows():

        save_post(row.to_dict())

    print(f"{len(df)} posts loaded into MongoDB.")