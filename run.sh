results=./results
rep_history=./final-report/history
report=./final-report

rm -rf $results # Удалить папку с результатами
pytest --alluredir=$results # Запустить тесты
mv $rep_history $results # Перенести историю в результаты
rm -rf $report # Удалить отчет
allure generate $results -o $report # Сгенерировать отчет


Для Windows 10/11
# Очистка предыдущих результатов
rmdir /s /q results 2>nul

# Запуск тестов
pytest --alluredir=results

# Генерация отчета
allure generate results -o final-report --clean

# Открыть отчет в браузере
allure serve results