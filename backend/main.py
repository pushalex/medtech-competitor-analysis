import base64
from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os, fitz
import logging

# Твои импорты
from backend.services.openai_service import openai_service
from backend.services.history_service import history_service
from backend.services.parser_service import parser_service
from backend.models.schemas import TextAnalysisRequest, ParsedContent
from backend.config import settings

logger = logging.getLogger("competitor_monitor.main")

app = FastAPI()

# Монтируем статику (проверь, что папка frontend в корне)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def root():
    return FileResponse("frontend/index.html")

# --- АНАЛИЗ ТЕКСТА ---
@app.post("/analyze-text")
async def analyze_text(request: TextAnalysisRequest):
    try:
        analysis = await openai_service.analyze_text(request.text)
        history_service.add_entry("text", f"Текст: {request.text[:30]}...", analysis.summary)
        # Возвращаем summary напрямую для корректного отображения в app.js
        return {"success": True, "analysis": analysis.summary}
    except Exception as e:
        logger.error(f"Ошибка анализа текста: {e}")
        return {"success": False, "error": str(e)}

# --- АНАЛИЗ PDF ---
@app.post("/analyze-pdf")
async def analyze_pdf(file: UploadFile = File(...)):
    try:
        content = await file.read()
        text = ""
        # Извлекаем текст из PDF
        with fitz.open(stream=content, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        
        if not text.strip():
            return {"success": False, "error": "PDF файл пуст или не содержит текста"}

        analysis = await openai_service.analyze_text(text)
        history_service.add_entry("pdf", f"Файл: {file.filename}", analysis.summary)
        return {"success": True, "analysis": analysis.summary}
    except Exception as e:
        logger.error(f"Ошибка анализа PDF: {e}")
        return {"success": False, "error": str(e)}

# --- АНАЛИЗ ИЗОБРАЖЕНИЯ ---
@app.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    try:
        content = await file.read()
        image_base64 = base64.b64encode(content).decode('utf-8')
        
        # Вызываем Vision-анализ
        analysis = await openai_service.analyze_image(
            image_base64=image_base64,
            mime_type=file.content_type
        )
        
        # Сохраняем описание в историю
        history_service.add_entry("image", f"Изображение: {file.filename}", analysis.description)
        return {"success": True, "analysis": analysis.description}
    except Exception as e:
        logger.error(f"Ошибка анализа изображения: {e}")
        return {"success": False, "error": str(e)}

# --- ДЕМО-ПАРСИНГ ---
@app.get("/parsedemo")
async def parsedemo():
    """Демопарсинг сайтов конкурентов и возврат сводного анализа"""
    if not settings.competitor_urls:
        return {"success": False, "error": "В config.py не заданы competitor_urls"}
    
    final_reports = []
    
    for url in settings.competitor_urls:
        logger.info(f"Парсинг в процессе: {url}")
        # Получаем данные и скриншот
        title, h1, first_paragraph, screenshot_bytes, error = await parser_service.parse_url(url)
        
        if error:
            logger.warning(f"Ошибка при парсинге {url}: {error}")
            continue
            
        screenshot_b64 = parser_service.screenshot_to_base64(screenshot_bytes) if screenshot_bytes else ""
        
        # Анализируем скриншот через OpenAI
        analysis = await openai_service.analyze_website_screenshot(
            screenshot_base64=screenshot_b64,
            url=url,
            title=title,
            h1=h1,
            first_paragraph=first_paragraph,
        )
        
        if analysis and analysis.summary:
            history_service.add_entry("parse", f"URL: {url}", analysis.summary)
            final_reports.append(f"--- РЕЗУЛЬТАТ ДЛЯ {url} ---\n{analysis.summary}")
    
    if not final_reports:
        return {"success": False, "error": "Не удалось собрать данные ни с одного сайта"}

    # Склеиваем отчеты в одну строку, чтобы app.js вывел их на экран
    return {"success": True, "analysis": "\n\n".join(final_reports)}

# --- ИСТОРИЯ ---
@app.get("/get-history")
async def get_history():
    return history_service.get_history()