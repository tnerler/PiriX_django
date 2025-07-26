from langchain.schema import Document
import hashlib
from typing import List, Dict, Any
import json
from datetime import datetime

def compute_hash(content: str) -> str:
    """
    İçeriğin benzersiz bir hash değerini hesaplar.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def process_data(data: dict, source_file: str) -> List[Document]:
    """
    Piri Reis Üniversitesi ücretleri JSON verisini işleyerek 
    LangChain Document nesnelerine dönüştürür.
    
    Args:
        data: Yüklenen JSON verisi.
        source_file: Kaynak dosya adı.
        
    Returns:
        Document nesnelerinden oluşan bir liste.
    """
    documents = []
    current_date = "2025-07-25 08:12:49"  # UTC format
    user_login = "tnerler"
    
    # Ana bilgileri al
    doc_title = data.get("document_title", "")
    document_date = data.get("document_date", "")
    metadata = data.get("metadata", {})
    university_name = metadata.get("university_name", "Piri Reis Üniversitesi")
    academic_year = metadata.get("academic_year", "")
    
    # Tüm ücret bilgilerini içeren ana doküman oluştur
    full_content = f"{doc_title}\n\n"
    full_content += f"Akademik Yıl: {academic_year}\n"
    full_content += f"Son Güncelleme: {document_date}\n\n"
    
    # Ücret kategorilerini ekle
    for category in data.get("fee_categories", []):
        category_name = category.get("category_name", "")
        programs = category.get("programs", [])
        
        full_content += f"## {category_name}\n\n"
        
        for program in programs:
            program_name = program.get("program_name", "")
            program_level = program.get("program_level", "")
            faculty = program.get("faculty", "")
            
            if faculty:
                full_content += f"### {program_name} ({faculty})\n\n"
            else:
                full_content += f"### {program_name}\n\n"
                
            payment_options = program.get("payment_options", [])
            
            for payment_option in payment_options:
                payment_type = payment_option.get("payment_type", "")
                full_content += f"#### {payment_type} Ödeme\n\n"
                
                full_content += "| Burs Durumu | Ücret | Vergi Durumu |\n"
                full_content += "|-------------|-------|-------------|\n"
                
                for scholarship_option in payment_option.get("scholarship_options", []):
                    scholarship = scholarship_option.get("scholarship", "")
                    fee = scholarship_option.get("fee", 0)
                    tax_info = scholarship_option.get("tax_info", "")
                    
                    # Ücret formatını düzenle (1.000 TL gibi)
                    formatted_fee = f"{fee:,}".replace(",", ".")
                    
                    full_content += f"| {scholarship} | {formatted_fee} TL | {tax_info} |\n"
                
                full_content += "\n"
            
            full_content += "\n"
    
    # Tam doküman için bir Document oluştur
    full_hash = compute_hash(full_content)
    documents.append(Document(
        page_content=full_content,
        metadata={
            "hash": full_hash,
            "title": doc_title,
            "university": university_name,
            "academic_year": academic_year,
            "source": source_file,
            "document_type": "ucretler_tam",
            "processed_date": current_date,
            "processed_by": user_login
        }
    ))
    
    # Kategori bazlı dokümanlar oluştur (Ön Lisans ve Lisans ayrı ayrı)
    for category in data.get("fee_categories", []):
        category_name = category.get("category_name", "")
        programs = category.get("programs", [])
        
        category_content = f"{university_name} - {category_name} - {academic_year} Eğitim Ücretleri\n\n"
        
        for program in programs:
            program_name = program.get("program_name", "")
            faculty = program.get("faculty", "")
            
            if faculty:
                category_content += f"## {program_name} ({faculty})\n\n"
            else:
                category_content += f"## {program_name}\n\n"
            
            payment_options = program.get("payment_options", [])
            
            for payment_option in payment_options:
                payment_type = payment_option.get("payment_type", "")
                category_content += f"### {payment_type} Ödeme\n\n"
                
                category_content += "| Burs Durumu | Ücret | Vergi Durumu |\n"
                category_content += "|-------------|-------|-------------|\n"
                
                for scholarship_option in payment_option.get("scholarship_options", []):
                    scholarship = scholarship_option.get("scholarship", "")
                    fee = scholarship_option.get("fee", 0)
                    tax_info = scholarship_option.get("tax_info", "")
                    
                    # Ücret formatını düzenle (1.000 TL gibi)
                    formatted_fee = f"{fee:,}".replace(",", ".")
                    
                    category_content += f"| {scholarship} | {formatted_fee} TL | {tax_info} |\n"
                
                category_content += "\n"
            
            category_content += "\n"
        
        category_hash = compute_hash(category_content)
        documents.append(Document(
            page_content=category_content,
            metadata={
                "hash": category_hash,
                "title": f"{university_name} - {category_name} - {academic_year} Eğitim Ücretleri",
                "university": university_name,
                "category": category_name,
                "academic_year": academic_year,
                "source": source_file,
                "document_type": "ucretler_kategori",
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Program bazlı dokümanlar oluştur
    for category in data.get("fee_categories", []):
        category_name = category.get("category_name", "")
        programs = category.get("programs", [])
        
        for program in programs:
            program_name = program.get("program_name", "")
            program_level = program.get("program_level", "")
            faculty = program.get("faculty", "")
            
            program_content = f"{university_name} - {program_name} - {academic_year} Eğitim Ücretleri\n\n"
            program_content += f"Kategori: {category_name}\n"
            
            if faculty:
                program_content += f"Fakülte: {faculty}\n"
            
            program_content += "\n"
            
            payment_options = program.get("payment_options", [])
            
            # Peşin ve taksitli ödeme bilgilerini karşılaştırmalı olarak göster
            program_content += "## Ödeme Seçenekleri\n\n"
            
            # Peşin ödeme bilgilerini tabloya ekle
            pesin_options = next((opt for opt in payment_options if opt.get("payment_type") == "Peşin"), {})
            taksit_options = next((opt for opt in payment_options if opt.get("payment_type") == "Taksitli"), {})
            
            program_content += "| Burs Durumu | Peşin Ödeme | Taksitli Ödeme | Fark |\n"
            program_content += "|-------------|-------------|---------------|------|\n"
            
            pesin_scholarship_options = pesin_options.get("scholarship_options", [])
            taksit_scholarship_options = taksit_options.get("scholarship_options", [])
            
            # Burs türlerini eşleştir ve karşılaştır
            for i, pesin_opt in enumerate(pesin_scholarship_options):
                if i < len(taksit_scholarship_options):
                    taksit_opt = taksit_scholarship_options[i]
                    
                    scholarship = pesin_opt.get("scholarship", "")
                    pesin_fee = pesin_opt.get("fee", 0)
                    taksit_fee = taksit_opt.get("fee", 0)
                    fark = taksit_fee - pesin_fee
                    
                    # Ücret formatını düzenle
                    formatted_pesin = f"{pesin_fee:,}".replace(",", ".")
                    formatted_taksit = f"{taksit_fee:,}".replace(",", ".")
                    formatted_fark = f"{fark:,}".replace(",", ".")
                    
                    program_content += f"| {scholarship} | {formatted_pesin} TL | {formatted_taksit} TL | {formatted_fark} TL |\n"
            
            program_content += "\n"
            program_content += "Not: Ücretlere %10 KDV dahil değildir.\n\n"
            
            # Her ödeme seçeneği için detaylı bilgi
            for payment_option in payment_options:
                payment_type = payment_option.get("payment_type", "")
                program_content += f"## {payment_type} Ödeme Detayları\n\n"
                
                for scholarship_option in payment_option.get("scholarship_options", []):
                    scholarship = scholarship_option.get("scholarship", "")
                    fee = scholarship_option.get("fee", 0)
                    tax_info = scholarship_option.get("tax_info", "")
                    
                    # KDV dahil ücret hesapla
                    kdv_dahil = fee * 1.10
                    
                    # Ücret formatını düzenle
                    formatted_fee = f"{fee:,}".replace(",", ".")
                    formatted_kdv = f"{kdv_dahil:,.2f}".replace(",", ".")
                    
                    program_content += f"**{scholarship}**\n"
                    program_content += f"- KDV Hariç: {formatted_fee} TL\n"
                    program_content += f"- KDV Dahil: {formatted_kdv} TL\n\n"
            
            program_hash = compute_hash(program_content)
            documents.append(Document(
                page_content=program_content,
                metadata={
                    "hash": program_hash,
                    "title": f"{university_name} - {program_name} - {academic_year} Eğitim Ücretleri",
                    "university": university_name,
                    "program": program_name,
                    "program_level": program_level,
                    "faculty": faculty,
                    "category": category_name,
                    "academic_year": academic_year,
                    "source": source_file,
                    "document_type": "ucretler_program",
                    "processed_date": current_date,
                    "processed_by": user_login
                }
            ))
    
    # Burs türleri bazlı dokümanlar oluştur
    burs_turleri = ["%50 ÖSYM BURSU + %20 TERCİH İNDİRİMİ", "%50 ÖSYM BURSU", "ÜCRETLİ + %20 TERCİH İNDİRİMİ", "ÜCRETLİ"]
    
    for burs_turu in burs_turleri:
        burs_content = f"{university_name} - {burs_turu} - {academic_year} Eğitim Ücretleri\n\n"
        
        # Lisans programları için tablo
        lisans_programs = []
        for category in data.get("fee_categories", []):
            if category.get("category_name") == "Lisans Programları":
                for program in category.get("programs", []):
                    program_name = program.get("program_name", "")
                    faculty = program.get("faculty", "")
                    
                    for payment_option in program.get("payment_options", []):
                        payment_type = payment_option.get("payment_type", "")
                        
                        for scholarship_option in payment_option.get("scholarship_options", []):
                            if scholarship_option.get("scholarship") == burs_turu:
                                fee = scholarship_option.get("fee", 0)
                                
                                lisans_programs.append({
                                    "program_name": program_name,
                                    "faculty": faculty,
                                    "payment_type": payment_type,
                                    "fee": fee
                                })
        
        if lisans_programs:
            burs_content += "## Lisans Programları\n\n"
            burs_content += "| Program Adı | Fakülte | Ödeme Tipi | Ücret |\n"
            burs_content += "|------------|--------|------------|-------|\n"
            
            for program in lisans_programs:
                program_name = program.get("program_name", "")
                faculty = program.get("faculty", "")
                payment_type = program.get("payment_type", "")
                fee = program.get("fee", 0)
                
                formatted_fee = f"{fee:,}".replace(",", ".")
                burs_content += f"| {program_name} | {faculty} | {payment_type} | {formatted_fee} TL |\n"
            
            burs_content += "\n"
        
        # Ön Lisans programları için tablo
        onlisans_programs = []
        for category in data.get("fee_categories", []):
            if category.get("category_name") == "Ön Lisans Programları":
                for program in category.get("programs", []):
                    program_name = program.get("program_name", "")
                    
                    for payment_option in program.get("payment_options", []):
                        payment_type = payment_option.get("payment_type", "")
                        
                        for scholarship_option in payment_option.get("scholarship_options", []):
                            if scholarship_option.get("scholarship") == burs_turu:
                                fee = scholarship_option.get("fee", 0)
                                
                                onlisans_programs.append({
                                    "program_name": program_name,
                                    "payment_type": payment_type,
                                    "fee": fee
                                })
        
        if onlisans_programs:
            burs_content += "## Ön Lisans Programları\n\n"
            burs_content += "| Program Adı | Ödeme Tipi | Ücret |\n"
            burs_content += "|------------|------------|-------|\n"
            
            for program in onlisans_programs:
                program_name = program.get("program_name", "")
                payment_type = program.get("payment_type", "")
                fee = program.get("fee", 0)
                
                formatted_fee = f"{fee:,}".replace(",", ".")
                burs_content += f"| {program_name} | {payment_type} | {formatted_fee} TL |\n"
            
            burs_content += "\n"
        
        burs_hash = compute_hash(burs_content)
        documents.append(Document(
            page_content=burs_content,
            metadata={
                "hash": burs_hash,
                "title": f"{university_name} - {burs_turu} - {academic_year} Eğitim Ücretleri",
                "university": university_name,
                "scholarship_type": burs_turu,
                "academic_year": academic_year,
                "source": source_file,
                "document_type": "ucretler_burs",
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Sık sorulan sorular formatında bir doküman
    faq_content = f"# {university_name} {academic_year} Eğitim Yılı Ücretleri Sıkça Sorulan Sorular\n\n"
    
    faq_content += "## Piri Reis Üniversitesi'nde eğitim ücretleri ne kadardır?\n\n"
    faq_content += f"Piri Reis Üniversitesi'nde {academic_year} akademik yılı için eğitim ücretleri, programlara ve burs durumlarına göre değişiklik göstermektedir. Lisans programlarında peşin ödeme seçeneğinde ücretler 260.000 TL ile 650.000 TL arasında, ön lisans programlarında ise 170.000 TL ile 425.000 TL arasında değişmektedir. Ücretlere %10 KDV dahil değildir.\n\n"
    
    faq_content += "## Hangi burs imkanları bulunmaktadır?\n\n"
    faq_content += "Piri Reis Üniversitesi'nde şu burs seçenekleri bulunmaktadır:\n"
    faq_content += "- %50 ÖSYM Bursu + %20 Tercih İndirimi\n"
    faq_content += "- %50 ÖSYM Bursu\n"
    faq_content += "- Ücretli + %20 Tercih İndirimi\n"
    faq_content += "- Ücretli\n\n"
    
    faq_content += "## Ödeme seçenekleri nelerdir?\n\n"
    faq_content += "Üniversite eğitim ücretlerini peşin veya taksitli ödeme seçenekleriyle ödeyebilirsiniz. Peşin ödemelerde, taksitli ödemeye göre daha avantajlı fiyatlar sunulmaktadır. Örneğin, lisans programlarında peşin ödeme ile taksitli ödeme arasında yaklaşık %20 fark bulunmaktadır.\n\n"
    
    faq_content += "## En uygun ücretli program hangisidir?\n\n"
    faq_content += "En uygun ücretli programlar, %50 ÖSYM Bursu + %20 Tercih İndirimi ile ön lisans programları için peşin ödemede 170.000 TL'dir. Lisans programları için ise aynı burs koşullarında peşin ödemede 260.000 TL'dir.\n\n"
    
    faq_content += "## KDV oranı ne kadardır?\n\n"
    faq_content += "Tüm eğitim ücretlerine %10 KDV ilave edilir. Belirtilen ücretlere KDV dahil değildir.\n\n"
    
    faq_hash = compute_hash(faq_content)
    documents.append(Document(
        page_content=faq_content,
        metadata={
            "hash": faq_hash,
            "title": f"{university_name} {academic_year} Eğitim Ücretleri Sıkça Sorulan Sorular",
            "university": university_name,
            "academic_year": academic_year,
            "source": source_file,
            "document_type": "ucretler_sss",
            "processed_date": current_date,
            "processed_by": user_login
        }
    ))
    
    return documents