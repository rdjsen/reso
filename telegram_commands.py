# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 19:20:15 2021

@author: rdjse
"""
import sqlite3
import pandas as pd
from time import sleep

#importing my modules
from sql_functions import (get_status, 
                           update_status,
                           count_resos, 
                           delete_reso_db, 
                           )

# # # ~ ~ ~ Functions for commands ~ ~ ~ # # #
def help_command(update, context):
    """Display available commands"""
    
    command_list = ("/start - Reset the bot.  This will DELETE any current resolutions.\n" +
                    "/track - List all current resolutions and status.\n" +
                    "/add - Add a new resolution to the list.\n" +
                    "/update - Give an update for each Resolution. \n" +
                    "/delete <num> - Delete resolution <num> from the list.")
    
    
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text = command_list)
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
                #wait 1 second for the next one
                sleep(1)
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
        
                     
def delete_reso(update, context):
    """Handles deleting a reso passed as args"""

    user_id = update.effective_chat.id
    
    #get user status    
    dbpull = get_status(user_id)
    
    cur_status = dbpull[0]
    
    if cur_status == None:
        "user isn't currently tracking"
        context.bot.send_message(chat_id=update.effective_chat.id,text = 
                                 "Looks like you haven't started tracking yet. "
                                 "Use /start begin!")
    elif cur_status == 'idle':
        try:
            cur_num = int(context.args[0])
            
            if not (cur_num > 0 and cur_num <= count_resos(user_id)):
                #out of range error
                raise ValueError
            
            delete_reso_db(user_id, cur_num)
            
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text = "Resolution Deleted.  Use /track to"+
                                     " see an updated list.")
            
        except (ValueError, NameError):
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text = "Illegal value enetered.  Usade: /delete <num>")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text = "Uh oh!  I can't delete resolutions right"
                                 " now since you are working on something else.  Finish"
                                 " that first!")
