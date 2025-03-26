from flask import Flask, request,jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS
from flask_migrate import Migrate
import os


app=Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///chat_history.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
db=SQLAlchemy(app)

migrate = Migrate(app, db)

class ChatSession(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    created_at=db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    chat_id= db.Column(db.Integer,db.ForeignKey('chat_session.id'), nullable=False)
    role=db.Column(db.String(10),nullable=False)
    text=db.Column(db.Text,nullable=False)
    created_at=db.Column(db.DateTime, default=datetime.utcnow)

if os.path.exists("chat_history.db"):
     os.remove("chat_history.db")

with app.app_context():
    db.create_all()

@app.route('/save_message',methods=['POST'])
def save_message():
    data=request.json
    chat_id=data.get("chat_id")
    if not chat_id:
        return jsonify({"error":"chat_id is required"}),400
    
    new_message=Message(chat_id=chat_id,role=data["role"],text=data["text"])
    db.session.add(new_message)
    db.session.commit()
    return jsonify({'message':'SAVED'})

@app.route('/get_history',methods=['GET'])
def get_history():
    chat_id= request.args.get("chat_id",type=int)
    if not chat_id:
        return jsonify({"error":"chat_id is required"}),400
    messages=Message.query.filter_by(chat_id=chat_id).order_by(Message.created_at).all()
    #messages=Message.query.order_by(Message.created_at).all()
    history=[{"role":msg.role,"text":msg.text}for msg in messages]
    return jsonify(history)

@app.route('/new_chat',methods=['POST'])
def new_chat():
    new_chat=ChatSession()
    db.session.add(new_chat)
    db.session.commit()
    return jsonify({'chat_id':new_chat.id})

@app.route('/all_chats',methods=['GET'])
def all_chats():
    chats=ChatSession.query.all()
    result=[]
    
    for chat in chats:
        messages=Message.query.filter_by(chat_id=chat.id).order_by(Message.created_at).all()
        chat_messages=[{"role":msg.role,"text":msg.text}for msg in messages]

        result.append({
            "chat_id":chat.id,
            "messages":chat_messages
        })
    return jsonify(result)


if __name__=='__main__':
    app.run(debug=True,port=5110)
