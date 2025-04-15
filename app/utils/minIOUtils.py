import logging
import os
import io
from typing import  Optional

from flask import current_app
from minio import Minio
from minio.error import S3Error



class MinIOStorage:
    """
    MinIO存储工具类，用于电影大数据分析项目中的文件存储操作
    支持词云图片、用户评论文本、JSON数据等多种文件格式
    """

    def __init__(self, app=None):
        """
        初始化MinIO客户端
        可以直接传入Flask应用或稍后使用init_app方法初始化

        :param app: Flask应用实例
        """
        self.client = None
        self.config = {}

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        从Flask应用配置中初始化MinIO客户端

        :param app: Flask应用实例
        """
        from app.config import MINIO_ENDPOINT


        # 从应用配置中获取MinIO配置
        self.config = {
            'MINIO_ENDPOINT': app.config.get('MINIO_ENDPOINT', MINIO_ENDPOINT),
            'MINIO_ACCESS_KEY': app.config.get('MINIO_ACCESS_KEY', 'minioadmin'),
            'MINIO_SECRET_KEY': app.config.get('MINIO_SECRET_KEY', 'minioadmin'),
            'MINIO_SECURE': app.config.get('MINIO_SECURE', False),
            'MINIO_REGION': app.config.get('MINIO_REGION', None),
            'MINIO_DEFAULT_BUCKET': app.config.get('MINIO_DEFAULT_BUCKET', 'movies-data'),
            'MINIO_BUCKETS': app.config.get('MINIO_BUCKETS', {
                'wordclouds': 'movie-wordclouds',
                'reviews': 'movie-reviews',
                'posters': 'movie-posters',
                'analytics': 'movie-analytics'
            })
        }

        # 实例化MinIO客户端
        self.client = Minio(
            endpoint=self.config['MINIO_ENDPOINT'],
            access_key=self.config['MINIO_ACCESS_KEY'],
            secret_key=self.config['MINIO_SECRET_KEY'],
            secure=self.config['MINIO_SECURE'],
            region=self.config['MINIO_REGION']
        )

        # 确保所需的bucket存在
        self._ensure_buckets_exist()

        # 将实例附加到应用
        app.extensions = getattr(app, 'extensions', {})
        app.extensions['minio_storage'] = self

    def _ensure_buckets_exist(self):
        """确保所有配置的存储桶都已存在，如果不存在则创建"""
        for bucket_purpose, bucket_name in self.config['MINIO_BUCKETS'].items():
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                current_app.logger.info(f"Created bucket: {bucket_name} for {bucket_purpose}")

    def _get_bucket_for_filetype(self, file_type: str) -> str:
        """
        根据文件类型确定应该使用哪个存储桶

        :param file_type: 文件类型标识符(如'wordcloud', 'review', 'poster', 'analytics')
        :return: 对应的存储桶名称
        """
        mapping = {
            'wordcloud': self.config['MINIO_BUCKETS'].get('wordclouds'),
            'review': self.config['MINIO_BUCKETS'].get('reviews'),
            'poster': self.config['MINIO_BUCKETS'].get('posters'),
            'analytics': self.config['MINIO_BUCKETS'].get('analytics')
        }

        return mapping.get(file_type, self.config['MINIO_DEFAULT_BUCKET'])

    def get_file(self,
                 object_name: str,
                 bucket_name: str = None,
                 file_type: str = None) -> Optional[io.BytesIO]:
        """
        获取文件内容

        :param object_name: 对象名称/路径
        :param bucket_name: 存储桶名称
        :param file_type: 文件类型（用于确定存储桶）
        :return: 包含文件内容的BytesIO对象，或None（如果文件不存在）
        """
        try:
            # 确定存储桶
            if bucket_name is None and file_type is not None:
                bucket_name = self._get_bucket_for_filetype(file_type)
            elif bucket_name is None:
                # 尝试从对象路径推断存储桶
                parts = object_name.split('/')
                if parts[0] in ['wordclouds', 'reviews', 'posters', 'analytics']:
                    file_type = parts[0][:-1] if parts[0].endswith('s') else parts[0]
                    bucket_name = self._get_bucket_for_filetype(file_type)
                else:
                    bucket_name = self.config['MINIO_DEFAULT_BUCKET']

            logging.info(f"Attempting to get file {object_name} from bucket {bucket_name}")
            # 获取对象
            response = self.client.get_object(
                bucket_name=bucket_name,
                object_name=object_name
            )

            # 读取内容到BytesIO
            data = io.BytesIO(response.read())
            response.close()
            response.release_conn()

            # 重置指针位置
            data.seek(0)
            return data

        except S3Error as e:
            current_app.logger.error(f"MinIO error getting file {object_name}: {e}")
            return None

        except Exception as e:
            current_app.logger.error(f"Error getting file {object_name}: {e}")
            return None






# 为了更方便地在Flask路由中使用，创建一些辅助函数

def init_minio_storage(app=None):
    """
    初始化MinIO存储
    可以作为Flask工厂函数的一部分调用

    :param app: Flask应用实例
    :return: MinIOStorage实例
    """
    storage = MinIOStorage()
    if app is not None:
        with app.app_context():
            storage.init_app(app)
    return storage


def get_minio_storage():
    """
    获取当前应用的MinIO存储实例

    :return: MinIOStorage实例
    """
    if not hasattr(current_app, 'extensions') or 'minio_storage' not in current_app.extensions:
        raise RuntimeError("MinIO存储未初始化。请先调用init_minio_storage(app)")

    return current_app.extensions['minio_storage']
