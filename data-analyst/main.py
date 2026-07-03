from services.load_enriched_posts import load_enriched_posts
from services.load_summary import load_summary
from services.load_event_correlations import load_event_correlations
from services.aggregate import run_aggregation

if __name__ == "__main__":

    print("Loading NLP results into MongoDB...")

    load_enriched_posts(
        "../partie_3_nlp/outputs/enriched_posts.csv"
    )

    print("Running aggregations...")

    run_aggregation()

    print("Loading summaries...")

    load_summary(
        "../partie_3_nlp/outputs/trend_summary.csv"
    )

    print("Loading event correlations...")

    load_event_correlations(
        "../partie_3_nlp/outputs/event_correlation_report.csv"
    )

    print("Pipeline completed.")