import fitz  # pymupdf
import re
from database import add_word_to_index, clear_user_index, get_user_id

def extract_text_from_pdf(pdf_path):
    """
    Извлича текст от PDF файл страница по страница.
    Връща списък от tuples: (страница_номер, текст)
    """
    try:
        doc = fitz.open(pdf_path)
        pages_text = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            # Почистване на текста
            text = re.sub(r'\s+', ' ', text)  # премахва излишни празни места
            text = text.strip()
            
            if text:  # добавя само ако има текст
                pages_text.append((page_num + 1, text))
        
        doc.close()
        return pages_text
    except Exception as e:
        print(f"Грешка при четене на {pdf_path}: {e}")
        return []

def get_unique_words(text):
    """
    Извлича уникалните думи от текст.
    Връща списък с уникални думи (малки букви, без препинателни знаци).
    """
    # Премахва препинателните знаци и цифри, оставя само букви
    words = re.findall(r'\b[a-zа-я]+\b', text.lower())
    return list(set(words))  # set = само уникални думи

def index_pdf_folder(folder_path, username, progress_callback=None):
    """
    Индексира всички PDF файлове в дадена папка.
    
    Параметри:
    - folder_path: път до папката с PDF-и
    - username: потребителско име (за чийто акаунт се индексира)
    - progress_callback: функция, която се вика за обновяване на прогреса
    
    Връща: (успешни_файлове, неуспешни_файлове)
    """
    import os
    
    user_id = get_user_id(username)
    if not user_id:
        return 0, 0, "Потребителят не е намерен!"
    
    # Изчистваме стария индекс на този потребител (или може да оставим и добавяме нови)
    # За по-просто - ще изчистваме всеки път при ново индексиране
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
        
        # Обновяваме прогреса, ако има callback функция
        if progress_callback:
            progress_callback(idx + 1, len(pdf_files), filename)
        
        # Извличаме текст от PDF
        pages = extract_text_from_pdf(pdf_path)
        
        if not pages:
            failed += 1
            continue
        
        # За всяка страница, вземаме уникалните думи и ги записваме в БД
        for page_num, text in pages:
            unique_words = get_unique_words(text)
            
            for word in unique_words:
                # Ако думата е твърде кратка или твърде дълга, я пропускаме
                if len(word) < 3 or len(word) > 50:
                    continue
                    
                add_word_to_index(user_id, filename, page_num, word)
        
        successful += 1
    
    return successful, failed, f"Готово! Индексирани: {successful}, Неуспешни: {failed}"