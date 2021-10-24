from typing import Any
import bleach


def shorten_string_to(string, num) -> str:
	return string if len(string) > num else f'{string[0:num]}...'


def clean_string(string_convertible: Any) -> str:
	return bleach.clean(
		text=str(string_convertible),
		tags=[],
		strip=True
	)


def foreign_key_title(string_convertible: Any):
	return 'None' if string_convertible is None else getattr(string_convertible, 'title')
