import fitz
import re
from database import add_word_to_index, clear_user_index, get_user_id

def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        pages_text = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            if text:
                pages_text.append((page_num + 1, text))
        
        doc.close()
        return pages_text
    except Exception as e:
        print(f"Грешка при четене на {pdf_path}: {e}")
        return []

def get_unique_words(text):
    words = re.findall(r'\b[a-zа-я]+\b', text.lower())
    return list(set(words))

def index_pdf_folder(folder_path, username, progress_callback=None):
    import os
    
    user_id = get_user_id(username)
    if not user_id:
        return 0, 0, "Потребителят не е намерен!"
    
    clear_user_index(user_id)
    
    pdf_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    
    if not pdf_files:
        return 0, 0, "Няма PDF файлове в избраната папка!"
    
    successful = 0
    failed = 0
    
    for idx, pdf_path in enumerate(pdf_files):
        filename = os.path.basename(pdf_path)
        
        if progress_callback:
            progress_callback(idx + 1, len(pdf_files), filename)
        
        pages = extract_text_from_pdf(pdf_path)
        
        if not pages:
            failed += 1
            continue
        
        for page_num, text in pages:
            unique_words = get_unique_words(text)
            
            for word in unique_words:
                if len(word) < 3 or len(word) > 50:
                    continue
                    
                add_word_to_index(user_id, filename, page_num, word)
        
        successful += 1
    
    return successful, failed, f"Готово! Индексирани: {successful}, Неуспешни: {failed}"