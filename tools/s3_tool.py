from typing import Optional
import io
import logging
from botocore.exceptions import ClientError
from config import s3_client, settings

logger = logging.getLogger(__name__)


def upload_text_to_s3(text: str, key: str, content_type: str = "text/plain") -> Optional[str]:
    """
    Upload a string as an object to the configured S3 bucket.
    Returns the S3 object URL on success, None on failure.
    `key` should be something like "research/<timestamp>_topic.txt"
    """
    bucket = settings.AWS_S3_BUCKET
    if not bucket:
        logger.error("AWS_S3_BUCKET not configured")
        return None

    try:
        # boto3 accepts bytes or file-like object
        body = io.BytesIO(text.encode("utf-8"))
        s3_client.upload_fileobj(
            Fileobj=body,
            Bucket=bucket,
            Key=key,
            ExtraArgs={"ContentType": content_type, "ACL": "private"},
        )

        # Construct an S3 URL (may vary depending on region / bucket config)
        url = f"s3://{bucket}/{key}"
        return url
    except ClientError as e:
        logger.exception("Failed to upload to S3: %s", e)
        return None


def download_text_from_s3(key: str) -> Optional[str]:
    """
    Download an object from S3 and return its text content, or None on failure.
    """
    bucket = settings.AWS_S3_BUCKET
    if not bucket:
        logger.error("AWS_S3_BUCKET not configured")
        return None

    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        body = response["Body"].read()
        return body.decode("utf-8")
    except ClientError as e:
        logger.exception("Failed to download from S3: %s", e)
        return None
