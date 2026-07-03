from services.load_enriched_posts import load_enriched_posts
from services.load_summary import load_summary
from services.load_event_correlations import load_event_correlations


load_enriched_posts(
    "../partie_3_nlp/outputs/enriched_posts.csv"
)

load_summary(
    "../partie_3_nlp/outputs/trend_summary.csv"
)

load_event_correlations(
    "../partie_3_nlp/outputs/event_correlation_report.csv"
)

print("NLP results loaded.")