# -*- coding: utf-8 -*-
"""
Created on Wed Dec 23 15:56:14 2020

@author: rdjse
"""

#wrapper for resolution tracker

import pandas as pd
from class_def import resolutions
from os import path
from os import getcwd
import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
import sqlite3

FILE_TEMPLATE = ['user_id', 'num', 'resolution', 'type', 'target', 'current', 'percent', 
                 'pace', 'pace percent']

conn = sqlite3.connect('data.db')

#file location

test = resolutions(path.join(getcwd(), "ryan.csv"))


def get_token():
    """Read the Token from token.txt"""
    
    token = open(path.join(getcwd(), 'token.txt')).read()
    return token

# # # ~ ~ ~ Functions for commands ~ ~ ~ # # #
def start(update, context):
    """Response to the Start Command"""
    
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text = "Hello World!  I'm a bot that tracks new years "
                             "resolutions for you.  Use /newtrack to begin, or /help for"
                             " a list of commands")

def help_command(update, context):
    """Display available commands"""
    pass

def start_tracking(update, context):
    """Generate a new tracking file"""
    
    #TODO code to check if file exists and confirm overrite (probably with args)
    user_id = update.effective_chat.id
    
    #add to user_data db
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    
# # # ~ ~ ~ Deprecated Code ~ ~ ~ # # #    
#    if path.isfile(str(user_id)+'.csv'):
#        #check for an overrite argument?  -r?
#        context.bot.send_message(chat_id=update.effective_chat.id,
#                             text = "It looks like I am already tracking resolutions"
#                             " for you.")
#        return
#    
#    #create blank file
#    blank_file = open(str(user_id)+'.csv', 'w')
#    blank_file.write(FILE_TEMPLATE)
#    blank_file.close()
# # # ~ ~ ~ End Deprecated Code ~ ~ ~ # # #
    
    #removing any old resolutions
    c.execute("""DELETE FROM resolutions
              WHERE user_id = ?
              """, (user_id,))
    conn.commit()
    
    #checking if currently in dB
    c.execute("""SELECT COUNT(*) FROM user_status WHERE chat_id=?""", (user_id,))
    count = c.fetchone()[0]
    
    if count == 0:
       #table doesn't exist
       c.execute("""INSERT INTO user_status VALUES (?, 'idle', 0)""", (user_id,))
       conn.commit()
    else:
        #table does exist, resetting to default values.  Nothing for now
        c.execute("""
                  UPDATE user_status
                  SET status = 'idle',
                  num = 0
                  WHERE chat_id=?
                  """, (user_id,))
        conn.commit()
    
    conn.close()
    #message to let user know to add resos
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text = "I am now ready to track you resolutions!"
                             " use /add to add a new resolution, and /status to "
                             "see current status of all resolutions.")
    
    
def track(update, context):
    """Response to the track command"""
    
    #TODO verify that user isn't adding, deleting, or updating
    #psuedocode
    #check if file exists for username
    #if not, create one
    #display currently tracked resos
    #prompt user to use /update, /
    
    pass

def add_reso(update, context):
    """add a new resolution"""
    user_id = update.effective_chat.id
    
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("""
              SELECT status
              FROM user_status
              WHERE chat_id=?
              """, (user_id,))
    cur_status = c.fetchone()[0]
    
    #check status, make sure not doing something else
    if cur_status != 'idle':
        #not idling, send error message
        
        context.bot.send_message(chat_id=update.effective_chat.id,
                             text = "Uh oh!  I can't add a new resolution right"
                             " now since you are working on something else.  Finish"
                             " that first!")
    else:
        #idling, change to adding and prompt input
        c.execute("""
                  UPDATE user_status
                  SET status = 'adding',
                  num = 0
                  WHERE chat_id=?
                  """, (user_id,))
        conn.commit()
        
        context.bot.send_message(chat_id=update.effective_chat.id,
                             text = "Ready to add a resolution to the tracker! "
                             "What type do you want to add?  A one-off resolution "
                             "or a yearly total?  Enter 1 for one-off, or 2 for yearly.")

# # # ~ ~ ~ Main Conversation Function ~ ~ ~ # # #
def input_loop(update, context):
    """Handles the adding, updating, and deleting trees"""
    
    #get current user status
    user_id = update.effective_chat.id
    
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("""
              SELECT status
              FROM user_status
              WHERE chat_id=?
              """, (user_id,))
    dbpull = c.fetchone()
    cur_status = dbpull[0]
    cur_num = dbpull[1]
    
    if cur_status == 'adding':
        
        #TODO custom keyboard input?
        if cur_num == 0:
            #Prompting type
            try:
                type_list = {1:'One-Off', 2:'Yearly Total'}
                cur_type = int(update.message.text)
                
                #calc newnum
                c.execute('''
                          SELECT COUNT(*) 
                          FROM resolutions 
                          WHERE user_id=?
                          ''', (user_id,))
                
                new_num = c.fetchone()[0] + 1
                
                c.execute("""INSERT INTO resolutions
                          VALUES (?, ?, "", ?, 0,0,0,0,0)
                          """, (user_id, new_num, type_list[cur_type],))
                
                conn.commit()
                
                #update status
                c.execute("""
                  UPDATE user_status
                  SET num = 1
                  WHERE chat_id=?
                  """, (user_id,))
                
                conn.commit()
                
                #added, send response method
                context.bot.send_message(chat_id=update.effective_chat.id,
                             text = "Great!  What is the resolution?")
                
            except (ValueError, IndexError):
                #illegal value entered
                context.bot.send_message(chat_id=update.effective_chat.id,
                             text = "Uh-Oh!  Illegal value entered! "
                             "Please try again!")
        
        elif cur_num == 1:
            #prompting description
            pass
    
        elif cur_num == 2:
            #prompting goal if type is yearly
            pass
    
        elif cur_num == 3:
            #prompting current value
            pass
    
        
        
        pass
    elif cur_status == 'updating':
        pass
    elif cur_status == 'deleting':
        pass
    else:
        pass
        #no command currently running
    
# # # ~ ~ ~ Other Functions ~ ~ ~ # # #
def file_not_found(update, context):
    """Display that tracking hasn't been started yet"""
    pass

def setup_db():
    """Check if db exists or create it if not"""
    #check if db exists
    #if not create it
    c = conn.cursor()
    
    #checking for user_status table
    c.execute('''SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='user_status' ''')
    
    if c.fetchone()[0] == 0:
        #table doesn't exist
        
        c.execute("""
                  CREATE TABLE user_status
                  (chat_id, status, num)
                  """)
        conn.commit()
        
    #checking for user resos tables
    c.execute('''SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='resolutions' ''')
    
    if c.fetchone()[0] == 0:
        #table doesn't exist
        df = pd.DataFrame(columns=FILE_TEMPLATE)
        df.to_sql('resolutions', conn, index=False)
        
# # # ~ ~ ~ Main ~ ~ ~ # # #
def main():
    """Main Code execution"""
    
    #setting up database
    setup_db()
    conn.close()
    
    bot_token = get_token()
    
    #setting up updater and dispatcher
    updater = Updater(token = bot_token, use_context = True)
    dispatcher = updater.dispatcher
    
    # # # ~ ~ ~ Handlers ~ ~ ~ # # #
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    
    start_tracking_handler = CommandHandler('newtrack', start_tracking)
    dispatcher.add_handler(start_tracking_handler)
    
    #start polling
    updater.start_polling()
    
if __name__ == '__main__':
    main()