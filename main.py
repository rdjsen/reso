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
                             " use /add to add a new resolution, and /track to "
                             "see current status of all resolutions.")
    
    
def track(update, context):
    """Response to the track command"""
    
    #get user_id
    user_id = update.effective_chat.id
    
    #db connection
    conn = sqlite3.connect('data.db')
    
    #get status
    cur_status = get_status(user_id)
    
    #verify idling
    if cur_status == None:
        "user isn't currently tracking"
        context.bot.send_message(chat_id=update.effective_chat.id,text = 
                                 "Looks like you haven't started tracking yet. "
                                 "Use /newtrack begin!")
        
    elif cur_status[0] == 'idle':
        #give update
        
        num_resos = count_resos(user_id)
        
        if num_resos == 0:
            #not tracking any
            context.bot.send_message(chat_id=update.effective_chat.id,
                             text = "Looks like you haven't added any resolutions "
                             "yet.  Use /add to add some!")
        else:
            #tracking resos.  Enter loop
            df = pd.read_sql("""
                             SELECT *
                             FROM resolutions
                             WHERE user_id =?
                             """, conn, params = (user_id,))
            for i in range(len(df)):
                #loop over all resos
                
                reso = df.loc[i]
                
                if reso['type'] == 'Yearly Total':
                    #yearly total message
                    message = (f"Resolution {i+1} / {num_resos} :"
                    f" {reso['resolution']}.  You have completed {reso['current']} "
                    f"out of {reso['target']} good for {reso['cur_percent']}%.  "
                    f"The pace for this point in the year is {int(float(reso['pace']))} which "
                    f"is {reso['pace_percent']}%.")
                    
                elif int(reso['current']) == 1:
                    #completed one off
                    message = (f"Resolution {i+1} / {num_resos} :"
                    f" {reso['resolution']}.  You have completed this resolution!")
                else:
                    #incomplete one-off
                    message = (f"Resolution {i+1} / {num_resos} :"
                    f" {reso['resolution']}.  You have not completed this resolution yet.")
                    pass
                
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text = message)   
            
    else:
        #error message
        context.bot.send_message(chat_id=update.effective_chat.id,
                             text = "Looks like you are currently working on something else."
                             "  Finish that first!")

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
    if cur_status == None:
        "user isn't currently tracking"
        context.bot.send_message(chat_id=update.effective_chat.id,text = 
                                 "Looks like you haven't started tracking yet. "
                                 "Use /newtrack begin!")
        
    elif cur_status != 'idle':
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
def start_updating(update, context):
    """start the updating loop"""
    
     #get user_id
    user_id = update.effective_chat.id
    
    #db connection
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    #get status
    dbpull = get_status(user_id)
    
    cur_status = dbpull[0]
    cur_num = dbpull[1]
    
    #verify idling
    if cur_status == None:
        "user isn't currently tracking"
        context.bot.send_message(chat_id=update.effective_chat.id,text = 
                                 "Looks like you haven't started tracking yet. "
                                 "Use /newtrack begin!")
        
    elif cur_status == 'idle':
        #give update
        
        num_resos = count_resos(user_id)
        
        if num_resos == 0:
            #not tracking any
            context.bot.send_message(chat_id=update.effective_chat.id,
                             text = "Looks like you haven't added any resolutions "
                             "yet.  Use /add to add some!")
        else:
            #tracking resos.  Change status to updating and prompt first one
            update_status(user_id, 'updating', 1)
            
            c.execute("""SELECT * FROM resolutions
                      WHERE user_id = ? AND num = 1""", (user_id,))
                      
            reso = c.fetchone()
            
            description = reso[2]
            cur_type = reso[3]
            cur_progress = reso[5]
            cur_target = reso[4]
            
            if cur_type == 'Yearly Total':
                #yearly total
                message = (f"Resolution 1 / {num_resos}: {description}.  You've completed"
                           f" {cur_progress} out of {cur_target}.  How many have you"
                           f" completed since the last update?")
            
                
            else:
                #one-off
                message = (f"Resolution 1 / {num_resos}: {description}.  "
                           f"Has this been completed?  Enter 1 for yes or 2 for no.")
            
            context.bot.send_message(chat_id=update.effective_chat.id,
                                         text = message)
            
    else:
        #not currently idling
        context.bot.send_message(chat_id=update.effective_chat.id,
                             text = "Uh oh!  I can't update resolutions right"
                             " now since you are working on something else.  Finish"
                             " that first!")
        
                     


# # # ~ ~ ~ Main Conversation Function ~ ~ ~ # # #
def input_loop(update, context):
    """Handles the adding, updating, and deleting trees"""
    
    #get current user status
    user_id = update.effective_chat.id
    
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    #get user status    
    dbpull = get_status(user_id)
    
    cur_status = dbpull[0]
    cur_num = dbpull[1]
    
    if cur_status == None:
        "user isn't currently tracking"
        context.bot.send_message(chat_id=update.effective_chat.id,text = 
                                 "Looks like you haven't started tracking yet. "
                                 "Use /newtrack begin!")
        
    elif cur_status == 'adding':
        
        if cur_num == 0:
            #Prompting type
            try:
                type_list = {1:'One-Off', 2:'Yearly Total'}
                cur_type = int(update.message.text)
                
                new_num = count_resos(user_id) + 1
                
                c.execute("""INSERT INTO resolutions
                          VALUES (?, ?, "", ?, 0,0,0,0,0)
                          """, (user_id, new_num, type_list[cur_type],))
                
                conn.commit()

                #update status                
                update_status(user_id, 'adding', 1)
                
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
            
            new_num = count_resos(user_id)
            
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
                
                update_status(user_id, 'adding', 2)
                
                conn.commit()
                conn.close()
                
                #response message
                context.bot.send_message(chat_id=update.effective_chat.id,
                             text = "Perfect!  What is your goal for the year? (Enter a number)")
                
            else:
                #type is one off - end adding
                
                update_status(user_id, 'idle', 0)
                
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
                new_num = count_resos(user_id)
                
                #update db
                c.execute("""
                          UPDATE resolutions
                          SET target =?
                          WHERE user_id=? 
                          AND num = ?                      
                          """, (cur_goal, user_id, new_num))
                
                conn.commit()
                
                #update status                
                update_status(user_id, 'adding', 3)
                
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
                new_num = count_resos(user_id)
                
                #update db
                c.execute("""
                          UPDATE resolutions
                          SET current =?
                          WHERE user_id=? 
                          AND num = ?                      
                          """, (cur_targ, user_id, new_num))
                
                conn.commit()
                
                #update status               
                update_status(user_id, 'idle', 0)
                
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
        #updating resos
        
        #give update
        
        num_resos = count_resos(user_id)
        
        dbpull = get_status(user_id)

        cur_status = dbpull[0]
        cur_num = dbpull[1]
        
        try:
            update_value = int(update.message.text)
            
            #checking if the last update 
            #getting old reso
            c.execute("""SELECT * FROM resolutions
                      WHERE user_id = ? AND num = ?""", (user_id, cur_num))
                      
            old_reso = c.fetchone()
            
            old_description = old_reso[2]
            old_type = old_reso[3]
            old_progress = old_reso[5]
            old_target = old_reso[4]
            
            if old_type == 'One-Off' and update_value not in [1,2]:
                #illegal value entered
                raise ValueError
                
            elif old_type == 'One-Off' and update_value == 1:
                #one off has been completed 
                
                c.execute("""UPDATE resolutions
                          SET current = 1
                          WHERE user_id = ? and num =?
                          """, (user_id, cur_num))
                
                conn.commit()
                
            elif old_type == 'Yearly Total':
                #yearly total reso
                c.execute("""UPDATE resolutions
                          SET current = current + ?
                          WHERE user_id = ? and num =?
                          """, (update_value, user_id, cur_num))
                
                conn.commit()
                
            
            #checking if this was the last one
            
            if cur_num == num_resos:
                #this was the last one
                
                #update status
                update_status(user_id, 'idle', 1)
                update_percents(user_id)
                
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text = 'Update Complete!  Use /track to '
                                         'see your updated progress!')
            else:
                #more resos to go, prompt the next one
                #getting next reso
                c.execute("""SELECT * FROM resolutions
                          WHERE user_id = ? AND num = ?""", (user_id, cur_num+1))
                      
                reso = c.fetchone()
            
                cur_description = reso[2]
                cur_type = reso[3]
                cur_progress = reso[5]
                cur_target = reso[4]
                
                if cur_type == 'Yearly Total':
                    #yearly total
                    message = (f"Resolution {cur_num+1} / {num_resos}: {cur_description}.  You've completed"
                               f" {cur_progress} out of {cur_target}.  How many have you"
                               f" completed since the last update?")
            
                
                else:
                    #one-off
                    message = (f"Resolution {cur_num+1} / {num_resos}: {cur_description}.  "
                               f"Has this been completed?  Enter 1 for yes or 2 for no.")
                
                update_status(user_id, 'updating', cur_num+1)
                
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text = message)              
                
            
            
        except ValueError:
            #illegal value entered        
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text = 'Uh-Oh!  Illegal value entered. Try Again!')
        
    elif cur_status == 'deleting':
        #TODO change this and add a deleting command with arguments
        pass
    else:
        pass
        #no command currently running

    
# # # ~ ~ ~ SQL Functions ~ ~ ~ # # #
def get_status(user_id):
    """Retrieve user status from database"""
    
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("""
              SELECT status, num
              FROM user_status
              WHERE chat_id=?
              """, (user_id,))
    
    return c.fetchone()


def update_status(user_id, status, num):
    """update SQL db with provided status"""

    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute("""
              UPDATE user_status
              SET num = ?,
              status = ?
              WHERE chat_id=?
              """, (num, status, user_id))
              
    conn.commit()

def count_resos(user_id):
    """get the current number of resos for a user"""
    
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    c.execute('''
              SELECT COUNT(*) 
              FROM resolutions 
              WHERE user_id=?
              ''', (user_id,))
                
    return c.fetchone()[0]


def update_percents(user_id):
    """update the percent and pace for a given user_id"""
    conn = sqlite3.connect('data.db')
    
    c = conn.cursor()
    
    cur_week_percent = datetime.date.isocalendar(datetime.date.today())[1] / 52
    
    #yearly totals
    c.execute("""
              UPDATE resolutions
              SET pace = ROUND((? * target)),
              cur_percent = ROUND(current*100.0 / target, 2),
              pace_percent = ROUND((? * 100.0), 2)
              WHERE user_id = ?
              AND type = "Yearly Total"
              """, (cur_week_percent, cur_week_percent, user_id))
    
    conn.commit()
    #TODO one-offs

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



      
# # # ~ ~ ~ Main ~ ~ ~ # # #
def main():
    """Main Code execution"""
    
    #setting up database
    setup_db()
    #conn.close()
    
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
    
    track_handler = CommandHandler('track', track)
    dispatcher.add_handler(track_handler)
    
    update_handler = CommandHandler('update', start_updating)
    dispatcher.add_handler(update_handler)
    
    
    #start polling
    updater.start_polling()
    
if __name__ == '__main__':
    main()