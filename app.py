from flask import Flask,request,jsonify,render_template
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt
app=Flask(__name__)
# initialises flask application 
CORS(app)
# to enable cross origin resource sharing so that frontend can interact with backend without any cors issues
client=MongoClient('mongodb://localhost:27017/')
db=client['todo_app']
# todo_app is the name of the database stored on mongodb
users=db['users']
# users collection which stores info about users 
tasks=db['tasks']
# tasks collection whcih stores the info related to teh tasks in todo
@app.route('/', methods=['GET'])
def test():
    return render_template('index.html')

@app.route('/login',methods=['POST'])
def login():
    data=request.get_json()
    # the request body that is sent in the json string format is converted to the python dictioanry in this case data 
    username=data['username']
    password=data['password']
    # extracting the username and password from the data received 
    user= users.find_one({"username":username})
    if(not user):
        return jsonify({"message":"User does not exist Try signing Up"})
        # if users collection in the datavase consists of the username provided by the body
    if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
        # if the user hashed password matches with the password given by the user (text)in the request is converted to bytes and then compared with the hashed password
        return jsonify({"message":"Login successful","user_id":str(user["_id"])}),200
    return jsonify({"error":"Invalid username or password"}),400
@app.route('/signup',methods=['POST'])
def signup():
    data=request.get_json()
    username=data['username']
    password=data['password']
    if users.find_one({"username":username}):
        return jsonify({"error":"Username already exists, Login Instead"}),400
    
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    users.insert_one({"username": username, "password": hashed})
    return jsonify({"message": "User created successfully,Login Successfully"}), 201

@app.route('/tasks',methods=['POST'])
def add_task():
    data=request.get_json()
    user_id=data['user_id']
    task=data['task']
    duration=data['duration']
    tasks.insert_one({"user_id":ObjectId(user_id),"task":task,"duration":duration,"completed": False})
    return jsonify({"message":"Task added successfuly"}),201

@app.route('/tasks/<user_id>', methods=['GET'])
def get_tasks(user_id):
    user_tasks = tasks.find({"user_id": ObjectId(user_id)})
    task_list = [{"id": str(task["_id"]), "task": task["task"],"duration":task['duration'],"completed":task["completed"]} for task in user_tasks]
    return jsonify(task_list), 200

@app.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    new_task = data['task']
    tasks.update_one({"_id": ObjectId(task_id)}, {"$set": {"task": new_task}})
    return jsonify({"message": "Task updated successfully"}), 200

@app.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    tasks.delete_one({"_id": ObjectId(task_id)})
    return jsonify({"message": "Task deleted successfully"}), 200

@app.route('/tasks/<task_id>/complete', methods=['PUT'])
def complete_task(task_id):
    tasks.update_one({"_id": ObjectId(task_id)}, {"$set": {"completed": True}})
    return jsonify({"message": "Task marked as completed"}), 200
@app.route('/sign',endpoint='sign')
def sign():
    return render_template('signup.html')

@app.route('/redirect')
def redirect():
    return render_template('signup.html')

@app.route('/log')
def log():
    return render_template('log.html')

@app.route('/logs',endpoint='logs')
def logs():
    return render_template('log.html')

if __name__ == '__main__':
    app.run(debug=True)
