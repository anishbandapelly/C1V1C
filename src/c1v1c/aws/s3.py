"""Amazon S3 adapter for versioned baseline objects and immutable run records."""
from __future__ import annotations

import hashlib
from pathlib import Path

from c1v1c.config import Settings


class S3Unavailable(RuntimeError):
    pass


def _client(settings: Settings):
    import boto3
    from botocore.config import Config

    cfg = Config(region_name=settings.aws_region, connect_timeout=settings.aws_timeout_s, read_timeout=settings.aws_timeout_s,
                 retries={"max_attempts": 2, "mode": "standard"})
    return boto3.client("s3", config=cfg)


def _safe(exc: Exception) -> str:
    """Error text without request ids, account numbers or credentials."""
    response = getattr(exc, "response", None) or {}
    code = response.get("Error", {}).get("Code")
    return f"{exc.__class__.__name__}{': ' + code if code else ''}"


class S3Store:
    def __init__(self, settings: Settings | None = None, client=None):
        self.settings = settings or Settings.load()
        if not self.settings.s3_bucket:
            raise S3Unavailable("S3_BUCKET is not configured")
        self.bucket = self.settings.s3_bucket
        self.client = client or _client(self.settings)

    def put_json(self, key: str, body: str) -> dict:
        """Write with server-side encryption; returns key, version id (if versioning is on) and checksum."""
        from botocore.exceptions import BotoCoreError, ClientError

        try:
            r = self.client.put_object(Bucket=self.bucket, Key=key, Body=body.encode(), ContentType="application/json",
                                       ServerSideEncryption="AES256")
        except (ClientError, BotoCoreError) as exc:
            raise S3Unavailable(_safe(exc)) from None
        return {"bucket": self.bucket, "key": key, "version_id": r.get("VersionId"),
                "sha256": hashlib.sha256(body.encode()).hexdigest()}

    def put_file(self, key: str, path: Path) -> dict:
        return self.put_json(key, Path(path).read_text(encoding="utf-8"))

    def get_text(self, key: str) -> str | None:
        from botocore.exceptions import BotoCoreError, ClientError

        try:
            r = self.client.get_object(Bucket=self.bucket, Key=key)
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") in ("NoSuchKey", "404"):
                return None
            raise S3Unavailable(_safe(exc)) from None
        except BotoCoreError as exc:
            raise S3Unavailable(_safe(exc)) from None
        return r["Body"].read().decode()


class FailoverS3:
    """Wraps S3Store so a cloud failure never breaks a local run; failures are recorded, not hidden."""

    def __init__(self, store: S3Store):
        self.store = store
        self.last_error: str | None = None

    def put_json(self, key: str, body: str) -> dict:
        try:
            ref = self.store.put_json(key, body)
            self.last_error = None
            return ref
        except S3Unavailable as exc:
            self.last_error = str(exc)
            return {"error": self.last_error}

    def get_text(self, key: str) -> str | None:
        try:
            return self.store.get_text(key)
        except S3Unavailable as exc:
            self.last_error = str(exc)
            return None
