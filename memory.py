# ======== JSON Storage Helpers (int user_id) ========
import json
import os
from typing import Optional


def save_data(user_id: int, field: str, value) -> None:
    """
    Save or update a single field for a user in persistent JSON storage.
    
    The function loads storage.json (if present; invalid JSON is treated as empty), updates the nested per-user dictionary stored under the stringified user_id with the given field/value, and writes the updated data back to storage.json using UTF-8 and pretty-printed JSON (ensure_ascii=False, indent=2).
    
    Parameters:
        user_id (int): Numeric user identifier; stored as a string key in the JSON object.
        field (str): Name of the field to set or update for the user.
        value: Value to assign to the specified field.
    
    Notes:
        - If storage.json contains invalid JSON, it will be replaced with a fresh structure containing only the provided update.
        - IO errors during writing are propagated.
    """
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
    """
    Return the value of `field` for `user_id` from storage.json, or None if not present.
    
    storage.json is expected to be a JSON object whose top-level keys are user IDs as strings and whose values are per-user dictionaries of field -> value pairs. If the file is missing, contains invalid JSON, the user ID or field is not present, this function returns None.
    
    Parameters:
        user_id (int): User identifier; converted to a string to index the top-level JSON object.
        field (str): Name of the field to retrieve.
    
    Returns:
        Optional[str]: The stored value for the given field, or None when not found or on file/parse errors.
    """
    try:
        with open('storage.json', 'r', encoding='utf-8') as f:
            data = json.load(f) or {}
        return data.get(str(user_id), {}).get(field)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def delete_data(user_id: int, field: str = None) -> None:
    """
    Delete a specific field for a user or remove the user's entire entry from storage.json.
    
    If `field` is provided, removes that key from the user's dictionary (no error if the key is absent). If `field` is None, deletes the whole user record stored under the stringified `user_id`. Updates are written back to storage.json with UTF-8 encoding and pretty JSON formatting. If the file is missing or contains invalid JSON, the function does nothing.
    """
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
