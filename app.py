from flask import Flask, render_template, request, redirect, url_for, g, flash
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import json
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.jinja_env.globals.update({
    'ord': ord,
    'chr': chr
})

db = SQLAlchemy(app)
login_manager = LoginManager(app)



@app.context_processor
def inject_json():
    return dict(json=json)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text, nullable=False)  # 存储为JSON格式
    answer = db.Column(db.String(10), nullable=False)
    analysis = db.Column(db.Text)
    type = db.Column(db.String(10), nullable=False)  # 单选或多选

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    exam_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class ExamForm(FlaskForm):
    count = IntegerField('题目数量', default=10)
    submit = SubmitField('开始考试')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/import', methods=['GET', 'POST'])
@login_required
def import_questions():
    if request.method == 'POST':
        file = request.files['file']
        if not file or file.filename == '':
            flash('请选择一个Excel文件进行上传！', 'warning')
            return redirect(url_for('index'))
        
        try:
            # 尝试读取文件内容
            df = pd.read_excel(file)
            if df.empty:
                flash('Excel文件为空，请检查文件内容！', 'danger')
                return redirect(url_for('index'))
            
            # 如果读取成功，继续导入题目
            for _, row in df.iterrows():
                options = []
                for c in ['A', 'B', 'C', 'D']:
                    if pd.notna(row[c]):
                        options.append(row[c])
                answer = row['答案'].strip()
                question_type = '单选' if len(answer) == 1 else '多选'
                question = Question(
                    question=row['题目'],
                    options=json.dumps(options),
                    answer=answer,
                    analysis=row['解析'],
                    type=question_type
                )
                db.session.add(question)
            db.session.commit()
            flash('题目导入成功！', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()  # 回滚数据库以避免部分导入
            flash(f'导入失败，错误信息：{str(e)}', 'danger')
            return redirect(url_for('index'))
    return render_template('import.html')



@app.route('/exam', methods=['GET', 'POST'])
@login_required
def exam():
    form = ExamForm()
    if form.validate_on_submit():
        count = form.count.data
        questions = Question.query.order_by(db.func.random()).limit(count).all()
        if not questions:
            flash('当前没有可用题目，请先导入题目！', 'warning')
            return redirect(url_for('index'))
        return render_template('exam.html', questions=questions, form=form)
    return render_template('exam.html', form=form)



@app.route('/result', methods=['POST'])
@login_required
def result():
    if not request.form:
        return redirect(url_for('index'))
    
    answers = request.form
    questions = Question.query.all()
    total_questions = len(questions)
    if total_questions == 0:
        flash('当前没有可用题目！', 'warning')
        return redirect(url_for('index'))
    
    result_details = []
    correct_count = 0

    for question in questions:
        key = f'question_{question.id}'
        if key not in answers:
            continue
        user_answer = answers.getlist(key)  # 获取所有选项，适用于多选
        # print(user_answer)
        
        # 将用户答案转换为列表，处理空字符串
        user_answers = [a.strip() for a in user_answer if a.strip()]
        correct_answers = [a.strip() for a in question.answer]
        
        is_correct = False
        # 比较答案
        if question.type == '单选':
            if user_answers and user_answers[0] == correct_answers[0]:
                correct_count += 1
                is_correct = True
        else:
            print(user_answers)
            print(correct_answers)
            if set(user_answers) == set(correct_answers):
                correct_count += 1
                is_correct = True

        result_details.append({
            'question_id': question.id,
            'question': question.question,
            'user_answer': ','.join(user_answers),  # 以逗号分隔显示
            'correct_answer': ','.join(correct_answers),  # 以逗号分隔显示
            'is_correct': is_correct
        })

    # 计算准确率
    all_answers = len(result_details)
    accuracy = (correct_count / all_answers) * 100
    accuracy = round(accuracy, 2)  # 保留两位小数
    wrong_count = all_answers - correct_count

    # 保存记录
    record = Record(user_id=current_user.id, score=accuracy)
    db.session.add(record)
    db.session.commit()

    return render_template('result.html', 
                         accuracy=accuracy,
                         wrong_count=wrong_count,
                         correct_count=correct_count,
                         result_details=result_details,
                         all_answers=all_answers)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误！', 'danger')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not User.query.filter_by(username=username).first():
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@login_manager.unauthorized_handler
def unauthorized_callback():
    flash('请先登录！', 'warning')
    return redirect(url_for('login'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
