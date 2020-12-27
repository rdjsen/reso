# -*- coding: utf-8 -*-
"""
Created on Wed Dec 23 14:59:18 2020

@author: rdjse
"""


import pandas as pd
import datetime


class resolutions:
    """Class to track new years resolutions"""
    
    def __init__(self, file):
        self.df = pd.read_csv(file)
        self.df.set_index('num', inplace=True)
        self.file = file
        #TODO add a check for missing file and create it.  second argument newfile=false
        
    def status(self):
        """Print Status of Resolutions"""
        
        print(self.df.drop('type', axis=1))
    
    def update(self):
        """Loop through Resolutions and update"""
        
        cur_week = datetime.date.isocalendar(datetime.date.today())[1]
        
        print('\n ~ ~ ~ * * * Starting update of Resolutions. * * * ~ ~ ~ \n' )
        print('Current Week = : ', cur_week)
        #loop through
        for i in range(1,len(self.df)+1):
            cur_reso = self.df.loc[i,'resolution']
            cur_type = self.df.loc[i,'type']
            cur_total = self.df.loc[i,'current']
            cur_goal = self.df.loc[i,'target']
            
            if cur_type == 'Yearly Total':
            
                print(f'\nResolution: {cur_reso} \nTotal Complete: {cur_total} out of {cur_goal}\n')
                cur_add = int(input("\nHow many completed this week?\n"))
            
                self.df.loc[i, 'current'] = self.df.loc[i,'current'] + cur_add
            elif cur_total == 0:
                print(f'\n Resolution: {cur_reso}\n')
                comp = input('Was this completed this week?  1 for yes, 2 for no.\n')
                
                if comp == '1':
                    self.df.loc[i, 'current'] = 1
                    self.df.loc[i, 'percent'] = 'Complete'
                    
                else:
                    self.df.loc[i, 'current'] = 0
                    self.df.loc[i, 'percent'] = 'Incomplete'
                    
        print('\n ~ ~ ~ * * * Update Complete * * * ~ ~ ~ \n' )
        self.update_percentage()
        self.status()
        self._save_csv()        
                
    def add(self, display=True):
        """Add a New Resolution"""
        reso = input('What is the resolution to add? \n')
        res_type_int = input('\n What is the resolution type? 1 for a One-Off, 2 for Yearly Total \n' )
        
        res_type = ''
        
        if res_type_int == '1':
            res_type = 'One-Off'
        else:
            res_type = 'Yearly Total'
            
        res_goal = 0
        cur_prog = 0
        
        if res_type == 'Yearly Total':
            res_goal = int(input('\n What is your goal for the year? (number)\n '))
            cur_prog = int(input('\n How many have been completed so far?\n'))
        else:
            res_goal = 1
            cur_prog = 0
            
        self.df.loc[len(self.df)+1] = [reso, res_type, res_goal, cur_prog, '0 %']
        self.update_percentage()
        
        
        if display == True:
            self.status()      
        #TODO Save function
        
    def delete(self, num):
        """Remove a resolution"""
        self.status()
        num = int(input('\n Which resolution would you like to remove? (Number)\n'))
        
        print(self.df.drop(num, axis=0, inplace = False))
    
        correct = int(input('\nEnter 1 to save changes, or 2 to discard\n'))
        
        if correct == 1:
            self.df.drop(num, axis=0, inplace = True)
            
        #TODO update the resolution numbers
    
    def update_percentage(self):
        """Recalculate Resolution Percentages"""
        
        #code for yearcount
        #calculate percent
        self.df.loc[self.df['type'] == 'Yearly Total', 'percent'] = (
                self.df['current'] / self.df['target']*100)
        
        self.df.loc[self.df['type'] == 'Yearly Total', 'percent'] = (
                self.df.loc[self.df['type'] == 'Yearly Total', 'percent'].apply(round))
        
        #convert to string and add % sign
        self.df.loc[self.df['type'] == 'Yearly Total', 'percent'] = self.df['percent'].apply(str)
        
        self.df.loc[self.df['type'] == 'Yearly Total', 'percent'] = self.df['percent'] + ' %'
        
        #calculate pace
        cur_week = datetime.date.isocalendar(datetime.date.today())[1]
        self.df['pace'] = self.df['target']*(cur_week-1)/52
        self.df['pace'] = self.df['pace'].apply(round)
        
        #pace percent
        self.df['pace percent'] = str(round((cur_week-1)/52*100)) + ' %'
        
        #TODO code to add the yearly percent
    def _save_csv(self):
        """Function to save the dataframe to a csv"""
        self.df.to_csv(self.file)
        
        