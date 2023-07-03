import re

from typing import Dict, Any

from flows.data_transformations.abstract import DataTransformation

from ..utils import logging

log = logging.get_logger(__name__)


class RegexFirstOccurrenceExtractor(DataTransformation):
    def __init__(self,
                 regex: str,
                 output_key: str,
                 assert_unique: bool,
                 strip: bool,
                 verbose: bool,
                 regex_fallback: str = None,
                 input_key: str = "raw_response"):
        super().__init__(output_key=output_key)
        self.input_key = input_key
        self.regex = regex
        self.regex_fallback = regex_fallback
        self.strip = strip
        self.assert_unique = assert_unique
        self.verbose = verbose

    def __call__(self, data_dict: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        txt = self._search(data_dict[self.input_key], self.regex)

        if txt is None and self.regex_fallback:
            if isinstance(self.regex_fallback, str):
                self.regex_fallback = [self.regex_fallback]

            for fallback_regex in self.regex_fallback:
                txt = self._search(data_dict[self.input_key], fallback_regex)
                if txt is not None:
                    if self.verbose:
                        log.info(f"Regex {self.regex} was not found, but {fallback_regex} was successful.")
                    break

        if txt is not None and self.strip:
            txt = txt.strip()

        data_dict[self.output_key] = txt
        return data_dict

    def _search(self, message, regex):
        match = re.search(regex, message)
        if match:
            if self.assert_unique:
                num_matches = len(match.groups())
                assert num_matches == 1, f"Regex {regex} expected to have only one group, found {num_matches}"
            return match.group(0)
        else:
            return None