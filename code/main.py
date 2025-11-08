#!/usr/bin/env python3
"""
Инструмент визуализации графа зависимостей пакетов
Этап 2: Сбор данных
"""

import argparse
import sys
import os
import json
import urllib.request
import urllib.error

class DependencyVisualizer:
    def __init__(self):
        self.config = {}
        
    def parse_arguments(self):
        """Парсинг аргументов командной строки"""
        parser = argparse.ArgumentParser(
            description='Инструмент визуализации графа зависимостей пакетов',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        parser.add_argument(
            '--package',
            type=str,
            required=True,
            help='Имя анализируемого пакета'
        )
        
        parser.add_argument(
            '--source',
            type=str,
            required=True,
            help='URL-адрес репозитория или путь к файлу тестового репозитория'
        )
        
        parser.add_argument(
            '--test-mode',
            action='store_true',
            default=False,
            help='Режим работы с тестовым репозиторием'
        )
        
        parser.add_argument(
            '--output',
            type=str,
            default='dependency_graph.png',
            help='Имя сгенерированного файла с изображением графа'
        )
        
        parser.add_argument(
            '--ascii-tree',
            action='store_true',
            default=False,
            help='Режим вывода зависимостей в формате ASCII-дерева'
        )
        
        return parser.parse_args()
    
    def validate_arguments(self, args):
        """Валидация аргументов командной строки"""
        errors = []
        
        if not args.package or not args.package.strip():
            errors.append("Имя пакета не может быть пустым")
        
        if not args.source or not args.source.strip():
            errors.append("Источник (URL или путь к файлу) не может быть пустым")
        
        if not args.output or not args.output.strip():
            errors.append("Имя выходного файла не может быть пустым")
        
        if args.test_mode and not os.path.exists(args.source):
            errors.append(f"Тестовый файл не найден: {args.source}")
        
        return errors
    
    def get_package_info_from_url(self, package_name, url):
        """Получение информации о пакете из npm реестра"""
        try:
            # Формируем URL для npm реестра
            npm_registry_url = f"https://registry.npmjs.org/{package_name}"
            
            print(f"Запрос информации о пакете: {npm_registry_url}")
            
            with urllib.request.urlopen(npm_registry_url) as response:
                data = json.loads(response.read().decode())
                
            # Получаем последнюю версию
            if 'dist-tags' in data and 'latest' in data['dist-tags']:
                latest_version = data['dist-tags']['latest']
            else:
                # Берем первую доступную версию
                latest_version = list(data.get('versions', {}).keys())[0]
            
            # Получаем зависимости для последней версии
            version_data = data['versions'][latest_version]
            dependencies = version_data.get('dependencies', {})
            
            return {
                'name': package_name,
                'version': latest_version,
                'dependencies': dependencies
            }
            
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise Exception(f"Пакет '{package_name}' не найден в npm реестре")
            else:
                raise Exception(f"Ошибка HTTP при запросе пакета: {e}")
        except urllib.error.URLError as e:
            raise Exception(f"Ошибка сети: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"Ошибка парсинга JSON: {e}")
        except Exception as e:
            raise Exception(f"Неизвестная ошибка при получении информации о пакете: {e}")
    
    def get_package_info_from_file(self, package_name, file_path):
        """Получение информации о пакете из файла (для тестового режима)"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if package_name not in data:
                raise Exception(f"Пакет '{package_name}' не найден в тестовом файле")
            
            package_info = data[package_name]
            return {
                'name': package_name,
                'version': package_info.get('version', '1.0.0'),
                'dependencies': package_info.get('dependencies', {})
            }
            
        except FileNotFoundError:
            raise Exception(f"Тестовый файл не найден: {file_path}")
        except json.JSONDecodeError:
            raise Exception(f"Ошибка парсинга JSON в файле: {file_path}")
        except Exception as e:
            raise Exception(f"Ошибка при чтении тестового файла: {e}")
    
    def get_direct_dependencies(self, args):
        """Получение прямых зависимостей пакета"""
        if args.test_mode:
            package_info = self.get_package_info_from_file(args.package, args.source)
        else:
            package_info = self.get_package_info_from_url(args.package, args.source)
        
        return package_info['dependencies']
    
    def print_direct_dependencies(self, dependencies):
        """Вывод прямых зависимостей на экран"""
        if not dependencies:
            print("Прямые зависимости не найдены")
            return
        
        print(f"\nПрямые зависимости пакета:")
        print("-" * 30)
        for dep_name, dep_version in dependencies.items():
            print(f"  {dep_name}: {dep_version}")
        print("-" * 30)
    
    def print_configuration(self, args):
        """Вывод конфигурации в формате ключ-значение"""
        print("Конфигурация приложения:")
        print("=" * 40)
        print(f"Имя анализируемого пакета: {args.package}")
        print(f"Источник данных: {args.source}")
        print(f"Режим тестирования: {'Включен' if args.test_mode else 'Выключен'}")
        print(f"Выходной файл: {args.output}")
        print(f"Режим ASCII-дерева: {'Включен' if args.ascii_tree else 'Выключен'}")
        print("=" * 40)
    
    def run(self):
        """Основной метод запуска приложения"""
        try:
            # Парсинг аргументов
            args = self.parse_arguments()
            
            # Валидация аргументов
            errors = self.validate_arguments(args)
            if errors:
                print("Ошибки конфигурации:")
                for error in errors:
                    print(f"  - {error}")
                sys.exit(1)
            
            # Вывод конфигурации
            self.print_configuration(args)
            
            # Получение и вывод прямых зависимостей
            dependencies = self.get_direct_dependencies(args)
            self.print_direct_dependencies(dependencies)
            
            print("\nЭтап 2 завершен успешно!")
            
        except Exception as e:
            print(f"Ошибка: {e}")
            sys.exit(1)

if __name__ == "__main__":
    visualizer = DependencyVisualizer()
    visualizer.run()