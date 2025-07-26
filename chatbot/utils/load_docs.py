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
from load_docs.load_ders_koordinasyonlugu import process_data as process_ders_koordinasyonu_json       
from load_docs.load_ek_sinav_hakki import process_data as process_ek_sinav_hakki_json
from load_docs.load_ingilizce_hazirlik_yonetmeligi import process_data as process_ingilizce_yonetmeligi_json   
from load_docs.load_lisans_onlisans_egitim_sinav_yonetmeligi import process_data as process_lisans_onlisans_json
from load_docs.load_uniforma_yonetmeligi import process_data as process_uniforma_yonetmeligi_json
from load_docs.load_erasmus_universiteleri import process_data as process_erasmus_json
from load_docs.load_kampus_olanaklari import process_data as process_kampus_json
from load_docs.load_siralamalar import process_data as process_siralamalar_json
from load_docs.load_ucretler import process_data as process_ucretler_json
from load_docs.load_ulasim import process_data as process_ulasim_json
from load_docs.load_burslar import process_data as process_burslar_json
from load_docs.load_sik_sorulan_sorular import process_data as process_sik_sorulan_sorular_json
from load_docs.load_pru_brosur import process_data as process_pru_brosur_md

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
    elif file_name_lower == "ders_koordinasyonlugu.json":
        return "ders_koordinasyonlugu"
    elif file_name_lower == "pru_ek_sinav_hakki.json":
        return "pru_ek_sinav_hakki"
    elif file_name_lower == "ingilizce_hazirlik_yonetmeligi.json":
        return "ingilizce_hazirlik_yonetmeligi"
    elif file_name_lower == "lisans_onlisans_egitim_sinav_yonetmeligi.json":
        return "lisans_onlisans_egitim_sinav_yonetmeligi"
    elif file_name_lower == "uniforma_yonetmeligi.json":
        return "uniforma_yonetmeligi"
    elif file_name_lower == "erasmus_universiteleri.json":
        return "erasmus_universiteleri"
    elif file_name_lower == "kampus_olanaklari.json":
        return "kampus_olanaklari"
    elif file_name_lower == "siralamalar.json":
        return "siralamalar"
    elif file_name_lower == "ucretler.json":
        return "ucretler"
    elif file_name_lower == "ulasim.json":
        return "ulasim"
    elif file_name_lower == "burslar.json":
        return "burslar"
    elif file_name_lower == "sik_sorulan_sorular.json":
        return "sik_sorulan_sorular"
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
    md_files = glob.glob(os.path.join(data_dir, "*.md"))

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
            elif json_type == "ders_koordinasyonlugu":
                docs = process_ders_koordinasyonu_json(data, file_name)
            elif json_type == "pru_ek_sinav_hakki":
                docs = process_ek_sinav_hakki_json(data, file_name)
            elif json_type == "ingilizce_hazirlik_yonetmeligi":
                docs = process_ingilizce_yonetmeligi_json(data, file_name)
            elif json_type == "lisans_onlisans_egitim_sinav_yonetmeligi":
                docs = process_lisans_onlisans_json(data, file_name)
            elif json_type == "uniforma_yonetmeligi":
                docs = process_uniforma_yonetmeligi_json(data, file_name)
            elif json_type == "erasmus_universiteleri":
                docs = process_erasmus_json(data, file_name)
            elif json_type == "kampus_olanaklari":
                docs = process_kampus_json(data, file_name)
            elif json_type == "siralamalar":
                docs = process_siralamalar_json(data, file_name)
            elif json_type == "ucretler":
                docs = process_ucretler_json(data, file_name)
            elif json_type == "ulasim":
                docs = process_ulasim_json(data, file_name)
            elif json_type == "burslar":
                docs = process_burslar_json(data, file_name)
            elif json_type == "sik_sorulan_sorular":
                docs = process_sik_sorulan_sorular_json(data, file_name)
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
    
    # Process MD files
    for md_file in md_files:
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                md_content = f.read()
            
            file_name = os.path.basename(md_file)
            print(f"[DEBUG] Loaded {file_name}")
            
            # Process Markdown file
            if "pru_brosur" in file_name.lower():
                docs = process_pru_brosur_md(md_content, file_name)
            else:
                # İleriki aşamada farklı markdown dosya tipleri için burada işleme eklenebilir
                print(f"[WARNING] Unknown MD file type {file_name}, skipping...")
                continue
            
            # Filter out duplicates based on content hash
            for doc in docs:
                if doc.metadata["hash"] not in processed_hashes:
                    processed_hashes.add(doc.metadata["hash"])
                    all_docs.append(doc)
                    
        except FileNotFoundError:
            print(f"❌ {os.path.basename(md_file)} not found.")
        except Exception as e:
            print(f"❌ Error processing {os.path.basename(md_file)}: {e}")
    
    print(f"[i] Total {len(all_docs)} unique documents loaded")
    return all_docs