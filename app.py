from flask import Flask, request, redirect, url_for, render_template_string # type: ignore
from flask_cors import CORS

from movieDetails.dm import dm as dm_dp
app = Flask(__name__)
CORS(app)
app.register_blueprint(dm_dp, url_prefix='/dm')
# 首页，提供一个简单的表单
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        return redirect(url_for('welcome', name=name))
    return '''
        <form method="post">
            Name: <input type="text" name="name">
            <input type="submit" value="Submit">
        </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)