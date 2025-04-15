import logging
import os
from logging.handlers import RotatingFileHandler

from elasticsearch import Elasticsearch
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql

from app.utils.minIOUtils import init_minio_storage

pymysql.install_as_MySQLdb()

app = Flask(__name__)

app.debug = os.environ.get('FLASK_ENV') == 'development'

# 配置日志记录
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)

app.logger.setLevel(logging.INFO)
app.logger.info('App startup')

# 从环境变量获取配置
DATABASE_URL = os.environ.get('DATABASE_URL', 'mysql://root:123456@127.0.0.1/moviedb')
MINIO_ENDPOINT = os.environ.get('MINIO_ENDPOINT', '127.0.0.1:9000')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY', 'minioadmin')
ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL', 'http://127.0.0.1:9200/')

# 配置数据库
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# 设置MinIO配置
app.config['MINIO_ENDPOINT'] = MINIO_ENDPOINT
app.config['MINIO_ACCESS_KEY'] = MINIO_ACCESS_KEY
app.config['MINIO_SECRET_KEY'] = MINIO_SECRET_KEY
app.config['MINIO_SECURE'] = True  # 在生产环境中使用 HTTPS

# 自定义存储桶配置
app.config['MINIO_BUCKETS'] = {
    'wordclouds': 'movie-wordclouds',
    'reviews': 'movie-reviews',
    'posters': 'movie-posters',
    'analytics': 'movie-analytics'
}

# 初始化MinIO存储
minio_storage = init_minio_storage(app)

def connect_to_elasticsearch():
    es = Elasticsearch([ELASTICSEARCH_URL])
    return es