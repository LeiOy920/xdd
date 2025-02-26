from flask import Flask, request, redirect, url_for, render_template_string # type: ignore

app = Flask(__name__)

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

# 欢迎页面，接收来自首页的名字参数并显示欢迎信息
@app.route('/welcome/<name>')
def welcome(name):
    return f'<h1>Welcome, {name}!</h1>'

if __name__ == '__main__':
    app.run(debug=True)