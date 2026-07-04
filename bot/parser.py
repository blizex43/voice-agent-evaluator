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

parser_functions: dict[ParserFunctionNamesType, Callable] = {}


def register_parser(name: ParserFunctionNamesType) -> ParserDefaultReturnType:
    def decorator(fn: ParserDefaultReturnType):
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> None:
            return fn(*args, **kwargs)

        parser_functions[name] = wrapper
        return wrapper

    return decorator


def extract_inline(input: str, prefix: str, suffix: str) -> str | None:
    """Parses the string for the string encapsulating both the prefix and the suffix"""
    if prefix and suffix:
        prefix_index = input.find(prefix)
        if prefix_index == -1:
            return None

        start = prefix_index + len(prefix)
        suffix_index = input.find(suffix, start)
        if suffix_index == -1:
            return input[start:]
        return input[start:suffix_index]

    if prefix:
        prefix_index = input.find(prefix)
        if prefix_index == -1:
            return None

        return input[prefix_index + len(prefix) :]

    if suffix:
        suffix_index = input.find(suffix)
        if suffix_index == -1:
            return None

        return input[:suffix_index]

    return input


def parse_value(
    input: str, name: ParserFunctionNamesType, value: Maybe[ParserDictNecessitiesType] = None
) -> Maybe[tuple[str, ParserDefaultReturnType, ParserFunctionNamesType]]:
    """Parse the string for a valid parse function while also returning the function parsed"""
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
    """Return the reply text and whether the call should be hung up."""
    for parser_name in ("parser_end_call", "parser_say"):
        result = parse_value(input, parser_name, None)
        if result is None:
            continue

        inline, _, matched_name = result
        return inline, matched_name == "parser_end_call"

    return input, False


def parse_response_for_matches(
    input: str,
) -> list[tuple[ParserFunctionNamesType, ParserDefaultReturnType, str]]:
    """Return parser matches with the resolved function and extracted inline text."""
    matches: list[tuple[ParserFunctionNamesType, ParserDefaultReturnType, str]] = []
    for func_name, func_value in parser_function_info.items():
        result = parse_value(input, func_name, func_value)
        if result is None:
            continue

        inline, func = result
        matches.append((func_name, func, inline))

    return matches
