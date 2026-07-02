import io
import json
from datetime import datetime

from storage.minio_client import get_minio


def save_json(bucket, prefix, data):

    client = get_minio()

    filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".json"

    key = f"{prefix}/{filename}"

    body = json.dumps(
        data,
        indent=2,
        ensure_ascii=False
    ).encode("utf-8")

    client.put_object(
        Bucket=bucket,
        Key=key,
        Body=io.BytesIO(body),
        ContentLength=len(body),
        ContentType="application/json"
    )

    print(f"Saved {key} to bucket '{bucket}'")