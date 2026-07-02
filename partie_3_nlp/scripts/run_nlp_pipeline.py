from pathlib import Path
import subprocess
import sys


BASE_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = BASE_DIR / "scripts"


def run_script(script_name: str):
    script_path = SCRIPTS_DIR / script_name

    print("=" * 80)
    print(f"Exécution : {script_name}")
    print("=" * 80)

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=BASE_DIR
    )

    if result.returncode != 0:
        raise RuntimeError(f"Erreur pendant l'exécution de {script_name}")


if __name__ == "__main__":
    run_script("01_validate_input.py")
    run_script("02_sentiment_enrichment.py")
    run_script("03_topic_modeling.py")
    run_script("05_generate_summary.py")

    print("=" * 80)
    print("Pipeline NLP terminé avec succès.")
    print("Sorties produites pour la partie Data Analyst :")
    print("- outputs/posts_with_sentiment.csv")
    print("- outputs/enriched_posts.csv")
    print("- outputs/top_topics.csv")
    print("- outputs/trend_summary.csv")
    print("- outputs/trend_summary.txt")
    print("=" * 80)