"""
Скрипт запуска приложения Мониторинг конкурентов
"""
import uvicorn
import logging
import os
import sys

# Добавляем текущую директорию в путь поиска модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.config import settings

# Настраиваем уровень логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("competitor_monitor")

if __name__ == "__main__":
    # Проверка: существует ли файл backend/main.py
    main_path = os.path.join("backend", "main.py")
    if not os.path.exists(main_path):
        print(f"❌ ОШИБКА: Не найден файл {main_path}")
        print("Убедитесь, что вы запускаете run.py из корневой папки проекта.")
        sys.exit(1)

    print()
    print("=" * 60)
    print("🚀 МОНИТОРИНГ КОНКУРЕНТОВ - AI Ассистент")
    print("=" * 60)
    print()
    print(f"📍 Веб-интерфейс:   http://localhost:{settings.api_port}")
    print(f"📚 Документация:    http://localhost:{settings.api_port}/docs")
    print(f"📖 ReDoc:           http://localhost:{settings.api_port}/redoc")
    print()
    print(f"🤖 Модель текста:   {settings.openai_model}")
    print(f"👁️ Модель vision:   {settings.openai_vision_model}")
    print(f"🔑 API ключ:        {'✓ Настроен' if settings.proxy_api_key else '✗ НЕ ЗАДАН!'}")
    print()
    print("-" * 60)
    print("Логи запросов будут отображаться ниже...")
    print("-" * 60)
    print()
    
    # Запуск сервера
    uvicorn.run(
        "backend.main:app",  # Путь к объекту FastAPI
        host=settings.api_host,
        port=settings.api_port,
        reload=True,         # Автоматическая перезагрузка при изменении кода
        log_level="info"
    )