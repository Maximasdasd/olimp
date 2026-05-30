import subprocess
import sys

def run_tests():
    print("Запуск тестов проекта 'Олимпиадное движение'")
    print("=" * 50)
    
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--cov=app",
        "--cov-report=term-missing"
    ])
    
    print("\n" + "=" * 50)
    if result.returncode == 0:
        print("Все тесты пройдены успешно!")
    else:
        print("Некоторые тесты не пройдены")
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(run_tests())