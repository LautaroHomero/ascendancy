import re

# Sufijos redundantes en títulos de LinkedIn que fragmentan el mismo grado
# en varios strings (ej. "Bachelor of Arts (B.A.)" vs "Bachelor of Arts (BA)").
_DEGREE_TRAILING_PAREN = re.compile(r"\s*\([^)]*\)\s*$")
_DEGREE_TRAILING_DASH = re.compile(
    r"\s*-\s*"
    r"(BA|BS|BSc|B\.A\.|B\.S\.|M\.A\.|MA|MS|M\.S\.|Ph\.?D\.?|MBA|JD|"
    r"Associate|Bachelor|Master|Doctor)"
    r"\s*$",
    re.IGNORECASE,
)


def normalize_degree(degree: str) -> str:
    """Unifica variantes del mismo título académico."""

    if not degree:

        return degree

    result = degree.strip()

    result = _DEGREE_TRAILING_PAREN.sub("", result).strip()
    result = _DEGREE_TRAILING_DASH.sub("", result).strip()

    return result or degree.strip()
