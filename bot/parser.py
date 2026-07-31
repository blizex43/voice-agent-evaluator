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
from enums.prompts import blacklisted_phrases
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


def extract_inline(text: str, prefix: str, suffix: str) -> str | None:
    """Extract the content between a parser prefix and suffix, if present."""
    if prefix and suffix:
        match = re.search(
            re.escape(prefix) + r"(.*?)" + re.escape(suffix),
            text,
            re.DOTALL,
        )
        return match.group(1) if match else None

    if prefix:
        match = re.search(
            re.escape(prefix) + r"(.*)",
            text,
            re.DOTALL,
        )
        return match.group(1) if match else None

    if suffix:
        match = re.search(
            r"(.*?)" + re.escape(suffix),
            text,
            re.DOTALL,
        )
        return match.group(1) if match else None

    return text


def parse_value(
    input: str,
    name: ParserFunctionNamesType,
    value: Maybe[ParserDictNecessitiesType] = None,
) -> Maybe[tuple[str, ParserDefaultReturnType, ParserFunctionNamesType]]:
    """Check whether a response contains a parser marker and return the parsed result."""
    if not value:
        value = parser_function_info[name]

    if name not in parser_functions:
        return None

    prefix = value.get("prefix", "")
    suffix = value.get("suffix", "")

    inline = extract_inline(input, prefix, suffix)
    if inline is None:
        return None

    parser_signal.emit("parser_succeeded", name, input)
    return inline, parser_functions[name], name


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
    for parser_name in parser_function_info.keys():
        result = parse_value(input, parser_name, None)
        if result is None:
            continue

        inline, _, matched_name = result
        return inline, matched_name == "parser_end_call"

    return input, False


def is_blacklisted_input(text: str) -> bool:
    """Return True when the incoming input contains a blocked phrase."""
    lowered_text = text.lower()
    return any(phrase.lower() in lowered_text for phrase in blacklisted_phrases)


def parse_response_for_matches(
    input: str,
) -> list[tuple[ParserFunctionNamesType, ParserDefaultReturnType, str]]:
    """Return all parser matches found in the input text with their extracted values."""
    matches: list[tuple[ParserFunctionNamesType, ParserDefaultReturnType, str]] = []
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
            (input,) = result

        inline, func = result
        matches.append((func_name, func, inline))

    return matches
