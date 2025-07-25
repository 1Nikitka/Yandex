import mysql.connector
import json
import uuid
import datetime
import re
import logging
logger = logging.getLogger(__name__)
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import SearchForm
from django.contrib.auth.models import User  # для создания пользователя
from types import SimpleNamespace
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import SearchResult
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from .models import Rabota





DB_CONFIG = {
    'host': "mysql.alliance-pr0fi.myjino.ru",
    'port': 3306,
    'user': "047281260_123",
    'password': "Zxcvbnm2025",
    'database': "alliance-pr0fi_123"
}


@login_required
def search_view(request):
    saved = False
    user_id = str(request.user.id)
    history = []  # сюда загрузим историю запросов

    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            username = request.user.username
            command_id = str(uuid.uuid4())
            status = "waiting"
            form_data = form.cleaned_data
            form_data_json = json.dumps(form_data, ensure_ascii=False)
            created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Получаем значение keyword
            keyword = form_data.get("keywords", "unknown")

            try:
                print(f"▶️ Подключение к базе: {DB_CONFIG['host']}:{DB_CONFIG['port']} пользователем {DB_CONFIG['user']}")
                connection = mysql.connector.connect(**DB_CONFIG)
                cursor = connection.cursor()

                # Вставка в таблицу user
                insert_user_query = """
                    INSERT INTO user (user_id, username, command, status, Jsonaforma, created_at, result)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                result_json = json.dumps({}, ensure_ascii=False)  # Пустой JSON
                cursor.execute(insert_user_query, (
                    user_id, username, command_id, status, form_data_json, created_at, result_json
                ))

                # Вставка в таблицу search_history
                insert_history_query = """
                    INSERT INTO search_history (user_id, keyword, search_date)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(insert_history_query, (
                    user_id, keyword, created_at
                ))

                connection.commit()
                saved = True
                print("✅ Данные успешно сохранены в обе таблицы")

                return redirect('/')  # редирект после POST

            except mysql.connector.Error as err:
                print(f"❌ Ошибка подключения или вставки: {err}")
            finally:
                if cursor:
                    cursor.close()
                if connection:
                    connection.close()
                    print("▶️ Соединение с базой закрыто")

    else:
        form = SearchForm()

    # Загрузка истории запросов для текущего пользователя из базы
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)

        history_query = """
            SELECT keyword, search_date 
            FROM search_history 
            WHERE user_id = %s 
            ORDER BY search_date DESC 
            LIMIT 20
        """
        cursor.execute(history_query, (user_id,))
        history = cursor.fetchall()

    except mysql.connector.Error as e:
        print(f"❌ Ошибка при загрузке истории: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    # Передаём в шаблон форму, флаг сохранения и историю
    return render(request, 'main_app/index.html', {
        'form': form,
        'saved': saved,
        'history': history,
    })

def blank_page_2(request):
    titles = request.session.get('titles', [])
    saved = request.session.get('saved', False)

    def parse_resultZE_blocks(raw_text):
        result = []
        block_pattern = re.compile(
            r'id:\s*"(.*?)";\s*'
            r'Link_baza_json:\s*"(.*?)";\s*'
            r'Zagolovok_json_sait:\s*"(.*?)";\s*'
            r'SnipetL_baza:\s*"(.*?)";\s*'
            r'Email:\s*"(.*?)";\s*'
            r'phone:\s*"(.*?)";\s*'
            r'phone2:\s*"(.*?)";\s*'
            r'Sity:\s*"(.*?)";\s*'
            r'TIN:\s*"(.*?)";',
            re.DOTALL
        )
        matches = block_pattern.findall(raw_text)
        for match in matches:
            result.append({
                "id": match[0],
                "Link_baza_json": match[1],
                "Zagolovok_json_sait": match[2],
                "SnipetL_baza": match[3],
                "Email": match[4],
                "phone": match[5],
                "phone2": match[6],
                "Sity": match[7],
                "TIN": match[8]
            })
        return result

    user_id = getattr(request.user, 'id', None)
    if user_id is None:
        return render(request, 'main_app/blank_page_2.html', {
            'titles': titles,
            'saved': saved,
            'page_obj': [],
            'status': None,
            'logs': 'User ID not found.',
            'taken_work': [],
        })

    results = []
    status = None
    taken_work = []

    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)

        # --- Работа с таблицей user (обработка result и resultZE) ---
        query = "SELECT id, status, result, resultZE FROM user WHERE user_id = %s ORDER BY id DESC LIMIT 1"
        cursor.execute(query, (str(user_id),))
        user_row = cursor.fetchone()

        if user_row:
            status = user_row['status']
            record_id = user_row['id']
            raw_result = user_row.get('result') or '[]'
            raw_resultZE = user_row.get('resultZE') or ''

            try:
                parsed_result = json.loads(raw_result)
                if isinstance(parsed_result, dict):
                    parsed_result = [parsed_result]
            except Exception as e:
                print(f"❌ Ошибка при загрузке result: {e}")
                parsed_result = []

            parsed_resultZE = []
            if raw_resultZE.strip():
                try:
                    parsed_resultZE = parse_resultZE_blocks(raw_resultZE)
                    print(f"🔧 Обработано {len(parsed_resultZE)} новых блоков из resultZE")
                except Exception as e:
                    print(f"❌ Ошибка при парсинге resultZE: {e}")

            combined = [r for r in (parsed_result + parsed_resultZE) if isinstance(r, dict) and r]

            for record in combined:
                if 'SnipetL_baza' in record and isinstance(record['SnipetL_baza'], str):
                    record['SnipetL_baza'] = record['SnipetL_baza'][:200]

                email_raw = record.get("Email", "")
                email_pattern = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
                record["email_list"] = email_pattern.findall(email_raw)

                phone_raw = record.get("phone", "")
                if phone_raw:
                    parts = phone_raw.split('+')
                    record["phone_list"] = ['+' + p.strip() for p in parts if p.strip()]
                else:
                    record["phone_list"] = []

            # Обновляем поле result, очищаем resultZE
            update_query = "UPDATE user SET result = %s, resultZE = '' WHERE id = %s"
            cursor.execute(update_query, (json.dumps(combined, ensure_ascii=False), record_id))
            connection.commit()
            results = combined
        else:
            print("❗ Нет записей пользователя в таблице user")

        # --- Взятые в работу берем из таблицы rabota, без фильтрации по статусу ---
        query_taken_rabota = """
            SELECT results, Sity
            FROM rabota
            WHERE user_id = %s
            ORDER BY id DESC
        """
        cursor.execute(query_taken_rabota, (str(user_id),))
        rows = cursor.fetchall()

        for row in rows:
            taken_work.append({
                "Sity": row.get("Sity", "Не указан"),
                "results": row.get("results", "#")
            })

        print(f"✅ Взятых записей из rabota найдено: {len(taken_work)}")

    except mysql.connector.Error as e:
        print(f"❌ Ошибка работы с БД: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    # Пагинация для основного списка результатов (если нужна)
    data_list = [SimpleNamespace(**item) for item in results]
    paginator = Paginator(data_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'main_app/blank_page_2.html', {
        'titles': titles,
        'saved': saved,
        'page_obj': page_obj,
        'status': status,
        'logs': f"Записей в result: {len(results)} | Взятых в работе (rabota): {len(taken_work)} | user_id: {user_id}",
        'taken_work': taken_work,
    })


@login_required
def blank_page_1(request):
    user_id = str(request.user.id)
    history = []

    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT keyword, search_date
            FROM search_history
            WHERE user_id = %s
            ORDER BY search_date DESC
            LIMIT 20
        """
        cursor.execute(query, (user_id,))
        history = cursor.fetchall()

    except mysql.connector.Error as err:
        print(f"❌ Ошибка при получении истории: {err}")
        history = []
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return render(request, 'main_app/blank_page_1.html', {
        'history': history
    })



@login_required
def blank_page_3(request):
    return render(request, 'main_app/blank_page_3.html')


@login_required
def blank_page_4(request):
    return render(request, 'main_app/blank_page_4.html')


@login_required
def blank_page_5(request):
    html_pages = request.session.get('html_pages', [])
    saved = request.session.get('saved', False)
    return render(request, 'main_app/test.html', {'html_pages': html_pages, 'saved': saved})


def blank_page_6(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            return render(request, 'main_app/registration.html', {'error': 'Введите email и пароль'})

        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect('search')
        else:
            try:
                user = User.objects.create_user(username=email, email=email, password=password)
                login(request, user)
                return redirect('search')
            except Exception as e:
                return render(request, 'main_app/registration.html', {'error': f'Ошибка: {str(e)}'})

    return render(request, 'main_app/registration.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('/registration/')

@login_required
@csrf_exempt
def take_to_work(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Неверный метод запроса'})

    user_id = str(request.user.id)
    item_id = request.POST.get('item_id')

    if not item_id:
        return JsonResponse({'status': 'error', 'message': 'Не передан item_id'})

    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT id, result FROM user WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
        row = cursor.fetchone()
        if not row:
            return JsonResponse({'status': 'error', 'message': 'Данные пользователя не найдены'})

        raw_result = row.get('result') or '[]'

        try:
            result_data = json.loads(raw_result)
            if isinstance(result_data, dict):
                result_data = [result_data]
        except Exception:
            result_data = []

        target_block = next((b for b in result_data if b.get('id') == item_id), None)
        if not target_block:
            return JsonResponse({'status': 'error', 'message': 'Блок с таким item_id не найден в result'})

        site_url = target_block.get('Link_baza_json', '')
        sity = target_block.get('Sity', '')

        insert_query = "INSERT INTO rabota (user_id, results, Sity) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (user_id, site_url, sity))
        connection.commit()

        return JsonResponse({'status': 'ok', 'message': 'Данные успешно сохранены в rabota'})

    except mysql.connector.Error as e:
        return JsonResponse({'status': 'error', 'message': f'Ошибка базы данных: {str(e)}'})
    except Exception as ex:
        return JsonResponse({'status': 'error', 'message': f'Ошибка обработки: {str(ex)}'})
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def dashboard(request):
    user_id = str(request.user.id)

    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT Sity, results FROM rabota WHERE user_id = %s ORDER BY id DESC", (user_id,))
        taken_work = cursor.fetchall()

    except Exception:
        taken_work = []
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return render(request, 'your_template.html', {'taken_work': taken_work})


@csrf_exempt
def delete_item(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Неверный метод'})

    item_id = request.POST.get('item_id')
    if not item_id:
        return JsonResponse({'status': 'error', 'message': 'item_id не передан'})

    user_id = str(request.user.id)

    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)

        # Получаем поле result для текущего пользователя (берем последнюю запись)
        cursor.execute("SELECT id, result FROM user WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
        row = cursor.fetchone()

        if not row or not row.get('result'):
            return JsonResponse({'status': 'error', 'message': 'Данные result не найдены'})

        data = json.loads(row['result'])
        if not isinstance(data, list):
            return JsonResponse({'status': 'error', 'message': 'JSON в поле result не список'})

        new_data = [obj for obj in data if obj.get('id') != item_id]

        if len(new_data) == len(data):
            return JsonResponse({'status': 'error', 'message': 'Объект с таким id не найден'})

        # Обновляем поле result в таблице user
        cursor.execute("UPDATE user SET result = %s WHERE id = %s", (json.dumps(new_data, ensure_ascii=False), row['id']))
        connection.commit()

        return JsonResponse({'status': 'ok'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()




@require_POST
@login_required
def take_in_work(request):
    if request.method == 'POST':
        user = request.user
        site_link = request.POST.get('site_link', '')
        city = request.POST.get('city', '')

        # Можно добавить проверки на валидность данных

        rabota = Rabota.objects.create(
            user=user,
            results=site_link,
            city=city,
        )
        return JsonResponse({'status': 'ok', 'id': rabota.id})
    return JsonResponse({'status': 'error'}, status=400)

def take_item(request):
    if request.method == 'POST':
        user = request.user
        sity = request.POST.get('Sity')
        results = request.POST.get('results')

        if not sity or not results:
            return JsonResponse({'status': 'error', 'message': 'Missing data'}, status=400)

        rabota = Rabota.objects.create(user=user, Sity=sity, results=results)
        return JsonResponse({'status': 'success', 'message': 'Item taken in work', 'id': rabota.id})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

        try:
            user = UserLogin.objects.get(username=email)
            if user.password == hashed_password:
                # Успешный вход
                request.session['user_id'] = user.id
                return redirect('home')
            else:
                error = "Неверный пароль"
        except UserLogin.DoesNotExist:
            # Пользователь не найден — создаём
            user = UserLogin.objects.create(username=email, password=hashed_password)
            request.session['user_id'] = user.id
            return redirect('home')

        return render(request, 'login.html', {'error': error})

    return render(request, 'login.html')

