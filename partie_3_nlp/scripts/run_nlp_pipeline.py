import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


def run_step(script_name: str) -> None:
    script_path = BASE_DIR / "scripts" / script_name

    print("=" * 80)
    print(f"Exécution : {script_name}")
    print("=" * 80)

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=BASE_DIR,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"Erreur pendant l'étape : {script_name}")


if __name__ == "__main__":
    steps = [
        "01_validate_input.py",
        "02_sentiment_enrichment.py",
        "03_topic_modeling.py",
        "04_generate_aggregates.py",
        "05_generate_summary.py",
        "06_correlate_match_events.py"
        
    ]
    

    for step in steps:
        run_step(step)

    print("=" * 80)
    print("Pipeline NLP terminé avec succès.")
    print("=" * 80)