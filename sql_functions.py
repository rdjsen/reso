# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 19:17:16 2021

@author: rdjse
"""

import sqlite3
import datetime

# # # ~ ~ ~ Functions to modify SQL database ~ ~ ~ # # #

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

def delete_reso_db(user_id, num):
    """Delete the current reso"""
    
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    c.execute("""DELETE FROM resolutions
              WHERE user_id = ?
              AND num = ?
              """, (user_id, num))
    
    conn.commit()
    #recalculate nums
    c.execute("""UPDATE resolutions
              SET num = num - 1
              WHERE user_id = ?
              AND num > ?
              """, (user_id,num))
    
    conn.commit()

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