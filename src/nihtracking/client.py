"""Lightweight NIH RePORTER client."""
from __future__ import annotations

import dataclasses
import json
from typing import Iterable, List, Mapping, MutableMapping
from urllib import request

API_URL = "https://api.reporter.nih.gov/v2/projects/search"
DEFAULT_FIELDS = [
    "project_num",
    "project_title",
    "pi_names",
    "org_name",
    "fy",
    "award_amount",
]


@dataclasses.dataclass
class SearchCriteria:
    """Search parameters for the NIH RePORTER API."""

    text_phrase: str
    fiscal_years: Iterable[int]

    def to_payload(self) -> MutableMapping[str, object]:
        return {
            "text_phrase": self.text_phrase,
            "fiscal_years": list(self.fiscal_years),
        }


class NIHReporterClient:
    """Client for paginated NIH RePORTER project searches."""

    def __init__(self) -> None:
        self._headers = {"Content-Type": "application/json"}

    def _post_json(self, payload: MutableMapping[str, object]) -> MutableMapping[str, object]:
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(API_URL, data=data, headers=self._headers)
        with request.urlopen(req, timeout=30) as resp:
            content = resp.read()
        return json.loads(content)

    def search_projects(
        self,
        criteria: SearchCriteria,
        *,
        limit: int = 500,
        include_fields: Iterable[str] | None = None,
    ) -> List[Mapping[str, object]]:
        """Fetch all project records matching ``criteria``.

        The call paginates until all records are retrieved or the API stops
        returning results. Use ``limit`` to adjust page size (max allowed is
        500 by the NIH API).  ``include_fields`` defaults to
        :data:`DEFAULT_FIELDS`.
        """

        fields = list(include_fields) if include_fields else DEFAULT_FIELDS
        payload = {
            "criteria": criteria.to_payload(),
            "include_fields": fields,
            "limit": limit,
            "offset": 0,
        }

        results: list[Mapping[str, object]] = []
        while True:
            body = self._post_json(payload)

            page = body.get("results", [])
            results.extend(page)

            meta = body.get("meta", {})
            total = meta.get("total", 0)
            if payload["offset"] + limit >= total or not page:
                break

            payload["offset"] += limit

        return results
