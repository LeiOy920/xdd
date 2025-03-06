import os
import io
from typing import Union, List, Dict, Tuple, Optional, BinaryIO
import tempfile
import json
from datetime import datetime, timedelta

from minio.deleteobjects import DeleteObject
from werkzeug.datastructures import FileStorage
from flask import current_app, send_file
from minio import Minio
from minio.error import S3Error
from PIL import Image
import pandas as pd


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
        # 从应用配置中获取MinIO配置
        self.config = {
            'MINIO_ENDPOINT': app.config.get('MINIO_ENDPOINT', 'localhost:9000'),
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

    def upload_file(self,
                    file_data: Union[FileStorage, BinaryIO, bytes, str],
                    object_name: str,
                    file_type: str = None,
                    bucket_name: str = None,
                    content_type: str = None,
                    metadata: Dict = None) -> bool:
        """
        上传文件到MinIO

        :param file_data: 要上传的文件数据，可以是Flask的FileStorage、文件对象、字节数据或文件路径
        :param object_name: 在MinIO中存储的对象名称/路径
        :param file_type: 文件类型，用于确定存储桶
        :param bucket_name: 显式指定存储桶，优先级高于file_type
        :param content_type: 文件的MIME类型
        :param metadata: 文件元数据
        :return: 上传是否成功
        """
        try:
            # 确定文件大小和数据
            file_size = 0
            file_obj = None

            # 处理不同类型的输入
            if isinstance(file_data, FileStorage):  # Flask上传的文件
                file_size = os.fstat(file_data.fileno()).st_size
                file_obj = file_data.stream
                # 如果未指定content_type，使用Flask检测的类型
                if content_type is None:
                    content_type = file_data.content_type

            elif isinstance(file_data, (io.IOBase, BinaryIO)):  # 文件对象
                file_data.seek(0, os.SEEK_END)
                file_size = file_data.tell()
                file_data.seek(0)
                file_obj = file_data

            elif isinstance(file_data, bytes):  # 字节数据
                file_size = len(file_data)
                file_obj = io.BytesIO(file_data)

            elif isinstance(file_data, str) and os.path.isfile(file_data):  # 文件路径
                file_size = os.path.getsize(file_data)
                file_obj = open(file_data, 'rb')

            else:
                raise ValueError("不支持的文件数据类型")

            # 确定存储桶
            if bucket_name is None and file_type is not None:
                bucket_name = self._get_bucket_for_filetype(file_type)
            elif bucket_name is None:
                bucket_name = self.config['MINIO_DEFAULT_BUCKET']

            # 确保存储桶存在
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)

            # 添加基本元数据
            if metadata is None:
                metadata = {}

            metadata.update({
                'uploaded-at': datetime.now().isoformat(),
                'file-type': file_type or 'unknown'
            })

            # 上传文件
            self.client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=file_obj,
                length=file_size,
                content_type=content_type,
                metadata=metadata
            )

            # 如果文件对象是由文件路径打开的，需要关闭它
            if isinstance(file_data, str) and os.path.isfile(file_data):
                file_obj.close()

            return True

        except S3Error as e:
            current_app.logger.error(f"MinIO error: {e}")
            # 如果文件对象是由文件路径打开的，确保关闭它
            if isinstance(file_data, str) and os.path.isfile(file_data) and file_obj:
                file_obj.close()
            return False

        except Exception as e:
            current_app.logger.error(f"Error uploading file to MinIO: {e}")
            # 如果文件对象是由文件路径打开的，确保关闭它
            if isinstance(file_data, str) and os.path.isfile(file_data) and file_obj:
                file_obj.close()
            return False

    def upload_wordcloud(self,
                         image_data: Union[Image.Image, bytes, str],
                         movie_id: str,
                         version: str = None) -> str:
        """
        上传电影词云图片

        :param image_data: PIL图像对象、字节数据或文件路径
        :param movie_id: 电影ID
        :param version: 词云版本号，默认使用当前时间戳
        :return: 存储的对象路径或None（如果上传失败）
        """
        try:
            # 准备图像数据
            if isinstance(image_data, Image.Image):
                # 将PIL图像转换为字节流
                img_byte_arr = io.BytesIO()
                image_data.save(img_byte_arr, format='PNG')
                img_byte_arr.seek(0)
                image_bytes = img_byte_arr
                content_type = 'image/png'
            elif isinstance(image_data, bytes):
                image_bytes = io.BytesIO(image_data)
                content_type = 'image/png'  # 假设是PNG格式
            elif isinstance(image_data, str) and os.path.isfile(image_data):
                # 直接使用文件路径
                image_bytes = image_data
                # 从文件扩展名推断内容类型
                ext = os.path.splitext(image_data)[1].lower()
                content_type = {
                    '.png': 'image/png',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.gif': 'image/gif',
                    '.svg': 'image/svg+xml'
                }.get(ext, 'application/octet-stream')
            else:
                raise ValueError("不支持的图像数据类型")

            # 生成版本号和对象名称
            version = version or datetime.now().strftime('%Y%m%d%H%M%S')
            object_name = f"wordclouds/{movie_id}/{version}.png"

            # 设置元数据
            metadata = {
                'movie-id': movie_id,
                'version': version,
                'type': 'wordcloud'
            }

            # 上传到MinIO
            bucket_name = self._get_bucket_for_filetype('wordcloud')
            if self.upload_file(
                    file_data=image_bytes,
                    object_name=object_name,
                    bucket_name=bucket_name,
                    content_type=content_type,
                    metadata=metadata
            ):
                return object_name
            return None

        except Exception as e:
            current_app.logger.error(f"Error uploading wordcloud: {e}")
            return None

    def upload_reviews(self,
                       reviews_data: Union[List[Dict], pd.DataFrame, str],
                       movie_id: str,
                       format: str = 'json') -> str:
        """
        上传电影评论数据

        :param reviews_data: 评论数据，可以是字典列表、Pandas DataFrame或CSV/JSON文件路径
        :param movie_id: 电影ID
        :param format: 存储格式，'json'或'csv'
        :return: 存储的对象路径或None（如果上传失败）
        """
        try:
            # 准备评论数据
            if isinstance(reviews_data, list):
                # 列表转DataFrame
                df = pd.DataFrame(reviews_data)
            elif isinstance(reviews_data, pd.DataFrame):
                df = reviews_data
            elif isinstance(reviews_data, str) and os.path.isfile(reviews_data):
                # 从文件加载数据
                ext = os.path.splitext(reviews_data)[1].lower()
                if ext == '.csv':
                    df = pd.read_csv(reviews_data)
                elif ext == '.json':
                    df = pd.read_json(reviews_data)
                else:
                    raise ValueError(f"不支持的文件格式: {ext}")
            else:
                raise ValueError("不支持的评论数据类型")

            # 转换为指定格式
            data_buffer = io.BytesIO()
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

            if format.lower() == 'json':
                df.to_json(data_buffer, orient='records', lines=True)
                content_type = 'application/json'
                object_name = f"reviews/{movie_id}/{timestamp}.json"
            else:  # csv
                df.to_csv(data_buffer, index=False)
                content_type = 'text/csv'
                object_name = f"reviews/{movie_id}/{timestamp}.csv"

            # 重置缓冲区指针
            data_buffer.seek(0)

            # 设置元数据
            metadata = {
                'movie-id': movie_id,
                'timestamp': timestamp,
                'row-count': str(len(df)),
                'format': format.lower(),
                'type': 'reviews'
            }

            # 上传到MinIO
            bucket_name = self._get_bucket_for_filetype('review')
            if self.upload_file(
                    file_data=data_buffer,
                    object_name=object_name,
                    bucket_name=bucket_name,
                    content_type=content_type,
                    metadata=metadata
            ):
                return object_name
            return None

        except Exception as e:
            current_app.logger.error(f"Error uploading reviews: {e}")
            return None

    def upload_analytics_result(self,
                                data: Union[Dict, List, pd.DataFrame, str],
                                result_type: str,
                                movie_id: str = None,
                                format: str = 'json') -> str:
        """
        上传分析结果数据

        :param data: 分析结果数据
        :param result_type: 结果类型标识符
        :param movie_id: 相关电影ID（如果适用）
        :param format: 存储格式，'json'或'csv'
        :return: 存储的对象路径或None（如果上传失败）
        """
        try:
            # 准备数据
            if isinstance(data, (dict, list)):
                # 字典或列表转DataFrame
                if isinstance(data, dict):
                    # 如果是嵌套字典，转换为JSON字符串
                    data_buffer = io.BytesIO(json.dumps(data).encode())
                    df = None
                else:
                    df = pd.DataFrame(data)
            elif isinstance(data, pd.DataFrame):
                df = data
            elif isinstance(data, str) and os.path.isfile(data):
                # 从文件加载数据
                ext = os.path.splitext(data)[1].lower()
                if ext == '.csv':
                    df = pd.read_csv(data)
                elif ext == '.json':
                    # 尝试作为DataFrame加载
                    try:
                        df = pd.read_json(data)
                    except:
                        # 如果失败，作为原始JSON处理
                        with open(data, 'r') as f:
                            data_buffer = io.BytesIO(f.read().encode())
                        df = None
                else:
                    raise ValueError(f"不支持的文件格式: {ext}")
            else:
                raise ValueError("不支持的数据类型")

            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            if movie_id:
                base_path = f"analytics/{result_type}/{movie_id}"
            else:
                base_path = f"analytics/{result_type}"

            # 转换为指定格式
            if df is not None:
                data_buffer = io.BytesIO()
                if format.lower() == 'json':
                    df.to_json(data_buffer, orient='records')
                    content_type = 'application/json'
                    object_name = f"{base_path}/{timestamp}.json"
                else:  # csv
                    df.to_csv(data_buffer, index=False)
                    content_type = 'text/csv'
                    object_name = f"{base_path}/{timestamp}.csv"
                # 重置缓冲区指针
                data_buffer.seek(0)
            else:
                # 假设已经是JSON字符串
                content_type = 'application/json'
                object_name = f"{base_path}/{timestamp}.json"

            # 设置元数据
            metadata = {
                'result-type': result_type,
                'timestamp': timestamp,
                'format': format.lower(),
                'type': 'analytics'
            }
            if movie_id:
                metadata['movie-id'] = movie_id

            # 上传到MinIO
            bucket_name = self._get_bucket_for_filetype('analytics')
            if self.upload_file(
                    file_data=data_buffer,
                    object_name=object_name,
                    bucket_name=bucket_name,
                    content_type=content_type,
                    metadata=metadata
            ):
                return object_name
            return None

        except Exception as e:
            current_app.logger.error(f"Error uploading analytics result: {e}")
            return None

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

    def get_wordcloud(self,
                      movie_id: str,
                      version: str = None) -> Optional[io.BytesIO]:
        """
        获取电影词云图片

        :param movie_id: 电影ID
        :param version: 版本号，如果不指定则获取最新版本
        :return: 包含图片内容的BytesIO对象，或None（如果文件不存在）
        """
        try:
            bucket_name = self._get_bucket_for_filetype('wordcloud')

            if version:
                # 获取指定版本
                object_name = f"wordclouds/{movie_id}/{version}.png"
                return self.get_file(object_name, bucket_name)
            else:
                # 获取最新版本
                prefix = f"wordclouds/{movie_id}/"
                objects = list(self.client.list_objects(bucket_name, prefix=prefix, recursive=True))

                if not objects:
                    return None

                # 按最后修改时间排序，获取最新的
                latest = max(objects, key=lambda obj: obj.last_modified)
                return self.get_file(latest.object_name, bucket_name)

        except Exception as e:
            current_app.logger.error(f"Error getting wordcloud for movie {movie_id}: {e}")
            return None

    def get_reviews(self,
                    movie_id: str,
                    timestamp: str = None,
                    as_dataframe: bool = True) -> Union[pd.DataFrame, List[Dict], None]:
        """
        获取电影评论数据

        :param movie_id: 电影ID
        :param timestamp: 时间戳，如果不指定则获取最新版本
        :param as_dataframe: 是否返回为Pandas DataFrame（否则返回字典列表）
        :return: 评论数据，或None（如果文件不存在）
        """
        try:
            bucket_name = self._get_bucket_for_filetype('review')

            if timestamp:
                # 尝试获取指定时间戳的JSON或CSV文件
                for ext in ['.json', '.csv']:
                    object_name = f"reviews/{movie_id}/{timestamp}{ext}"
                    data = self.get_file(object_name, bucket_name)
                    if data:
                        break
            else:
                # 获取最新版本
                prefix = f"reviews/{movie_id}/"
                objects = list(self.client.list_objects(bucket_name, prefix=prefix, recursive=True))

                if not objects:
                    return None

                # 按最后修改时间排序，获取最新的
                latest = max(objects, key=lambda obj: obj.last_modified)
                data = self.get_file(latest.object_name, bucket_name)
                object_name = latest.object_name

            if not data:
                return None

            # 根据文件类型解析数据
            if object_name.endswith('.json'):
                df = pd.read_json(data, orient='records', lines=True)
            else:  # CSV
                df = pd.read_csv(data)

            if as_dataframe:
                return df
            else:
                return df.to_dict(orient='records')

        except Exception as e:
            current_app.logger.error(f"Error getting reviews for movie {movie_id}: {e}")
            return None

    def get_analytics_result(self,
                             result_type: str,
                             movie_id: str = None,
                             timestamp: str = None,
                             as_dataframe: bool = True) -> Union[pd.DataFrame, Dict, List, None]:
        """
        获取分析结果数据

        :param result_type: 结果类型标识符
        :param movie_id: 相关电影ID（如果适用）
        :param timestamp: 时间戳，如果不指定则获取最新版本
        :param as_dataframe: 是否尝试返回为Pandas DataFrame
        :return: 分析结果数据，或None（如果文件不存在）
        """
        try:
            bucket_name = self._get_bucket_for_filetype('analytics')

            # 构建基本路径
            if movie_id:
                base_path = f"analytics/{result_type}/{movie_id}"
            else:
                base_path = f"analytics/{result_type}"

            if timestamp:
                # 尝试获取指定时间戳的JSON或CSV文件
                for ext in ['.json', '.csv']:
                    object_name = f"{base_path}/{timestamp}{ext}"
                    data = self.get_file(object_name, bucket_name)
                    if data:
                        break
            else:
                # 获取最新版本
                prefix = f"{base_path}/"
                objects = list(self.client.list_objects(bucket_name, prefix=prefix, recursive=True))

                if not objects:
                    return None

                # 按最后修改时间排序，获取最新的
                latest = max(objects, key=lambda obj: obj.last_modified)
                data = self.get_file(latest.object_name, bucket_name)
                object_name = latest.object_name

            if not data:
                return None

            # 根据文件类型解析数据
            if object_name.endswith('.json'):
                try:
                    if as_dataframe:
                        return pd.read_json(data)
                    else:
                        data.seek(0)
                        return json.loads(data.read().decode())
                except:
                    # 如果解析为DataFrame失败，尝试作为JSON对象/列表解析
                    data.seek(0)
                    return json.loads(data.read().decode())
            else:  # CSV
                df = pd.read_csv(data)
                if as_dataframe:
                    return df
                else:
                    return df.to_dict(orient='records')

        except Exception as e:
            current_app.logger.error(f"Error getting analytics result {result_type}: {e}")
            return None

    def list_files(self,
                   prefix: str = None,
                   bucket_name: str = None,
                   file_type: str = None,
                   recursive: bool = True) -> List[Dict]:
        """
        列出匹配前缀的文件

        :param prefix: 对象名前缀
        :param bucket_name: 存储桶名称
        :param file_type: 文件类型（用于确定存储桶）
        :param recursive: 是否递归查找子目录
        :return: 文件信息列表
        """
        try:
            # 确定存储桶
            if bucket_name is None and file_type is not None:
                bucket_name = self._get_bucket_for_filetype(file_type)
            elif bucket_name is None:
                bucket_name = self.config['MINIO_DEFAULT_BUCKET']

            # 获取对象列表
            objects = self.client.list_objects(
                bucket_name=bucket_name,
                prefix=prefix,
                recursive=recursive
            )

            # 转换为字典列表
            result = []
            for obj in objects:
                result.append({
                    'name': obj.object_name,
                    'size': obj.size,
                    'last_modified': obj.last_modified,
                    'etag': obj.etag,
                    'content_type': self.client.stat_object(bucket_name, obj.object_name).content_type
                })

            return result

        except S3Error as e:
            current_app.logger.error(f"MinIO error listing files: {e}")
            return []

        except Exception as e:
            current_app.logger.error(f"Error listing files: {e}")
            return []

    def get_file_url(self,
                     object_name: str,
                     bucket_name: str = None,
                     file_type: str = None,
                     expires: int = 3600) -> Optional[str]:
        """
        获取文件的临时访问URL

        :param object_name: 对象名称/路径
        :param bucket_name: 存储桶名称
        :param file_type: 文件类型（用于确定存储桶）
        :param expires: 过期时间（秒）
        :return: 临时访问URL，或None（如果生成失败）
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

            # 生成临时URL
            url = self.client.presigned_get_object(
                bucket_name=bucket_name,
                object_name=object_name,
                expires=expires
            )

            return url

        except S3Error as e:
            current_app.logger.error(f"MinIO error generating URL for {object_name}: {e}")
            return None

        except Exception as e:
            current_app.logger.error(f"Error generating URL for {object_name}: {e}")
            return None

    def serve_file(self,
                   object_name: str,
                   bucket_name: str = None,
                   file_type: str = None,
                   download_name: str = None,
                   as_attachment: bool = False) -> Optional[object]:
        """
        从MinIO获取文件并通过Flask发送

        :param object_name: 对象名称/路径
        :param bucket_name: 存储桶名称
        :param file_type: 文件类型（用于确定存储桶）
        :param download_name: 下载文件名，默认使用对象名的最后一部分
        :param as_attachment: 是否作为附件下载
        :return: Flask的响应对象，或None（如果文件不存在）
        """
        try:
            # 获取文件内容
            data = self.get_file(object_name, bucket_name, file_type)
            if not data:
                return None

            # 确定文件名
            if download_name is None:
                download_name = object_name.split('/')[-1]

            # 确定MIME类型
            content_type = None
            try:
                # 尝试从MinIO获取内容类型
                if bucket_name is None and file_type is not None:
                    bucket_name = self._get_bucket_for_filetype(file_type)
                elif bucket_name is None:
                    parts = object_name.split('/')
                    if parts[0] in ['wordclouds', 'reviews', 'posters', 'analytics']:
                        file_type = parts[0][:-1] if parts[0].endswith('s') else parts[0]
                        bucket_name = self._get_bucket_for_filetype(file_type)
                    else:
                        bucket_name = self.config['MINIO_DEFAULT_BUCKET']

                stat = self.client.stat_object(bucket_name, object_name)
                content_type = stat.content_type
            except:
                # 如果获取失败，根据文件扩展名推断
                ext = os.path.splitext(download_name)[1].lower()
                content_type = {
                    '.png': 'image/png',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.gif': 'image/gif',
                    '.svg': 'image/svg+xml',
                    '.json': 'application/json',
                    '.csv': 'text/csv',
                    '.txt': 'text/plain',
                    '.pdf': 'application/pdf',
                    '.html': 'text/html'
                }.get(ext, 'application/octet-stream')

            # 发送文件
            return send_file(
                data,
                mimetype=content_type,
                as_attachment=as_attachment,
                download_name=download_name
            )

        except Exception as e:
            current_app.logger.error(f"Error serving file {object_name}: {e}")
            return None

    def delete_file(self,
                    object_name: str,
                    bucket_name: str = None,
                    file_type: str = None) -> bool:
        """
        删除文件

        :param object_name: 对象名称/路径
        :param bucket_name: 存储桶名称
        :param file_type: 文件类型（用于确定存储桶）
        :return: 是否删除成功
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

            # 删除文件
            self.client.remove_object(
                bucket_name=bucket_name,
                object_name=object_name
            )

            return True

        except S3Error as e:
            current_app.logger.error(f"MinIO error deleting file {object_name}: {e}")
            return False

        except Exception as e:
            current_app.logger.error(f"Error deleting file {object_name}: {e}")
            return False

    def bulk_delete(self,
                    object_names: List[str],
                    bucket_name: str = None,
                    file_type: str = None) -> Tuple[int, int]:
        """
        批量删除文件

        :param object_names: 对象名称/路径列表
        :param bucket_name: 存储桶名称
        :param file_type: 文件类型（用于确定存储桶）
        :return: 成功删除数量和失败数量的元组
        """
        try:
            # 确定存储桶
            if bucket_name is None and file_type is not None:
                bucket_name = self._get_bucket_for_filetype(file_type)
            elif bucket_name is None:
                bucket_name = self.config['MINIO_DEFAULT_BUCKET']

            # 使用MinIO的delete_objects批量删除
            errors = self.client.remove_objects(
                bucket_name=bucket_name,
                delete_object_list=map(lambda x: DeleteObject(x), object_names)
            )

            # 计算错误数量
            error_count = sum(1 for _ in errors)
            success_count = len(object_names) - error_count

            return success_count, error_count

        except S3Error as e:
            current_app.logger.error(f"MinIO error in bulk delete: {e}")
            return 0, len(object_names)

        except Exception as e:
            current_app.logger.error(f"Error in bulk delete: {e}")
            return 0, len(object_names)


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