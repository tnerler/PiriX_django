import json
from langchain.schema import Document
import hashlib
import os
from typing import List, Dict, Any
import glob

def compute_hash(content: str) -> str:
    """
    Computes a SHA256 hash from content to prevent duplicate document loading.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def process_data(data: Dict[str, Any], source_file: str) -> List[Document]:
    """
    Process the JSON structure for the Maritime Vocational School (DMYO).
    Extracts meaningful content and organizes it into searchable documents.
    """
    documents = []
    school_name = data.get("school_name", "")
    
    # Process general sections about the school
    if "sections" in data:
        sections = data["sections"]
        
        # About section with director message
        if "about" in sections:
            about = sections["about"]
            
            # Director message
            if "director_message" in about:
                dir_msg = about["director_message"]
                title = dir_msg.get("title", "Müdür Mesajı")
                content = dir_msg.get("content", "")
                
                if content:
                    text = f"{school_name} - {title}\n\n{content}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "school": school_name,
                            "section": "director_message",
                            "source": source_file
                        }
                    ))
            
            # History section
            if "history" in about:
                history = about["history"]
                title = history.get("title", "Tarihçe")
                content = history.get("content", "")
                
                if content:
                    text = f"{school_name} - {title}\n\n{content}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "school": school_name,
                            "section": "history",
                            "source": source_file
                        }
                    ))
            
            # Mission vision section
            if "mission_vision" in about:
                mission_vision = about["mission_vision"]
                title = mission_vision.get("title", "Misyon-Vizyon")
                content = mission_vision.get("content", "")
                
                if content:
                    text = f"{school_name} - {title}\n\n{content}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "school": school_name,
                            "section": "mission_vision",
                            "source": source_file
                        }
                    ))
            
            # Other about sections
            for key in ["quality", "research", "internationalization"]:
                if key in about:
                    section = about[key]
                    title = section.get("title", key.capitalize())
                    content = section.get("content", "")
                    
                    if content:
                        text = f"{school_name} - {title}\n\n{content}"
                        doc_hash = compute_hash(text)
                        documents.append(Document(
                            page_content=text,
                            metadata={
                                "hash": doc_hash,
                                "school": school_name,
                                "section": key,
                                "source": source_file
                            }
                        ))
        
        # Management sections
        if "management" in sections:
            management = sections["management"]
            
            # School management
            if "school_management" in management:
                mgmt = management["school_management"]
                title = mgmt.get("title", "Yüksekokulu Yönetimi")
                members = mgmt.get("members", [])
                
                if members:
                    members_text = "\n".join([f"{m.get('name', '')}: {m.get('title', '')}" for m in members])
                    text = f"{school_name} - {title}\n\n{members_text}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "school": school_name,
                            "section": "school_management",
                            "source": source_file
                        }
                    ))
            
            # School board
            if "school_board" in management:
                board = management["school_board"]
                title = board.get("title", "Yüksekokul Kurulu")
                members = board.get("members", [])
                
                if members:
                    members_text = "\n".join([f"{m.get('name', '')}: {m.get('title', '')}" for m in members])
                    text = f"{school_name} - {title}\n\n{members_text}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "school": school_name,
                            "section": "school_board",
                            "source": source_file
                        }
                    ))
            
            # Executive board
            if "executive_board" in management:
                exec_board = management["executive_board"]
                title = exec_board.get("title", "Yüksekokul Yönetim Kurulu")
                members = exec_board.get("members", [])
                
                if members:
                    members_text = "\n".join([f"{m.get('name', '')}: {m.get('title', '')}" for m in members])
                    text = f"{school_name} - {title}\n\n{members_text}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "school": school_name,
                            "section": "executive_board",
                            "source": source_file
                        }
                    ))
            
            # Department and program heads
            if "department_program_heads" in management:
                dept_heads = management["department_program_heads"]
                title = dept_heads.get("title", "Bölüm Başkanları ve Program Başkanları Sorumluları")
                departments = dept_heads.get("departments", [])
                
                if departments:
                    dept_text = ""
                    for dept in departments:
                        dept_text += f"Bölüm: {dept.get('name', '')}\n"
                        dept_text += f"Bölüm Başkanı: {dept.get('head', '')}\n"
                        
                        if "programs" in dept:
                            dept_text += "Programlar:\n"
                            for prog in dept["programs"]:
                                dept_text += f"- {prog.get('name', '')}: {prog.get('responsible', '')}\n"
                        dept_text += "\n"
                    
                    text = f"{school_name} - {title}\n\n{dept_text}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "school": school_name,
                            "section": "department_program_heads",
                            "source": source_file
                        }
                    ))
        
        # Academic staff by department
        if "academic_staff" in sections:
            ac_staff = sections["academic_staff"]
            title = ac_staff.get("title", "Akademik Kadro")
            
            if "departments" in ac_staff:
                depts = ac_staff["departments"]
                
                for dept_key, dept_value in depts.items():
                    dept_name = dept_value.get("name", dept_key)
                    
                    if "programs" in dept_value:
                        programs = dept_value["programs"]
                        
                        for prog_key, prog_value in programs.items():
                            prog_name = prog_value.get("name", prog_key)
                            staff = prog_value.get("staff", [])
                            
                            if staff:
                                staff_text = "\n".join([f"{s.get('rank', '')} {s.get('name', '')}" for s in staff])
                                text = f"{school_name} - {dept_name} - {prog_name} - Akademik Kadro\n\n{staff_text}"
                                doc_hash = compute_hash(text)
                                documents.append(Document(
                                    page_content=text,
                                    metadata={
                                        "hash": doc_hash,
                                        "school": school_name,
                                        "department": dept_name,
                                        "program": prog_name,
                                        "section": "academic_staff",
                                        "source": source_file
                                    }
                                ))
    
    # Process individual programs
    if "programs" in data:
        programs = data["programs"]
        
        for prog_key, prog_value in programs.items():
            prog_name = prog_value.get("name", prog_key)
            
            # Program about section
            if "about" in prog_value:
                about = prog_value["about"]
                title = about.get("title", "Program Hakkında")
                
                # Main content
                content = about.get("content", "")
                if content:
                    # Check for career_opportunities and vertical_transfer in content
                    career_content = about.get("career_opportunities", "")
                    
                    # Combine all content
                    full_content = content
                    if career_content:
                        full_content += f"\n\nKariyer Fırsatları:\n{career_content}"
                    
                    # Vertical transfer section
                    if "vertical_transfer" in about:
                        vt = about["vertical_transfer"]
                        vt_title = vt.get("title", "Dikey Geçiş İmkanları")
                        vt_content = vt.get("content", "")
                        vt_programs = vt.get("programs", [])
                        vt_additional = vt.get("additional_info", "")
                        
                        vt_text = f"{vt_title}:\n{vt_content}\n"
                        if vt_programs:
                            vt_text += "- " + "\n- ".join(vt_programs) + "\n"
                        if vt_additional:
                            vt_text += vt_additional
                        
                        full_content += f"\n\n{vt_text}"
                    
                    text = f"{school_name} - {prog_name} - {title}\n\n{full_content}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "school": school_name,
                            "program": prog_name,
                            "section": "about",
                            "source": source_file
                        }
                    ))
            
            # Program head message
            if "program_head_message" in prog_value:
                head_msg = prog_value["program_head_message"]
                title = head_msg.get("title", "Program Sorumlusunun Mesajı")
                content = head_msg.get("content", "")
                author = head_msg.get("author", "")
                author_title = head_msg.get("title_author", "")
                
                if content:
                    message_text = content
                    if author:
                        message_text += f"\n\n{author}"
                    if author_title:
                        message_text += f"\n{author_title}"
                    
                    text = f"{school_name} - {prog_name} - {title}\n\n{message_text}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "school": school_name,
                            "program": prog_name,
                            "section": "program_head_message",
                            "source": source_file
                        }
                    ))
            
            # Academic staff
            if "academic_staff" in prog_value:
                staff = prog_value["academic_staff"]
                
                if staff:
                    staff_text = "\n".join([s.get("name", "") for s in staff])
                    text = f"{school_name} - {prog_name} - Akademik Kadro\n\n{staff_text}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "school": school_name,
                            "program": prog_name,
                            "section": "academic_staff",
                            "source": source_file
                        }
                    ))
            
            # Other program sections
            for section_key in ["internship", "dual_major_minor", "student_clubs", "erasmus", "events", "news"]:
                if section_key in prog_value:
                    section = prog_value[section_key]
                    
                    if isinstance(section, dict):
                        title = section.get("title", section_key.replace("_", " ").capitalize())
                        content = section.get("content", "")
                        
                        if content:
                            text = f"{school_name} - {prog_name} - {title}\n\n{content}"
                            doc_hash = compute_hash(text)
                            documents.append(Document(
                                page_content=text,
                                metadata={
                                    "hash": doc_hash,
                                    "school": school_name,
                                    "program": prog_name,
                                    "section": section_key,
                                    "source": source_file
                                }
                            ))
            
            # Special case for Hybrid and Electric Vehicles program (inactive)
            if "note" in prog_value:
                note = prog_value.get("note", "")
                
                if note:
                    text = f"{school_name} - {prog_name}\n\nNot: {note}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "school": school_name,
                            "program": prog_name,
                            "section": "note",
                            "source": source_file
                        }
                    ))
    
    # Process contact information
    if "contact" in data:
        contact = data["contact"]
        title = contact.get("title", "İletişim")
        content = contact.get("content", "")
        
        if content:
            text = f"{school_name} - {title}\n\n{content}"
            doc_hash = compute_hash(text)
            documents.append(Document(
                page_content=text,
                metadata={
                    "hash": doc_hash,
                    "school": school_name,
                    "section": "contact",
                    "source": source_file
                }
            ))
    
    return documents