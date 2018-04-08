from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://get-it-done:vera2012@localhost:8889/get-it-done'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '11223344'

class Task(db.Model): 

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    completed = db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self,name,owner):
        self.name = name
        self.completed = False
        self.owner = owner


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    tasks = db.relationship('Task', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password


#tells flask to run this function before any incoming request handlers are run

@app.before_request 
def require_login():
    allowed_routes = ['login','register'] #list of routes users dont need to be logged ion to see
    if request.endpoint not in allowed_routes and 'email' not in session: 
        return redirect('/login') 


@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        email= request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email # - "remember" that the user has logged in
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error') # 'error' is a category we use a placeholder on base.html to make it a class to turn text red
            return render_template('login.html')

    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        #TODO - validate

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email # - "remember" that the user has logged in
            return redirect('/')
        else:
            #TODO - user better response messaging
            return "<h1>Duplicate user</h1>"

    return render_template('register.html')

@app.route('/logout')
def logout():
    del session['email'] #<---removes the email session to stop "remembering" user is logged in.
    return redirect('/')


    

@app.route('/', methods=['POST', 'GET'])
def index():
    owner = User.query.filter_by(email=session['email']).first()
    
    if request.method == 'POST':
        task_name = request.form['task']   
        new_task = Task(task_name, owner)
        db.session.add(new_task)
        db.session.commit()
        

    tasks = Task.query.filter_by(completed= False, owner=owner).all()
    completed_tasks = Task.query.filter_by(completed= True, owner=owner).all()

    return render_template('todos.html', title="GET IT DONE!", tasks=tasks, completed_tasks=completed_tasks)

@app.route('/delete-task', methods=['POST'])
def delete_task():
    task_id = int(request.form['task-id'])
    task = Task.query.get(task_id) 
    task.completed = True
    db.session.add(task)
    #db.session.delete(task)  <---for my own learning purposes we used this before we added boolean column in task class now we don't need it
    db.session.commit()

    return redirect('/')




if __name__ == '__main__':
    app.run()