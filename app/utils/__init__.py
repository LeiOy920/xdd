# from flask import Blueprint, request, jsonify
# from minio_utils import get_minio_storage
# from wordcloud import WordCloud
# import pandas as pd
# import io
#
# bp = Blueprint('movies', __name__)
#
#
# # @bp.route('/movies/<movie_id>/wordcloud', methods=['POST'])
# # def upload_wordcloud(movie_id):
# #     """上传电影词云图片"""
# #     # 假设从请求中获取词云数据
# #     text_data = request.json.get('text', '')
# #
# #     # 生成词云
# #     wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_data)
# #
# #     # 保存到BytesIO
# #     img_bytes = io.BytesIO()
# #     wordcloud.to_image().save(img_bytes, format='PNG')
# #     img_bytes.seek(0)
# #
# #     # 上传到MinIO
# #     storage = get_minio_storage()
# #     object_path = storage.upload_wordcloud(img_bytes, movie_id)
# #
# #     if object_path:
# #         # 生成临时访问URL
# #         url = storage.get_file_url(object_path)
# #         return jsonify({'success': True, 'path': object_path, 'url': url})
# #     else:
# #         return jsonify({'success': False, 'error': '上传失败'}), 500
# #
# #
# # @bp.route('/movies/<movie_id>/reviews', methods=['POST'])
# # def upload_reviews(movie_id):
# #     """上传电影评论数据"""
# #     # 假设从请求中获取CSV文件
# #     if 'file' not in request.files:
# #         return jsonify({'success': False, 'error': '未找到文件'}), 400
# #
# #     file = request.files['file']
# #
# #     # 上传到MinIO
# #     storage = get_minio_storage()
# #     object_path = storage.upload_reviews(file, movie_id)
# #
# #     if object_path:
# #         return jsonify({'success': True, 'path': object_path})
# #     else:
# #         return jsonify({'success': False, 'error': '上传失败'}), 500
#
#
# @bp.route('/movies/<movie_id>/wordcloud', methods=['GET'])
# def get_wordcloud(movie_id):
#     """获取电影词云图片"""
#     version = request.args.get('version')
#
#     storage = get_minio_storage()
#
#     # 直接通过Flask返回文件
#     response = storage.serve_file(
#         f"wordclouds/{movie_id}/{version}.png" if version else None,
#         file_type='wordcloud',
#         as_attachment=False
#     )
#
#     if response:
#         return response
#     else:
#         return jsonify({'success': False, 'error': '词云不存在'}), 404
#
#
# @bp.route('/movies/<movie_id>/reviews/analysis', methods=['POST'])
# def analyze_reviews(movie_id):
#     """分析电影评论并存储结果"""
#     # 获取评论数据
#     storage = get_minio_storage()
#     reviews_df = storage.get_reviews(movie_id, as_dataframe=True)
#
#     if reviews_df is None:
#         return jsonify({'success': False, 'error': '未找到评论数据'}), 404
#
#     # 假设进行一些分析
#     analysis_result = {
#         'total_reviews': len(reviews_df),
#         'average_rating': reviews_df['rating'].mean() if 'rating' in reviews_df.columns else None,
#         'sentiment_counts': reviews_df[
#             'sentiment'].value_counts().to_dict() if 'sentiment' in reviews_df.columns else None
#     }
#
#     # 存储分析结果
#     object_path = storage.upload_analytics_result(
#         analysis_result,
#         result_type='review_summary',
#         movie_id=movie_id
#     )
#
#     if object_path:
#         return jsonify({'success': True, 'path': object_path, 'result': analysis_result})
#     else:
#         return jsonify({'success': False, 'error': '存储分析结果失败'}), 500