from __future__ import annotations

from abc import ABC, abstractmethod

from src.core.fetch import FetchClient
from src.core.schema import ScholarshipRecord


class BaseScholarshipAdapter(ABC):
    source_name: str

    @abstractmethod
    def collect(self, fetch_client: FetchClient) -> list[ScholarshipRecord]:
        raise NotImplementedError
