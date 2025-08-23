# ======== JSON Storage Helpers (int user_id) ========
import json
import os
from typing import Optional


def save_data(user_id: int, field: str, value) -> None:
    """Save or update a field for a specific user (nested dictionary)."""
    path = 'storage.json'
    data = {}
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f) or {}
        except json.JSONDecodeError:
            data = {}

    user_data = data.get(user_id, {})
    user_data[field] = value
    data[str(user_id)] = user_data

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_data(user_id: int, field: str) -> Optional[str]:
    """Retrieve a field value by user ID from storage.json."""
    try:
        with open('storage.json', 'r', encoding='utf-8') as f:
            data = json.load(f) or {}
        return data.get(str(user_id), {}).get(field)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def delete_data(user_id: int, field: str = None) -> None:
    """Delete a field or the entire user entry."""
    path = 'storage.json'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f) or {}
        if str(user_id) in data:
            if field:
                data[str(user_id)].pop(field, None)
            else:
                del data[str(user_id)]
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
