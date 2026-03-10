import PyInstaller.__main__
import os
import sys

def build_app():
    # Определяем базовую директорию проекта
    base_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(base_dir, 'run.py')
    
    if not os.path.exists(script_path):
        print(f"❌ Ошибка: Файл {script_path} не найден!")
        return

    print(f"🚀 Запуск сборки из: {base_dir}")

    PyInstaller.__main__.run([
        script_path,
        '--name=MedAnalyzeMonitor',
        '--onefile',
        '--windowed',
        # Важно: используем полные пути для данных
        f'--add-data={os.path.join(base_dir, "frontend")}{os.pathsep}frontend',
        f'--add-data={os.path.join(base_dir, "backend")}{os.pathsep}backend',
        '--hidden-import=uvicorn.logging',
        '--hidden-import=uvicorn.loops.auto',
        '--hidden-import=uvicorn.protocols.http.auto',
        '--noconfirm',
        '--clean',
        '--log-level=DEBUG' # Добавляем лог для поиска причины
    ])

if __name__ == "__main__":
    build_app()