# -*- coding: utf-8 -*-
"""
Created on Wed Dec 23 15:56:14 2020

@author: Ryan Johnsen rdjsen@gmail.com
"""

#wrapper for resolution tracker

import pandas as pd
from os import path
from os import getcwd
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import sqlite3
import datetime

FILE_TEMPLATE = ['user_id', 'num', 'resolution', 'type', 'target', 'current', 'cur_percent', 
                 'pace', 'pace_percent']

actions = ['adding', 'updating', 'deleting']

conn = sqlite3.connect('data.db')

#file location

#test = resolutions(path.join(getcwd(), "ryan.csv"))


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
    
    #get user_id
    user_id = update.effective_chat.id
    
    #db connection
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    #get status
    c.execute("""
              SELECT status
              FROM user_status
              WHERE chat_id=?
              """, (user_id,))
    cur_status = c.fetchone()[0]
    
    #verify idling
    
    if cur_status == 'idle':
        #give update
        df = pd.read_sql("""
                         SELECT *
                         FROM resolutions
                         WHERE user_id =?
                         """, conn, params = (user_id,))
        
        #loop to give the update on each one
    else:
        #error message
        pass
    
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
              SELECT status, num
              FROM user_status
              WHERE chat_id=?
              """, (user_id,))
    
    dbpull = c.fetchone()
    cur_status = dbpull[0]
    cur_num = dbpull[1]
    
    if cur_status == 'adding':
        
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
                
                conn.close()
            except (ValueError, IndexError, KeyError):
                #illegal value entered
                context.bot.send_message(chat_id=update.effective_chat.id,
                             text = "Uh-Oh!  Illegal value entered! "
                             "Please try again!")
                
                conn.close()
        
        elif cur_num == 1:
        #prompting description
            description = update.message.text
            
            #calc new_num
            c.execute('''
                      SELECT COUNT(*) 
                      FROM resolutions 
                      WHERE user_id=?
                      ''', (user_id,))
                
            new_num = c.fetchone()[0]
            
            #add description to db
            c.execute("""
                      UPDATE resolutions
                      SET resolution =?
                      WHERE user_id=? 
                      AND num = ?                      
                      """, (description, user_id, new_num))
                
            conn.commit()
            
            #update status - check if yearly or one-off
            
            #get cur_type
            c.execute('''
                      SELECT type 
                      FROM resolutions 
                      WHERE user_id=?
                      AND num =?
                      ''', (user_id, new_num))
                
            cur_type = c.fetchone()[0]
            
            if cur_type == 'Yearly Total':
            
                #if yearly total, move on to prompting for goal and current
                c.execute("""
                          UPDATE user_status
                          SET num = 2
                          WHERE chat_id=?
                          """, (user_id,))
                
                conn.commit()
                conn.close()
                
                #response message
                context.bot.send_message(chat_id=update.effective_chat.id,
                             text = "Perfect!  What is your goal for the year? (Enter a number)")
                
            else:
                #type is one off - end adding
                
                #update status
                c.execute("""
                          UPDATE user_status
                          SET num = 0,
                          status = 'idle'
                          WHERE chat_id=?
                          """, (user_id,))
               
                conn.commit()
                conn.close() 
                
                #response message
                context.bot.send_message(chat_id=update.effective_chat.id,
                             text = "Perfect!  The Resolution has been added!")
                
                update_percents(user_id)
    
        elif cur_num == 2:
            #prompting goal if type is yearly
            try:
                cur_goal = int(update.message.text)
                
                if cur_goal <= 0:
                    #illegal input, but doesn't raise error
                    raise ValueError
                    
                #calc newnum
                c.execute('''
                          SELECT COUNT(*) 
                          FROM resolutions 
                          WHERE user_id=?
                          ''', (user_id,))
                
                new_num = c.fetchone()[0]
                
                #update db
                c.execute("""
                          UPDATE resolutions
                          SET target =?
                          WHERE user_id=? 
                          AND num = ?                      
                          """, (cur_goal, user_id, new_num))
                
                conn.commit()
                
                #update status
                c.execute("""
                          UPDATE user_status
                          SET num = 3
                          WHERE chat_id=?
                          """, (user_id,))
                
                conn.commit()
                conn.close()
                
                #send response
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text = "Fantastic!  How many have you completed?")
                
                
            except ValueError:
                #illegal input
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text = "Whoops!  Illegal value entered.  Try Again!")
            
    
        elif cur_num == 3:
            #prompting current value
            try:
                cur_targ = int(update.message.text)
                
                if cur_targ < 0:
                    #illegal input, but doesn't raise error
                    raise ValueError
                    
                #calc newnum
                c.execute('''
                          SELECT COUNT(*) 
                          FROM resolutions 
                          WHERE user_id=?
                          ''', (user_id,))
                
                new_num = c.fetchone()[0]
                
                #update db
                c.execute("""
                          UPDATE resolutions
                          SET current =?
                          WHERE user_id=? 
                          AND num = ?                      
                          """, (cur_targ, user_id, new_num))
                
                conn.commit()
                
                #update status
                c.execute("""
                          UPDATE user_status
                          SET num = 0,
                          status = 'idle'
                          WHERE chat_id=?
                          """, (user_id,))
                
                conn.commit()
                conn.close()
                
                #send response
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text = 'Perfect!  The Resolution has been added!')
                update_percents(user_id)
                
            except ValueError:
                #illegal input
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text = "Whoops!  Illegal value entered.  Try Again!")
    
        #completed to here but not tested
        
        pass
    elif cur_status == 'updating':
        pass
    elif cur_status == 'deleting':
        pass
    else:
        pass
        #no command currently running
    
# # # ~ ~ ~ Other Functions ~ ~ ~ # # #
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


def update_percents(user_id):
    """update the percent and pace for a given user_id"""
    #TODO update percents
    conn = sqlite3.connect('data.db')
    
    c = conn.cursor()
    
    cur_week_percent = datetime.date.isocalendar(datetime.date.today())[1] / 52
    
    #yearly totals
    #TODO have not tested
    c.execute("""
              UPDATE resolutions
              SET pace = ROUND((? * target)),
              cur_percent = ROUND((current / target * 100), 0),
              pace_percent = ROUND((? * 100), 0)
              WHERE user_id = ?
              AND type = "Yearly Total"
              """, (cur_week_percent, cur_week_percent, user_id))
    
    #TODO one-offs
    
      
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
    
    adding_handler = CommandHandler('add', add_reso)
    dispatcher.add_handler(adding_handler)
    
    input_loop_handler = MessageHandler(Filters.text & (~Filters.command), input_loop)
    dispatcher.add_handler(input_loop_handler)
    
    #start polling
    updater.start_polling()
    
if __name__ == '__main__':
    main()