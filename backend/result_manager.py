import os
import json

VAULT_PATH = os.path.join(os.path.dirname(__file__), 'registry', 'organ_strength_vault.json')

def load_vault():
    if os.path.exists(VAULT_PATH):
        with open(VAULT_PATH, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_vault(data):
    os.makedirs(os.path.dirname(VAULT_PATH), exist_ok=True)
    with open(VAULT_PATH, "w") as f:
        json.dump(data, f, indent=4)

def initialize_structure(vault):
    """
    Ensures old flat list structure is converted to the new dict structure with status.
    """
    updated = False
    for category, content in list(vault.items()):
        if isinstance(content, list):
            # Convert list to dict with status
            vault[category] = {
                "status": "active",
                "findings": content
            }
            updated = True
    if updated:
        save_vault(vault)
    return vault

def set_category_status(category, status):
    """
    Sets the status of a category to 'active', 'archived', or 'trash'.
    """
    if status not in ['active', 'archived', 'trash']:
        return {"error": f"Invalid status: {status}"}
        
    vault = load_vault()
    vault = initialize_structure(vault)
    
    if category in vault:
        vault[category]["status"] = status
        save_vault(vault)
        return {"success": f"Category '{category}' moved to {status}."}
    else:
        return {"error": f"Category '{category}' not found."}

def permanent_delete_category(category):
    """
    Permanently deletes a category from the vault if it is in trash.
    """
    vault = load_vault()
    vault = initialize_structure(vault)
    
    if category in vault:
        if vault[category]["status"] == "trash":
            del vault[category]
            save_vault(vault)
            return {"success": f"Category '{category}' permanently deleted."}
        else:
            return {"error": f"Category '{category}' must be in trash before permanent deletion."}
    else:
        return {"error": f"Category '{category}' not found."}

def get_categories_by_status(status):
    """
    Returns all categories with a specific status.
    """
    vault = load_vault()
    vault = initialize_structure(vault)
    
    result = {}
    for category, content in vault.items():
        if content.get("status") == status:
            result[category] = content["findings"]
    return result

if __name__ == "__main__":
    # Test the manager
    print("Initializing Vault Structure...")
    v = load_vault()
    initialize_structure(v)
    print("Vault initialized.")
    
    # Test getting active
    print("\nActive Categories:")
    print(list(get_categories_by_status("active").keys()))
