import json
from pathlib import Path
from jsonschema import validate, ValidationError, Draft7Validator


class CVSchema:
    def __init__(self, schema_path: str | Path = None):
        if schema_path is None:
            schema_path = Path(__file__).parent / "schema.json"
        with open(schema_path) as f:
            self.schema = json.load(f)
        self.validator = Draft7Validator(self.schema)

    def validate(self, data: dict) -> tuple[bool, list[str]]:
        errors = []
        for error in self.validator.iter_errors(data):
            path = ".".join(str(p) for p in error.path) if error.path else "root"
            errors.append(f"{path}: {error.message}")
        return len(errors) == 0, errors

    def validate_file(self, file_path: str | Path) -> tuple[bool, list[str]]:
        with open(file_path) as f:
            data = json.load(f)
        return self.validate(data)
