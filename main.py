# -*- coding: utf-8 -*-
"""
Created on Wed Dec 23 15:56:14 2020

@author: Ryan Johnsen rdjsen@gmail.com
"""

#wrapper for resolution tracker

import pandas as pd
from os import path
from os import getcwd
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import sqlite3


#importing my module
from telegram_commands import (help_command,
                               start_tracking,
                               track,
                               add_reso,
                               start_updating,
                               delete_reso)

from update_loop import input_loop

FILE_TEMPLATE = ['user_id', 'num', 'resolution', 'type', 'target', 'current', 'cur_percent', 
                 'pace', 'pace_percent']

actions = ['adding', 'updating', 'deleting']

conn = sqlite3.connect('data.db')

#file location

def get_token():
    """Read the Token from token.txt"""
    
    token = open(path.join(getcwd(), 'token.txt')).read()
    return token

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
    dispatcher.add_handler(CommandHandler('start', start_tracking))   
    dispatcher.add_handler(CommandHandler('add', add_reso)) 
    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), input_loop))
    dispatcher.add_handler(CommandHandler('track', track))
    dispatcher.add_handler(CommandHandler('update', start_updating))
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(CommandHandler('delete', delete_reso))
    
    #start polling
    updater.start_polling()
    updater.idle()
    
if __name__ == '__main__':
    main()