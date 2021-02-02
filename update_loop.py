# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 19:38:26 2021

@author: rdjse
"""
import sqlite3

#importing my modules
from sql_functions import (get_status, 
                           update_status,
                           count_resos,  
                           update_percents
                           )


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
            
            old_type = old_reso[3]
            
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
    else:
        pass
        #no command currently running