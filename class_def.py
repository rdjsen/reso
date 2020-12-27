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
        
        return(self.df.drop('type', axis=1))
        
    def update(self, num, add):
        """Increase reso <num> by <add>"""
        
        self.df.loc[num, 'current'] = self.df.loc[num,'current'] + add
        
        cur_type = cur_type = self.df.loc[num,'type']
        
        if (cur_type == 'One-Off') and (self.df.loc[num, 'current'] >= self.df.loc[num, 'target']):
            #if a oneoff is completed
            self.df.loc[num, 'percent'] = 'Complete'
        
        #saving
        self.update_percentage()
        self._save_csv()
        
            
                
    def add(self, reso, res_type, goal, current):
        """Add a New Resolution"""
        
        if res_type == 'Yearly Total':
            self.df.loc[len(self.df)+1] = [reso, res_type, goal, current, '0 %', 0, 0]
        elif current < goal:
            self.df.loc[len(self.df)+1] = [reso, res_type, goal, current, 'Incomplete', 0, 0]
        else:
            self.df.loc[len(self.df)+1] = [reso, res_type, goal, current, 'Complete', 0, 0]
        
        self.update_percentage()
        self._save_csv()
        
    def delete(self, num):
        """Remove reso <num>"""
        
        self.df.drop(num, inplace=True)
        self.df.reset_index(inplace=True)
        
        #loop to fix the numbers
        for i in range(0, len(self.df)):
            self.df.loc[i, 'num'] = i + 1
        
        self.df.set_index('num', inplace=True)
        self._save_csv()
    
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
        
        
        #percent for one offs
        
        
        #calculate pace
        cur_week = datetime.date.isocalendar(datetime.date.today())[1]
        self.df['pace'] = self.df['target']*(cur_week-1)/52
        self.df['pace'] = self.df['pace'].apply(round)
        
        #pace percent
        self.df['pace percent'] = str(round((cur_week-1)/52*100)) + ' %'
        
        
    def _save_csv(self):
        """Function to save the dataframe to a csv"""
        self.df.to_csv(self.file)
        
    #iteration
    def resos_list(self):
        """Generator for the resolutions"""
        for i in range(1, len(self.df)+1):
            yield self.df.loc[i]
   
         
# # # ~ ~ ~ DEPRECIATED CODE ~ ~ ~ # # #
def old_update(self):
        """Loop through Resolutions and update - will be removed"""
        
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

def old_delete(self, num):
        """Remove a resolution - will be deleted"""
        self.status()
        num = int(input('\n Which resolution would you like to remove? (Number)\n'))
        
        print(self.df.drop(num, axis=0, inplace = False))
    
        correct = int(input('\nEnter 1 to save changes, or 2 to discard\n'))
        
        if correct == 1:
            self.df.drop(num, axis=0, inplace = True)
                 

def old_add(self, display=True):
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
        