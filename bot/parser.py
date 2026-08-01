from enums.parser import parser_function_info
from .listeners import parser_signal
from functools import wraps
from typing import Callable, Any
from structs.custom import Maybe
from structs.parser import (
    ParserFunctionNamesType,
    ParserDefaultReturnType,
    ParserDictNecessitiesType,
)
from enums.prompts import blacklist_items
import re

parser_functions: dict[ParserFunctionNamesType, Callable] = {}


def register_parser(name: ParserFunctionNamesType) -> ParserDefaultReturnType:
    """Register a parser function so it can be matched against response text."""

    def decorator(fn: ParserDefaultReturnType):
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> None:
            return fn(*args, **kwargs)

        parser_functions[name] = wrapper
        return wrapper

    return decorator


def extract_inline(text: str, prefix: str, suffix: str) -> tuple[str, bool]:
    """Extract the content between a parser prefix and suffix, if present."""
    if prefix and suffix:
        match = re.search(
            re.escape(prefix) + r"(.*?)" + re.escape(suffix),
            text,
            re.DOTALL,
        )
        if match:
            return (match.group(1), True)

    if prefix:
        match = re.search(
            re.escape(prefix) + r"(.*)",
            text,
            re.DOTALL,
        )
        if match:
            return (match.group(1), True)

    if suffix:
        match = re.search(
            r"(.*?)" + re.escape(suffix),
            text,
            re.DOTALL,
        )
        if match:
            return (match.group(1), True)

    return (text, False)


def parse_value(
    input: str,
    name: ParserFunctionNamesType,
    value: Maybe[ParserDictNecessitiesType] = None,
) -> Maybe[tuple[str, ParserFunctionNamesType]]:
    """Check whether a response contains a parser marker and return the parsed result."""
    if not value:
        value = parser_function_info[name]

    if name not in parser_functions:
        return None

    prefix = value.get("prefix", "")
    suffix = value.get("suffix", "")

    inline, response = extract_inline(input, prefix, suffix)
    if not response:
        return None

    parser_signal.emit("parser_succeeded", name, input)
    return (inline, name)


@register_parser("parser_end_call")
def end_call_parser(input: str, inline: str) -> str:
    """Parser function to end the call"""
    pass


@register_parser("parser_say")
def say_parser(input: str, inline: str) -> str:
    """Parser function to respond to the caller"""
    pass


def parse_response_for_functions(input: str) -> list[ParserFunctionNamesType]:
    return [
        func_name
        for func_name, func_value in parser_function_info.items()
        if parse_value(input, func_name, func_value)
    ]


def resolve_parser_reply(input: str) -> tuple[str, bool]:
    """Return the reply text and whether the call should end based on parser markers."""
    matches = parse_response_for_matches(input)
    if not matches:
        return input, False
    hang_up = "parser_end_call" in matches
    exported_text = matches.get("parser_say") or list(matches.values())[0]
    return exported_text, hang_up


def is_blacklisted_input(text: str) -> bool:
    """Return True if any blacklist phrase exists in the text."""
    lowered = text.lower()

    return any(
        phrase.lower() in lowered
        for item in blacklist_items
        for phrase in item.get("phrases", ())
    )


def query_blacklisted_input(text: str) -> bool:
    """Return False if a blacklist phrase exceeds its suffix word limit."""
    if not text:
        return True

    lowered = text.lower()

    for item in blacklist_items:
        limit = item.get("suffix_word_limit", 0)
        if limit <= 0:
            continue

        for phrase in item.get("phrases", ()):
            phrase = phrase.lower()

            index = lowered.find(phrase)
            if index == -1:
                continue

            suffix = lowered[index + len(phrase) :].strip()
            words = len(suffix.split())

            if words > limit:
                return False

    return True


def parse_response_for_matches(
    input: str,
) -> dict[ParserFunctionNamesType, str]:
    """Return all parser matches found in the input text with their extracted values."""
    matches: dict[ParserFunctionNamesType, str] = {}
    parsers = sorted(
        parser_function_info.items(),
        key=lambda item: (
            item[1].get("prefix", "") == "",  # False (0) first, True (1) last
        ),
    )

    for func_name, func_value in parsers:
        result = parse_value(input, func_name, func_value)
        if result is None:
            continue
        else:
            matches[func_name] = result[0]

    return matches
