import enum
import json
from typing import Any, Literal, overload


class Policy(enum.Enum):
    NONE = "NONE"
    GET = "GET_ONLY"
    READ = "READ_ONLY"
    WRITE = "WRITE_ONLY"
    READ_WRITE = "READ_WRITE"

    @overload
    def bucket(
        self, bucket_name: str, *, json_encode: Literal[True] = ...
    ) -> str: ...

    @overload
    def bucket(
        self, bucket_name: str, *, json_encode: Literal[False]
    ) -> dict[str, Any]: ...

    def bucket(
        self, bucket_name: str, *, json_encode: bool = True
    ) -> str | dict[str, Any]:
        policies = {
            Policy.GET: _get,
            Policy.READ: _read,
            Policy.WRITE: _write,
            Policy.READ_WRITE: _read_write,
            Policy.NONE: _none,
        }

        pol = policies[self](bucket_name)
        if json_encode:
            return json.dumps(pol)
        return pol


def _none(bucket_name: str) -> dict[str, Any]:
    return {"Version": "2012-10-17", "Statement": []}


def _get(bucket_name: str) -> dict[str, Any]:
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{bucket_name}/*"],
            }
        ],
    }


def _read(bucket_name: str) -> dict[str, Any]:
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": ["s3:GetBucketLocation"],
                "Resource": [f"arn:aws:s3:::{bucket_name}"],
            },
            {
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": ["s3:ListBucket"],
                "Resource": [f"arn:aws:s3:::{bucket_name}"],
            },
            {
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{bucket_name}/*"],
            },
        ],
    }


def _write(bucket_name: str) -> dict[str, Any]:
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": ["s3:GetBucketLocation"],
                "Resource": [f"arn:aws:s3:::{bucket_name}"],
            },
            {
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": ["s3:ListBucketMultipartUploads"],
                "Resource": [f"arn:aws:s3:::{bucket_name}"],
            },
            {
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": [
                    "s3:ListMultipartUploadParts",
                    "s3:AbortMultipartUpload",
                    "s3:DeleteObject",
                    "s3:PutObject",
                ],
                "Resource": [f"arn:aws:s3:::{bucket_name}/*"],
            },
        ],
    }


def _read_write(bucket_name: str) -> dict[str, Any]:
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": ["s3:GetBucketLocation"],
                "Resource": [f"arn:aws:s3:::{bucket_name}"],
            },
            {
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": ["s3:ListBucket"],
                "Resource": [f"arn:aws:s3:::{bucket_name}"],
            },
            {
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": ["s3:ListBucketMultipartUploads"],
                "Resource": [f"arn:aws:s3:::{bucket_name}"],
            },
            {
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": [
                    "s3:AbortMultipartUpload",
                    "s3:DeleteObject",
                    "s3:GetObject",
                    "s3:ListMultipartUploadParts",
                    "s3:PutObject",
                ],
                "Resource": [f"arn:aws:s3:::{bucket_name}/*"],
            },
        ],
    }
