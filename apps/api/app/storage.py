"""MinIO (S3-compatible) storage helpers using boto3 — Phase 1."""

import boto3
from botocore.client import Config as BotoConfig

from app.config import settings


def get_s3_client():
    """Return a boto3 S3 client configured for the MinIO instance."""
    return boto3.client(
        "s3",
        endpoint_url=f"http://{settings.minio_endpoint}",
        aws_access_key_id=settings.minio_user,
        aws_secret_access_key=settings.minio_password,
        config=BotoConfig(signature_version="s3v4"),
        region_name="us-east-1",
    )


def ensure_bucket() -> None:
    """Create the default bucket if it doesn't already exist."""
    client = get_s3_client()
    try:
        client.head_bucket(Bucket=settings.minio_bucket)
    except client.exceptions.ClientError:
        client.create_bucket(Bucket=settings.minio_bucket)


def upload_file(file_obj, object_key: str, content_type: str) -> str:
    """Upload a file-like object to MinIO and return the object key."""
    client = get_s3_client()
    ensure_bucket()
    client.upload_fileobj(
        file_obj,
        settings.minio_bucket,
        object_key,
        ExtraArgs={"ContentType": content_type},
    )
    return object_key


def generate_presigned_url(object_key: str, expires_in: int = 3600) -> str:
    """Generate a presigned GET URL for a MinIO object."""
    client = get_s3_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.minio_bucket, "Key": object_key},
        ExpiresIn=expires_in,
    )


def delete_file(object_key: str) -> None:
    """Delete an object from MinIO."""
    client = get_s3_client()
    client.delete_object(Bucket=settings.minio_bucket, Key=object_key)
