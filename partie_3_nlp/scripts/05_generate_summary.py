from pathlib import Path
import pandas as pd
import requests


BASE_DIR = Path(__file__).resolve().parents[1]

ENRICHED_PATH = BASE_DIR / "outputs" / "enriched_posts.csv"
TOPICS_PATH = BASE_DIR / "outputs" / "top_topics.csv"

SUMMARY_TXT_PATH = BASE_DIR / "outputs" / "trend_summary.txt"
SUMMARY_CSV_PATH = BASE_DIR / "outputs" / "trend_summary.csv"

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen3:4b"


def format_dict(data: dict) -> str:
    if not data:
        return "aucun élément significatif"

    return ", ".join([f"{key}: {value}" for key, value in data.items()])


def build_context(enriched_df: pd.DataFrame, topics_df: pd.DataFrame) -> dict:
    """
    Prépare le contexte donné au résumé IA.
    On utilise uniquement les posts enrichis NLP et les topics.
    Les agrégats Gold restent dans la partie 4.
    """

    enriched_df["created_at"] = pd.to_datetime(
        enriched_df["created_at"],
        errors="coerce"
    )

    match_name = (
        enriched_df["match_name"].iloc[0]
        if "match_name" in enriched_df.columns and not enriched_df.empty
        else "Non renseigné"
    )

    match_id = (
        enriched_df["match_id"].iloc[0]
        if "match_id" in enriched_df.columns and not enriched_df.empty
        else "unknown_match"
    )

    total_posts = len(enriched_df)

    start_date = enriched_df["created_at"].min()
    end_date = enriched_df["created_at"].max()

    sentiment_counts = (
        enriched_df["sentiment_label"]
        .value_counts()
        .to_dict()
        if "sentiment_label" in enriched_df.columns
        else {}
    )

    dominant_sentiment = (
        enriched_df["sentiment_label"].value_counts().idxmax()
        if "sentiment_label" in enriched_df.columns
        and not enriched_df["sentiment_label"].dropna().empty
        else "non disponible"
    )

    top_topics = (
        enriched_df["topic_label"]
        .value_counts()
        .head(5)
        .to_dict()
        if "topic_label" in enriched_df.columns
        else {}
    )

    negative_topics = (
        enriched_df[enriched_df["sentiment_label"] == "négatif"]["topic_label"]
        .value_counts()
        .head(3)
        .to_dict()
        if "sentiment_label" in enriched_df.columns
        and "topic_label" in enriched_df.columns
        else {}
    )

    top_sources = (
        enriched_df["source"]
        .value_counts()
        .head(5)
        .to_dict()
        if "source" in enriched_df.columns
        else {}
    )

    return {
        "match_id": match_id,
        "match_name": match_name,
        "start_date": start_date,
        "end_date": end_date,
        "total_posts": total_posts,
        "sentiment_counts": sentiment_counts,
        "dominant_sentiment": dominant_sentiment,
        "top_topics": top_topics,
        "negative_topics": negative_topics,
        "top_sources": top_sources
    }


def generate_template_summary(context: dict) -> str:
    """
    Fallback déterministe si Ollama n'est pas disponible.
    Le pipeline reste donc fonctionnel même sans modèle local lancé.
    """

    return f"""
Résumé automatique des tendances — {context["match_name"]}

Période analysée : du {context["start_date"]} au {context["end_date"]}.
Nombre de messages publics traités : {context["total_posts"]}.

Le sentiment dominant est : {context["dominant_sentiment"]}.
Répartition des sentiments : {format_dict(context["sentiment_counts"])}.

Les sujets les plus visibles sont : {format_dict(context["top_topics"])}.
Les sujets les plus associés aux réactions négatives sont : {format_dict(context["negative_topics"])}.
Sources les plus présentes : {format_dict(context["top_sources"])}.

Ce résumé est basé uniquement sur les posts enrichis par NLP.
Les agrégats Gold et la visualisation Superset sont pris en charge dans la partie Data Analyst.
""".strip()


def build_ollama_prompt(context: dict) -> str:
    return f"""
Tu es un assistant d'analyse de tendances football.

Rédige un résumé court, clair et factuel en français.
Utilise uniquement les données fournies.
N'invente aucune information.

Match ou compétition : {context["match_name"]}
Période : {context["start_date"]} à {context["end_date"]}
Nombre total de posts publics : {context["total_posts"]}

Sentiment dominant : {context["dominant_sentiment"]}
Répartition des sentiments : {format_dict(context["sentiment_counts"])}

Topics les plus visibles : {format_dict(context["top_topics"])}
Topics les plus associés au négatif : {format_dict(context["negative_topics"])}
Sources principales : {format_dict(context["top_sources"])}

Donne un résumé en 8 lignes maximum.
""".strip()


def generate_summary_with_ollama(context: dict) -> tuple[str, str]:
    """
    Essaie d'appeler Ollama avec Qwen.
    Si Ollama n'est pas lancé ou si le modèle n'est pas disponible,
    on utilise le fallback template.
    """

    prompt = build_ollama_prompt(context)

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()
        summary_text = response.json().get("response", "").strip()

        if summary_text:
            return summary_text, f"ollama_{OLLAMA_MODEL}"

        return generate_template_summary(context), "template_fallback_empty_ollama_response"

    except Exception as error:
        print("Ollama indisponible. Fallback template utilisé.")
        print(error)
        return generate_template_summary(context), "template_fallback_ollama_unavailable"


if __name__ == "__main__":
    enriched_df = pd.read_csv(ENRICHED_PATH)

    if TOPICS_PATH.exists():
        topics_df = pd.read_csv(TOPICS_PATH)
    else:
        topics_df = pd.DataFrame()

    context = build_context(enriched_df, topics_df)
    summary_text, summary_method = generate_summary_with_ollama(context)

    SUMMARY_TXT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(SUMMARY_TXT_PATH, "w", encoding="utf-8") as file:
        file.write(summary_text)

    summary_df = pd.DataFrame([
        {
            "match_id": context["match_id"],
            "match_name": context["match_name"],
            "summary_text": summary_text,
            "generated_at": pd.Timestamp.now(),
            "summary_method": summary_method
        }
    ])

    summary_df.to_csv(SUMMARY_CSV_PATH, index=False, encoding="utf-8")

    print("Résumé généré.")
    print(f"Méthode utilisée : {summary_method}")
    print(f"Fichier TXT : {SUMMARY_TXT_PATH}")
    print(f"Fichier CSV : {SUMMARY_CSV_PATH}")
    print()
    print(summary_text)