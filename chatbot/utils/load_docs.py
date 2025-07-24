import json
from langchain.schema import Document
import hashlib
import os
from typing import List
import glob
from load_docs.load_denizcilik_fakultesi import process_data as process_denizcilik_json
from load_docs.load_dmyo import process_data as process_dmyo_json
from load_docs.load_het import process_data as process_het_json
from load_docs.load_hukuk import process_data as process_hukuk_json
from load_docs.load_iibf import process_data as process_iibf_json
from load_docs.load_kisiler import process_data as process_people_json
from load_docs.load_muhendislik import process_data as process_muhendislik_json


def compute_hash(content: str) -> str:
    """
    Computes a SHA256 hash from content to prevent duplicate document loading.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def identify_json_type(data, file_name: str) -> str:
    """
    Identify the type of JSON file based on its content and name.
    """
    file_name_lower = file_name.lower()
    
    if file_name_lower == "denizcilik_fakultesi.json":
        return "denizcilik_fakultesi"
    elif file_name_lower == "dmyo.json":
        return "dmyo"
    elif file_name_lower == "het.json":
        return "het"
    elif file_name_lower == "hukuk.json":
        return "hukuk"
    elif file_name_lower == "iibf.json":
        return "iibf"
    elif file_name_lower == "kisiler.json":
        return "kisiler"
    elif file_name_lower == "muhendislik.json":
        return "muhendislik"
    else:
        return "unknown"


def load_docs() -> List[Document]:
    """
    Loads all JSON files in the data directory and converts them to LangChain Documents.
    Handles different JSON structures appropriately.
    """
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(BASE_DIR, "data")

    # Get all JSON files in the data directory
    json_files = glob.glob(os.path.join(data_dir, "*.json"))
    
    all_docs = []
    processed_hashes = set()
    
    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            file_name = os.path.basename(json_file)
            print(f"[DEBUG] Loaded {file_name}")
            
            # Identify JSON type and process accordingly
            json_type = identify_json_type(data, file_name)
            
            if json_type == "denizcilik_fakultesi":
                docs = process_denizcilik_json(data, file_name)
            elif json_type == "dmyo":
                docs = process_dmyo_json(data, file_name)
            elif json_type == "het":
                docs = process_het_json(data, file_name)
            elif json_type == "hukuk":
                docs = process_hukuk_json(data, file_name)
            elif json_type == "iibf":
                docs = process_iibf_json(data, file_name)
            elif json_type == "kisiler":
                docs = process_people_json(data, file_name)
            elif json_type == "muhendislik":
                docs = process_muhendislik_json(data, file_name)
            else:
                print(f"[WARNING] Unknown JSON structure in {file_name}, skipping...")
                continue
            
            # Filter out duplicates based on content hash
            for doc in docs:
                if doc.metadata["hash"] not in processed_hashes:
                    processed_hashes.add(doc.metadata["hash"])
                    all_docs.append(doc)
            
        except FileNotFoundError:
            print(f"❌ {os.path.basename(json_file)} not found.")
        except json.JSONDecodeError:
            print(f"❌ Error decoding {os.path.basename(json_file)}: Invalid JSON format.")
        except Exception as e:
            print(f"❌ Error processing {os.path.basename(json_file)}: {e}")
    
    print(f"[i] Total {len(all_docs)} unique documents loaded")
    return all_docs