import os

# Путь до корня проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Секретный ключ для Django — замени на свой уникальный
SECRET_KEY = 'your-secret-key-here'

# Включаем режим отладки (в боевом режиме ставь False)
DEBUG = True

ALLOWED_HOSTS = []

# Установленные приложения
INSTALLED_APPS = [
    'django.contrib.admin',                   # ✅ админка
    'django.contrib.auth',                    # ✅ система аутентификации
    'django.contrib.contenttypes',            # ✅ поддержка моделей
    'django.contrib.sessions',                # ✅ сессии
    'django.contrib.messages',                # ✅ сообщения
    'django.contrib.staticfiles',             # ✅ статика

    'main_app',                               # 👈 твое приложение
    'widget_tweaks',                          # 👈 твой пакет для кастомизации форм
]

# Промежуточное ПО (middleware)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',      # ✅ сессии
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',   # ✅ авторизация
    'django.contrib.messages.middleware.MessageMiddleware',      # ✅ сообщения
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Корень URL-ов
ROOT_URLCONF = 'simple_django_project.urls'

# Настройки шаблонов
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # Если у тебя общая папка templates, можешь указать путь здесь
        'APP_DIRS': True,  # Ищет шаблоны внутри папок каждого приложения
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',         # ✅ авторизация
                'django.contrib.messages.context_processors.messages', # ✅ сообщения
                'django.template.context_processors.static',           # ✅ доступ к STATIC_URL
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'alliance-pr0fi_123',  # имя базы
        'USER': '047281260_123',    # имя пользователя
        'PASSWORD': 'Zxcvbnm2025',      # пароль
        'HOST': 'mysql.alliance-pr0fi.myjino.ru',      # хост сервера базы (уточни у хостера)
        'PORT': '3306',                 # порт, обычно 3306
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
# Точка входа WSGI
WSGI_APPLICATION = 'simple_django_project.wsgi.application'


# Локализация
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Статические файлы (CSS, JS, картинки)
STATIC_URL = '/static/'

# Где искать статику (в папке main_app/static/)
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'main_app', 'static'),
]
LOGIN_URL = '/blank6/'
LOGIN_REDIRECT_URL = '/'

