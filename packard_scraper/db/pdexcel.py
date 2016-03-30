'''
Created on Jun 23, 2015

@author: Gregory Kramida
@copyright: 2015 Gregory Kramida
'''
import pandas as pd
from pandas.io.excel import ExcelWriter
import os
from datetime import datetime
from packard_scraper.items import FellowProfile


class PandasExcelHelper(object):
    '''
    A helper class to help write notices to and read them from excel
    '''
    #how frequently to save the scraped items, i.e. interval of 5 means
    #5 items are saved at a time.
    save_interval = 1


    def __init__(self, db_filename = "profiles_database.xlsx",
                 report_prefix = "report", 
                 sheet_name = "profiles",
                 index_column = "url",
                 report_only_new = True):
        '''
        Constructor
        '''
        if(not os.path.isfile(db_filename)):
            #generate a blank writable excel sheet from scratch
            field_names = [field_name for field_name in FellowProfile.fields]
            writer = ExcelWriter(db_filename)
            profile_dataframe = pd.DataFrame(columns = field_names)
            profile_dataframe.to_excel(writer,sheet_name)
            writer.save()
            writer.close()
        
        self.report_filename = (report_prefix + "_" 
                                + str(datetime.today())[:19]
                                .replace(":","_").replace(" ","[") + "].xlsx")
        #kept for posterity, in case only the date component is needed and we don't care about overwrites
        #self.report_filename = report_prefix + "_" + str(date.today())
        self.db_filename = db_filename
        self.sheet_name = sheet_name
        self.profile_dataframe = pd.read_excel(db_filename,sheet_name, index_col = index_column)
        self.usaved_sol_counter = 0
        self.profile_counter = 0
        self.added_items = set()
        self.index_column = index_column
        
    
    def generate_report(self):
        '''
        Generates a separate excel report, consisting of non-award-type notices
        that are not yet overdue
        '''
        print "\n\n========  Generating report...  ========"
        df = self.profile_dataframe.copy()
        ix = pd.Series([(True if ix in self.added_items else False ) 
                                      for ix in df.index ],
                                      index=df.index)
        report_df = df[ix == True]
        
        writer = ExcelWriter(self.report_filename)
        report_df.to_excel(writer,self.sheet_name,merge_cells=False)
        writer.save()
        writer.close()
        
        print "========  Report Generated as " + self.report_filename + " ========\n"
        
        
    def add_item(self,item):
        '''
        Adds the item to the proper dataframe
        '''
        item = dict(item)
        
        key = item[self.index_column]
        item_body = {}
        
        for field_name in item:
            if not field_name == self.index_column:
                item_body[field_name] = item[field_name]
        
        item_series = pd.Series(name=key,data=item_body)
        
        self.added_items.add(key)
        self.profile_dataframe.loc[key] = item_series
            
        if(self.profile_counter < PandasExcelHelper.save_interval):
            self.profile_counter += 1
        else:
            self.profile_counter = 0
            self.save_all()

        
    def save_all(self):
        '''
        Dumps all solicitations in both databases to an excel file
        '''
        print "\n\n========  Saving {:s}  ========".format(self.sheet_name)
        writer = ExcelWriter(self.db_filename)
        self.profile_dataframe.to_excel(writer,self.sheet_name,merge_cells=False)
        writer.save()
        writer.close()
        print "========  Done saving.  ========\n"
        
    def contains(self,key):
        '''
        Checks whether the key is present in the dataframe
        '''
        return key in self.profile_dataframe.index