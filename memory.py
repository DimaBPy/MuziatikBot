# ======== JSON Storage Helpers (int user_id) ========
import json
import os
from typing import Optional


def save_data(user_id: int, field: str, value) -> None:
    """Save or update a field for a specific user (nested dictionary)."""
    path = 'storage.json'
    if os.path.exists(path):
        with open(path, 'r+', encoding='utf-8') as f:
            try:
                data = json.load(f)  # Load existing data
            except json.JSONDecodeError:
                # If file is empty or invalid, initialize to empty dict
                data = {}

            user_data = data.get(str(user_id), {})  # Fix: user_id should be a string
            user_data[field.lower()] = value.lower() if isinstance(value, str) else value
            data[str(user_id)] = user_data
            # Move the file pointer to the start before writing
            f.seek(0)
            f.truncate()
            json.dump(data, f, ensure_ascii=False, indent=2)
    else:
        # If a file doesn't exist, create a new one
        with open(path, 'w', encoding='utf-8') as f:
            data = {str(user_id): {field.lower(): value.lower() if isinstance(value, str) else value}}
            json.dump(data, f, ensure_ascii=False, indent=2)


def get_data(user_id: int, field: str = None) -> Optional[str]:
    """Retrieve a field value by user ID from storage.json."""
    try:
        with open('storage.json', 'r', encoding='utf-8') as f:
            data = json.load(f) or {}
        user_data = data.get(str(user_id), {})
        if field:
            return user_data.get(field.lower() if field else None)
        else:
            # Filter out voice_week_start_ts and voice_counter from the returned data
            return {k: v for k, v in user_data.items()
                    if k not in ['voice_week_start_ts', 'voice_counter']}
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
                data[str(user_id)].pop(field.lower(), None)
            else:
                del data[str(user_id)]
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
