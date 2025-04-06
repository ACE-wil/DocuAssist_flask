from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from datetime import timedelta, datetime
from werkzeug.security import check_password_hash, generate_password_hash
from urllib.parse import urlparse
import random
from werkzeug.utils import secure_filename
from flask_cors import CORS
import sqlite3
from pathlib import Path
import json
from zhipuai import ZhipuAI
from pathlib import Path
from openai import OpenAI
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
from qiniu import Auth, put_data, etag  # 导入七牛SDK所需的模块
import time
from celery import Celery
from main.api.generate_scene import generate_scene
from concurrent.futures import ThreadPoolExecutor
from main.api.getWordsArr import get_words_arr
from main.api.qwcodeplus import get_qwen_response
from flask_jwt_extended import JWTManager, create_access_token


# 加载.env文件
load_dotenv()

# 从环境变量中获取敏感信息
ZHIPUAI_API_KEY = os.getenv('ZHIPUAI_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
QINIU_AK = os.getenv('QINIU_AK')
QINIU_SK = os.getenv('QINIU_SK')
QINIU_BUCKET_NAME = os.getenv('QINIU_BUCKET_NAME')
# 从环境变量中获取敏感信息


# 这是你的七牛空间名
bucket_name = 'docu-assist-base'  # 存储空间名称

# 构建鉴权对象
q = Auth(QINIU_AK, QINIU_SK)
# 填写您自己的APIKey
client = ZhipuAI(api_key=ZHIPUAI_API_KEY)
# 在创建Flask应用后立即启用CORS

db = SQLAlchemy()

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.absolute()

# 配置各种路径
INSTANCE_DIR = PROJECT_ROOT / 'instance'
UPLOAD_DIR = PROJECT_ROOT / 'uploads'
DB_PATH = INSTANCE_DIR / 'site.db'

# 创建必要的目录
INSTANCE_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 设置为16MB
# CORS_ORIGINS = os.getenv('CORS_ORIGINS')
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')

# 配置 CORS
CORS(app, resources={
    r"/api/*": {
        "origins": CORS_ORIGINS,  # React 开发服务器地址
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Accept", "X-Requested-With"],
        "supports_credentials": True,
        "expose_headers": ["Content-Disposition"],
        "max_age": 3600
    }
})

# 3. 初始化JWT
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # 设置密钥
jwt = JWTManager(app)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['UPLOAD_FOLDER'] = str(UPLOAD_DIR)  # Flask需要字符串路径
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 增加到 50MB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '7a9e6b5fc3d24a8f1e0b2c4d6a8f0e1c'  # 使用我们之前生成的密钥
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # 设置登录视图的端点

app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/api/upload', methods=['POST'])
def upload_file():
    load_dotenv()
    file = request.files['file']
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # 上传文件到 Kimi
    kimi_client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url="https://api.moonshot.cn/v1",
    )
    
    with open(filepath, 'rb') as f:
        file_object = kimi_client.files.create(
            file=f,
            purpose="file-extract"
        )
    
    # 获取文件内容
    file_content = kimi_client.files.content(file_id=file_object.id).text
    
    # 清理上传的文件
    os.remove(filepath)
    
    return jsonify({
        'status': 'success',
        'parsedContent': file_content
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    # 从请求中获取用户输入和对话历史
    user_input = request.json.get('message', '')
    chat_history = request.json.get('messages', [])

    # 将新的用户输入添加到消息历史
    messages_preset = chat_history + [
        {
            "role": "user",
            "content": user_input
        }
    ]

    # 调用 ZhipuAI API
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=messages_preset
    )

    # 返回生成的对话
    return jsonify({'response': response.choices[0].message.content}), 200

@app.route('/api/chat-qwen', methods=['POST'])
def chat_qwen():
    try:
        # 从请求中获取消息历史
        messages = request.json.get('messages', [])
        
        # 调用千问API获取回复
        response_content = get_qwen_response(messages)
        
        # 返回API响应
        return jsonify({
            'status': 'success',
            'response': response_content
        })
    except Exception as e:
        print(f"千问API调用错误: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'调用千问API时出错: {str(e)}'
        }), 500


@app.route('/dashboard')
@login_required
def dashboard():
    question_count = 100  # 这里应该从数据库获取实际数据
    user_count = 50
    active_user_count = 30
    recent_activities = [
        "用户A添加了新题目",
        "用户B更新了个人资料",
        "管理员修改系统设置"
    ]
    return render_template('dashboard.html', 
                           question_count=question_count,
                           user_count=user_count,
                           active_user_count=active_user_count,
                           recent_activities=recent_activities)

@app.route('/game-management')
@login_required
def gameManagement():
    return render_template('gameManagement.html')

@app.route('/title-management')
@login_required
def titleManagement():
    total_questions = Question.query.count()
    easy_questions = Question.query.filter_by(difficulty='简单').count()
    medium_questions = Question.query.filter_by(difficulty='中等').count()
    hard_questions = Question.query.filter_by(difficulty='困难').count()
    questions = Question.query.all()
    return render_template('titleManagement.html', 
                           total_questions=total_questions,
                           easy_questions=easy_questions,
                           medium_questions=medium_questions,
                           hard_questions=hard_questions,
                           questions=questions)

@app.route('/user-management')
@login_required
def userManagement():
    return render_template('userManagement.html')

@app.route('/questions')
@login_required
def question_list():
    questions = Question.query.all()
    return render_template('question_list.html', questions=questions)

@app.route('/questions/add', methods=['GET', 'POST'])
@login_required
def add_question():
    form = QuestionForm()
    if form.validate_on_submit():
        question = Question(content=form.content.data, answer=form.answer.data, difficulty=form.difficulty.data)
        db.session.add(question)
        db.session.commit()
        flash('题目已添加成功', 'success')
        return redirect(url_for('question_list'))
    return render_template('add_question.html', form=form)

@app.route('/user_list')
@login_required
def user_list():
    users = User.query.all()
    return render_template('user_list.html', users=users)

@app.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    form = UserForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('用户已添加成功', 'success')
        return redirect(url_for('user_list'))
    return render_template('add_user.html', form=form)

@app.route('/logs')
@login_required
def logs():
    # 这里应该从数据库或日志文件中获取日志数据
    logs = []  # 暂时使用空列表
    return render_template('logs.html', logs=logs)



@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        if form.password.data:
            current_user.password = generate_password_hash(form.password.data)
        db.session.commit()
        flash('个人资料已更新', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('profile.html', form=form)

@app.route('/report')
@login_required
def report():
    # 生成模拟数据
    today = datetime.now()
    dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, 0, -1)]
    
    # 用户活跃度数据
    daily_active_users = [random.randint(50, 200) for _ in range(30)]
    
    # 题目完成情况
    total_questions = 1000
    completed_questions = random.randint(600, 900)
    completion_rate = (completed_questions / total_questions) * 100
    
    # 难度分布
    difficulty_distribution = {
        '简单': random.randint(30, 40),
        '中等': random.randint(40, 50),
        '困难': random.randint(10, 20)
    }
    
    # 用户增长趋势
    user_growth = [random.randint(5, 20) for _ in range(30)]
    
    # 平均答题时间（分钟）
    avg_answer_time = random.uniform(5, 15)
    
    # 最受欢迎的题类型
    popular_question_types = [
        ('算法', random.randint(100, 200)),
        ('数据结构', random.randint(80, 150)),
        ('数据库', random.randint(60, 120)),
        ('网络', random.randint(50, 100)),
        ('操作系统', random.randint(40, 90))
    ]
    
    return render_template('report.html',
                           dates=dates,
                           daily_active_users=daily_active_users,
                           total_questions=total_questions,
                           completed_questions=completed_questions,
                           completion_rate=completion_rate,
                           difficulty_distribution=difficulty_distribution,
                           user_growth=user_growth,
                           avg_answer_time=avg_answer_time,
                           popular_question_types=popular_question_types)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm()
    if form.validate_on_submit():
        # 保存设置
        flash('设置已更新', 'success')
        return redirect(url_for('settings'))
    return render_template('settings.html', form=form)

@app.route('/help')
@login_required
def help():
    return render_template('help.html')




admin = Admin(app, name='管理后台', template_mode='bootstrap4')
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    answer = db.Column(db.String(255), nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)

# 创建管理视图
class UserAdminView(ModelView):
    column_list = ('id', 'username')
    form_columns = ('username', 'password')
    
class QuestionAdminView(ModelView):
    column_list = ('id', 'content', 'difficulty')
    form_columns = ('content', 'answer', 'difficulty')

admin.add_view(UserAdminView(User, db.session))
admin.add_view(QuestionAdminView(Question, db.session))

# 登录表单
class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember = BooleanField('记住我')
    submit = SubmitField('登录')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            print(f"用户 {user.username} 已成功登录")
            return redirect(url_for('home'))
        else:
            return render_template('login.html', form=form, error=True)
    return render_template('login.html', form=form, error=False)

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    
    if user and check_password_hash(user.password, data.get('password')):
        # 生成JWT令牌
        token = create_access_token(identity=user.id)
        return jsonify({
            'status': 'success',
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username
            }
        })
    
    return jsonify({
        'status': 'error',
        'message': '用户名或密码错误'
    }), 401

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    print("访问了home页面")
    return render_template('home.html')

# 创建数据库表
with app.app_context():
    try:
        print(f"\n当前工作目录: {os.getcwd()}")
        print(f"数据库文件路径: {DB_PATH}")
        print(f"上传文件夹路径: {UPLOAD_DIR}\n")
        
        db.create_all()
        
        # 检查是否已存在默认用户
        default_user = User.query.filter_by(username='admin').first()
        if not default_user:
            default_user = User(username='admin', password=generate_password_hash('password'))
            db.session.add(default_user)
            db.session.commit()
            print("默认用户已创建")
        else:
            print("默认用户已存在")
    except Exception as e:
        print(f"数据库初始化错误: {str(e)}")
        db.session.rollback()
        raise

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)
        
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/about')
@login_required
def about():
    return render_template('about.html')

class SettingsForm(FlaskForm):
    site_name = StringField('网站名称', validators=[DataRequired()])
    maintenance_mode = BooleanField('维护模式')
    submit = SubmitField('保存设置')

# 添加 Application 模型定义
class Applications(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, nullable=False)
    app_name = db.Column(db.String(100), nullable=False)
    app_description = db.Column(db.Text)
    creator_name = db.Column(db.String(100))
    app_avatar_path = db.Column(db.String(255))
    doc_file_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    visit_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    favorite_count = db.Column(db.Integer, default=0)
    used_models = db.Column(db.String(255))
    prize = db.Column(db.String(100))
    appId = db.Column(db.String(100))
    type = db.Column(db.Text)

class UserGame(db.Model):
    __tablename__ = 'user_game'  # 显式指定表名
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer)
    app_name = db.Column(db.String(100), nullable=False)
    app_description = db.Column(db.Text)
    creator_name = db.Column(db.String(100))
    app_avatar = db.Column(db.Text)
    user_doc = db.Column(db.Text)
    type = db.Column(db.String(100))
    scene = db.Column(db.Text, nullable=True)

# 创建一个全局的线程池执行器
executor = ThreadPoolExecutor(max_workers=5)

@app.route('/api/create-app', methods=['POST'])
def create_app():
    try:
        app_name = request.form.get('app_name')
        app_description = request.form.get('app_description')
        creator_name = request.form.get('creator_name')
        game_type = request.form.get('game_type')
        story_type = request.form.get('story_type')

        # 打印数据库路径
        db_path = os.path.abspath(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))
        print(f"\n数据库文件路径: {db_path}")
        
        # 打印上传文件夹路径
        upload_folder = os.path.abspath(app.config['UPLOAD_FOLDER'])
        print(f"上传文件夹路径: {upload_folder}\n")

        # 确保上传目录存在
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        
         # 处理头像文件
        app_avatar_path = None
        if 'app_avatar' in request.files:
            avatar_file = request.files['app_avatar']
            if avatar_file and avatar_file.filename:
                filename = secure_filename(f"{app_name}_avatar_{int(time.time())}_{avatar_file.filename}")
                print(f"头像文件名: {filename}")
                # 生成上传凭证
                token = q.upload_token(bucket_name, f'avatar/{filename}')
                # 直接上传文件内容
                ret, info = put_data(token, key=f'avatar/{filename}', data=avatar_file.read())
                if ret is not None:
                    file_key = ret['key']  # 上传后七牛云返回的文件名
                    base_url = 'http://cdn.docuparser.top/'  # 七牛云的默认域名
                    app_avatar_path = base_url + file_key  # 构造完整的文件外链
                    print(f"头像文件已上传到七牛云: {app_avatar_path}")
                else:
                    print(f"上传头像文件失败: {info}")
        
        # 处理文档文件
        doc_file_path = None
        if 'doc_file' in request.files:
            doc_file = request.files['doc_file']
            if doc_file and doc_file.filename:
                # 保存文件到本地
                local_filename = secure_filename(f"{app_name}_doc_{int(time.time())}_{doc_file.filename}")
                local_file_path = os.path.join(app.config['UPLOAD_FOLDER'], local_filename)
                doc_file.save(local_file_path)
                print(f"文档文件已保存到本地: {local_file_path}")

        # 上传文件到线上
        filename = secure_filename(f"{app_name}_doc_{int(time.time())}_{doc_file.filename}")
        print(f"文档文件名: {filename}")
        token = q.upload_token(bucket_name, f'doc/{filename}')
        
        # 读取本地文件内容并上传
        with open(local_file_path, 'rb') as f:
            file_data = f.read()
            ret, info = put_data(token, key=f'doc/{filename}', data=file_data)
        
        if ret is not None:
            file_key = ret['key']  # 上传后七牛云返回的文件名
            base_url = 'http://cdn.docuparser.top/'  # 七牛云的默认域名
            doc_file_path = base_url + file_key  # 构造完整的文件外链
            print(f"文档文件已上传到七牛云: {doc_file_path}")
            # 使用 SQLAlchemy ORM
            new_app = UserGame(
                userId=12619,
                app_name=app_name,
                app_description=app_description,
                creator_name=creator_name,
                app_avatar=app_avatar_path,
                user_doc=doc_file_path,
                type=game_type
            )
        
            db.session.add(new_app)
            db.session.commit()
            print(f"数据已保存到数据库表: userGame")

            moviesName = '绿皮书'  # 设置一个合理的默认值
            if(story_type == 'adventure'):
                moviesName = '千与千寻'
            elif(story_type == 'enlightenment'):
                moviesName = '绿皮书'
            print('电影名', moviesName)
            # 异步获取单词数组并生成场景
            def process_app_creation(local_file_path, app_id, moviesName):
                words_array = get_words_arr(local_file_path)
                print('单词数组', words_array[0])
                generate_scene_task(app_id, moviesName, words_array[0])

            # 提交异步任务
            executor.submit(process_app_creation, local_file_path, new_app.id, moviesName)

            # 立即返回成功响应
            response_data = {
                'message': '应用创建成功',
                'received_data': {
                    'success': True,
                    # 'app_name': app_name,
                    # 'app_description': app_description,
                    # 'creator_name': creator_name,
                    # 'app_avatar': app_avatar_path,
                    # 'doc_file': doc_file_path
                }
            }
            
            return jsonify(response_data), 201
        else:
            print(f"上传文档文件失败: {info}")



        response_data = {
            'message': '应用创建成功',
            'received_data': {
                'success': True,
                # 'app_name': app_name,
                # 'app_description': app_description,
                # 'creator_name': creator_name,
                # 'app_avatar': app_avatar_path,
                # 'doc_file': doc_file_path
            }
        }
        
        return jsonify(response_data), 201
        
    except Exception as e:
        print(f"错误: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-my-apps', methods=['GET'])
def get_my_apps():
    try:
        myApps = UserGame.query.filter_by(userId=12619).all()

        myApps_data = [
            {
                'id': app.id,
                'app_name': app.app_name,
                'app_description': app.app_description,
                'creator_name': app.creator_name,
                'app_avatar': app.app_avatar,
                'user_doc': app.user_doc,
                'type': app.type,
                'scene': app.scene
            }
            for app in myApps
        ]
        
        return jsonify({'myApps': myApps_data}), 200
    except Exception as e:
        print(f"错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-apps', methods=['GET'])
def get_apps():
    try:
        # 查询所有应用数据
        applications = Applications.query.all()
        
        # 将查询结果转换为字典列表
        apps_data = [
            {
                'id': app.id,
                'userId': app.userId,
                'appId': app.appId,
                'app_name': app.app_name,
                'app_description': app.app_description,
                'creator_name': app.creator_name,
                'app_avatar_path': app.app_avatar_path,
                'doc_file_path': app.doc_file_path,
                'created_at': app.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'visit_count': app.visit_count,
                'comment_count': app.comment_count,
                'favorite_count': app.favorite_count,
                'used_models': app.used_models,
                'prize': app.prize,
                'created_at': app.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': app.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'type': app.type
            }
            for app in applications
        ]
        
        return jsonify({'applications': apps_data}), 200
        
    except Exception as e:
        print(f"错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker='redis://localhost:6379/0',  # 使用 Redis 作为消息代理
        backend='redis://localhost:6379/0'
    )
    celery.conf.update(app.config)
    return celery


celery = make_celery(app)


@celery.task
def generate_scene_task(app_id, moviesName, words_array):
    # 生成场景数据
    print(f"开始生成场景数据")
    scene_data = generate_scene(moviesName, words_array)
    print(f"场景数据生成完成")
    # 使用应用上下文
    with app.app_context():
        try:
            # 更新数据库记录
            app_record = UserGame.query.get(app_id)
            if app_record:
                app_record.scene = json.dumps(scene_data)  # 将场景数据转换为 JSON 字符串存储
                db.session.commit()
                print(f"应用 {app_id} 的场景数据已更新")
        except Exception as e:
            print(f"更新应用 {app_id} 的场景数据时出错: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

