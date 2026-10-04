import os


def get_database_uri():
    database_url = os.environ.get('DATABASE_URL')
    if os.environ.get('VERCEL') == '1' and not database_url:
        raise RuntimeError('Set DATABASE_URL to a persistent PostgreSQL database in Vercel.')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    return database_url or 'sqlite:///lms.db'


def get_secret_key():
    secret_key = os.environ.get('SECRET_KEY')
    if os.environ.get('VERCEL') == '1' and not secret_key:
        raise RuntimeError('Set SECRET_KEY in the Vercel environment variables.')
    return secret_key or 'local-development-key-change-before-deploying'


class Config:
    SECRET_KEY = get_secret_key()
    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False  # Disabled for simplicity in academic project
