from typing import Literal, Callable, Any
from pyee import EventEmitter

# Type definitions for parser functions
type ParserFunctionNamesType = Literal["parser_end_call", "parser_say"]
type ParserDictNecessitiesType = dict[Literal["prefix", "suffix"], str]
type ParserDictValue = dict[ParserFunctionNamesType, ParserDictNecessitiesType]
type ParserDefaultReturnType = Callable[[str, str], Any]

# Type for parser signal handlers
type ParserSignalHandler = Callable[[str, Any], None]