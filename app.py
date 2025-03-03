from flask import Flask, request, redirect, url_for, render_template_string # type: ignore
from flask_cors import CORS
from app.config import app
from app.routes.datatest import datatest


app.register_blueprint(datatest, url_prefix='/dt')


# 创建应用实例
if __name__ == '__main__':
    app.run(debug=True)