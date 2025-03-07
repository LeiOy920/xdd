from elasticsearch import Elasticsearch
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql

from app.utils.minIOUtils import init_minio_storage

pymysql.install_as_MySQLdb()

app = Flask(__name__)

app.debug = True


IP = '127.0.0.1'  # 统管IP


# url的格式为：数据库的协议：//用户名：密码@ip地址：端口号（默认可以不写）/数据库名
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql://root:123456@{IP}/moviedb"
# 动态追踪数据库的修改. 性能不好. 且未来版本中会移除. 目前只是为了解决控制台的提示才写的
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# 创建数据库的操作对象
db = SQLAlchemy(app)


# 设置MinIO配置
app.config['MINIO_ENDPOINT'] = f'{IP}:9000'
app.config['MINIO_ACCESS_KEY'] = 'minioadmin'
app.config['MINIO_SECRET_KEY'] = 'minioadmin'
app.config['MINIO_SECURE'] = False  # 如果使用HTTPS，设为True

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
    es = Elasticsearch([f'http://{IP}:9200/'])

    return es