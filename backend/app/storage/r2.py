"""
Cloudflare R2 upload helper.

R2 is S3-compatible, so this just uses boto3's S3 client pointed at R2's
endpoint. Needs these env vars set (e.g. in backend/.env):

    R2_ACCOUNT_ID        — Cloudflare account id
    R2_ACCESS_KEY_ID     — R2 API token access key
    R2_SECRET_ACCESS_KEY — R2 API token secret
    R2_BUCKET_NAME       — the bucket to upload into
    R2_PUBLIC_URL        — the public base URL for the bucket
                            (either the R2.dev URL or a custom domain
                            you've mapped to the bucket), no trailing slash

None of these are required for the app to boot — get_r2_client() only
raises when an upload is actually attempted without them configured, so
local dev without R2 set up still works for everything else.
"""

import os
import uuid
import boto3
from botocore.client import Config as BotoConfig

ALLOWED_IMAGE_TYPES = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/webp": "webp",
    "image/gif": "gif",
}

MAX_IMAGE_BYTES = 2 * 1024 * 1024  # 2MB, same limit the old raw-bytes code used


class R2NotConfigured(Exception):
    pass


def _get_config():
    account_id = os.getenv("R2_ACCOUNT_ID")
    access_key = os.getenv("R2_ACCESS_KEY_ID")
    secret_key = os.getenv("R2_SECRET_ACCESS_KEY")
    bucket = os.getenv("R2_BUCKET_NAME")
    public_url = os.getenv("R2_PUBLIC_URL")

    missing = [
        name for name, val in [
            ("R2_ACCOUNT_ID", account_id),
            ("R2_ACCESS_KEY_ID", access_key),
            ("R2_SECRET_ACCESS_KEY", secret_key),
            ("R2_BUCKET_NAME", bucket),
            ("R2_PUBLIC_URL", public_url),
        ] if not val
    ]

    if missing:
        raise R2NotConfigured(
            f"R2 is not configured — missing env vars: {', '.join(missing)}"
        )

    return account_id, access_key, secret_key, bucket, public_url.rstrip("/")


def get_r2_client():
    account_id, access_key, secret_key, _, _ = _get_config()

    return boto3.client(
        "s3",
        endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=BotoConfig(signature_version="s3v4"),
        region_name="auto",
    )


def upload_image(file_storage, key_prefix):
    """Uploads a werkzeug FileStorage image to R2 and returns its public URL.

    Raises R2NotConfigured, ValueError (bad type/size), or a boto3
    ClientError on upload failure — callers should catch these and turn
    them into the appropriate HTTP response.
    """
    _, _, _, bucket, public_url = _get_config()

    content_type = file_storage.mimetype
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise ValueError(f"unsupported image type: {content_type}")

    file_storage.stream.seek(0, os.SEEK_END)
    size = file_storage.stream.tell()
    file_storage.stream.seek(0)

    if size > MAX_IMAGE_BYTES:
        raise ValueError("image too large (max 2MB)")

    ext = ALLOWED_IMAGE_TYPES[content_type]
    key = f"{key_prefix}/{uuid.uuid4()}.{ext}"

    client = get_r2_client()
    client.upload_fileobj(
        file_storage.stream,
        bucket,
        key,
        ExtraArgs={"ContentType": content_type},
    )

    return f"{public_url}/{key}"