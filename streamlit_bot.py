import streamlit as st
import google.generativeai as genai
import requests
import os

from dotenv import load_dotenv

load_dotenv()

GENAI_API_KEY=os.getenv('GENAI_API_KEY')
FLASK_API_KEY="http://127.0.0.1:5110"

genai.configure(api_key=GENAI_API_KEY)

def get_gemini_responses(user_message):
    model=genai.GenerativeModel("gemini-1.5-flash")
    response=model.generate_content(user_message)
    return response.text

def save_message(chat_id, role,text):
    """Saves chat messages to database via FLASK API"""
    requests.post(f"{FLASK_API_KEY}/save_message",json={'chat_id':chat_id,'role':role,'text':text})
    
def load_chat_history(chat_id):
    """Loads chat history from the database"""
    response=requests.get(f"{FLASK_API_KEY}/get_history", params={"chat_id": chat_id})
    if response.status_code==200:
        return response.json()
    return[]

def get_all_chats():
    response=requests.get(f"{FLASK_API_KEY}/all_chats")
    if response.status_code==200:
        return response.json()
    return[]

if "chat_id" not in st.session_state:
    st.session_state["chat_id"]=None

if "messages" not in st.session_state:
    st.session_state["messages"]=[]

if "all_chats" not in st.session_state:
    st.session_state["all_chats"]=get_all_chats()

st.title("EchoBot")
st.write("Lets Connect")

st.sidebar.title("Chat Options")
all_chats=st.session_state["all_chats"]
#st.sidebar.write(f"Debug:{all_chats}")
#chat_options={f"Chat{c['chat_id']}":c["chat_id"]for c in all_chats} if all_chats else {}
for chat in all_chats:
    if st.sidebar.button(f"Chat{chat['chat_id']}"):
        new_chat_id=chat["chat_id"]
        if st.session_state["chat_id"] != new_chat_id:
         st.session_state["chat_id"]=new_chat_id
         st.session_state["messages"]=load_chat_history(st.session_state["chat_id"])
         st.rerun()


# selected_chat= st.sidebar.selectbox("Select a chat:", options=list(chat_options.keys()), index=0 if chat_options else None)

# if selected_chat:
#     #st.session_state["chat_id"]=chat_options[selected_chat]
#     new_chat_id=chat_options[selected_chat]
#     if st.session_state["chat_id"] != new_chat_id:
#         st.session_state["chat_id"]=new_chat_id
#         st.session_state["messages"]=load_chat_history(st.session_state["chat_id"])
#         st.rerun()

if st.sidebar.button("New Chat"):
   response=requests.post(f"{FLASK_API_KEY}/new_chat")
   if response.status_code==200:
       st.session_state["chat_id"]=response.json()["chat_id"]
       st.session_state["messages"]=[]
       st.session_state["all_chats"]=get_all_chats()
       st.rerun()

if st.session_state["chat_id"] is None:
    response=requests.post(f"{FLASK_API_KEY}/new_chat")
    if response.status_code==200:
        st.session_state["chat_id"]=response.json()["chat_id"]

# if st.session_state["chat_id"]:
#      st.session_state["messages"]=load_chat_history(st.session_state["chat_id"])
    
   
# if "messages" not in st.session_state:
#      if "chat_id" in st.session_state and st.session_state["chat id"]:
#          st.session_state.message=load_chat_history(st.session_state["chat_id"])
#      else:
#          st.session_state=[]

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

for msg in st.session_state.messages:
    if isinstance(msg,dict):
        role,text=msg["role"],msg["text"]
    else:
        role,text=msg
    if role=="user":
        st.chat_message("user").markdown(f"**You**:{text}")
    else:
        st.chat_message("BOT").markdown(f"**BOT**:{text}")


user_input= st.text_input("TYPE YOUR MESSAGE:",key ="user_input")


if st.button("Send"):
    if user_input:
        chat_id=st.session_state.get("chat_id")
        if chat_id:
            #st.session_state.messages.append(("user",user_input))
            st.session_state.messages.append({"role": "user", "text": user_input}) 
            save_message(chat_id,"user",user_input)
            bot_response=get_gemini_responses(user_input)
            st.session_state.messages.append({"role": "BOT", "text": bot_response})  
            #st.session_state.messages.append(("BOT",bot_response))
            save_message(chat_id,"BOT",bot_response)
            st.session_state.pop("user_input")
            st.rerun()
        else:
            st.error("Chat ID is missing")
    else:
        st.warning("Please enter a message!")
