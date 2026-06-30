from __future__ import annotations

import logging
import re

SENSITIVE_KEYS: tuple[str, ...] = (
    "company_tax_id",
    "tax_id",
    "taxId",
    "companyTaxId",
)


class SensitiveDataFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        for key in SENSITIVE_KEYS:
            if hasattr(record, key):
                setattr(record, key, "[REDACTED]")
            if isinstance(record.msg, str):
                record.msg = re.sub(
                    rf"{re.escape(key)}\s*[:=]\s*['\"]?[^,'\"\s}}]+",
                    f"{key}=[REDACTED]",
                    record.msg,
                )
        if record.args:
            new_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    for key in SENSITIVE_KEYS:
                        arg = re.sub(
                            rf"{re.escape(key)}\s*[:=]\s*['\"]?[^,'\"\s}}]+",
                            f"{key}=[REDACTED]",
                            arg,
                        )
                new_args.append(arg)
            record.args = tuple(new_args)
        return True


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.addFilter(SensitiveDataFilter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)
