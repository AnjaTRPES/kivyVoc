# -*- coding: ascii -*-
"""
Created on Wed Jul 31 07:23:36 2019

@author: Anja
"""
__version__="0.9"
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
import codecs
from kivy.clock import Clock
from kivy.properties import (
    StringProperty,ObjectProperty
)
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
import os

from kivy.uix.scrollview import ScrollView
import re as re
import random as rd
import time as t
import copy as cp
#import sys
#reload(sys)
#sys.setdefaultencoding("utf-8")

class ScrollableLabel(ScrollView):
    text = StringProperty('')
    
class FloatInput(TextInput):
    pat = re.compile('[^0-9]')
    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if '.' in self.text:
            s = re.sub(pat, '', substring)
        else:
            s = '.'.join([re.sub(pat, '', s) for s in substring.split('.', 1)])
        return super(FloatInput, self).insert_text(s, from_undo=from_undo)
class Word(object):
    
    def __init__(self, lang1,lang2,lang1_notes,lang2_notes,lang1_times_asked,lang2_times_asked,
             lang1_asked_when,lang2_asked_when,counter=3):
        self.lang1=lang1
        self.lang2=lang2
        self.lang1_notes=lang1_notes
        self.lang2_notes=lang2_notes
        self.lang1_times_asked=int(lang1_times_asked)
        self.lang2_times_asked=int(lang2_times_asked)
        self.lang1_asked_when=float(lang1_asked_when)
        self.lang2_asked_when=float(lang2_asked_when)
        #counter is an internal variable useful for asking it
        self.counter=counter
    
    def time_to_ask(self,time_keys,direction):
        if direction=='dir1':
            print('is it time to ask',t.time(),t.time()-self.lang1_asked_when)
            print(time_keys[self.lang1_times_asked])
            if (t.time()-self.lang1_asked_when)>=time_keys[self.lang1_times_asked]:
                return True
            else:
                return False
        else:
            print('is it time to ask dir 2',t.time(),t.time()-self.lang2_asked_when)
            print(time_keys[self.lang2_times_asked])
            try:
                if (t.time()-self.lang2_asked_when)>=time_keys[self.lang2_times_asked]:
                    return True
                else:
                    return False
            except KeyError:
                print(self.lang1,self.lang2,self.lang2_times_asked)
                return False
        
        
class Words():
    all_words=[]
    def delete_word(self,word):
        if self.word_available(word)==True:
            position=self.word_index(word)
            print('the position is',position)
            self.all_words.pop(position)
            
    def add_words(self,new_word):
        #compare whether the words corresponds to one already there
        if self.word_available(new_word)==False:
            self.all_words.append(new_word)
    def word_index(self,test_word):
         if self.all_words!=[]:
            for i,word in enumerate(self.all_words):
                if word.lang1==test_word.lang1 and word.lang2==test_word.lang2:
                    return i

        
    def word_available(self,new_word):
        if self.all_words!=[]:
            for word in self.all_words:
                if word.lang1==new_word.lang1 and word.lang2==new_word.lang2:
                    return True
            return False
        else:
            return False
    def get_word(self,text,language):
        if language=='russian':
            for word in self.all_words:
                if word.lang1==text:
                    return word
        else:
            for word in self.all_words:
                if word.lang2==text:
                    return word
    def size(self):
        return len(self.all_words)
    def update_word(self, lang1,lang2,success=True,direction='dir1'):
        for word in self.all_words:
            if word.lang1==lang1 and word.lang2==lang2:
                if direction=='dir1':
                    if success==True:
                        word.lang1_times_asked+=1
                    else:
                        word.lang1_times_asked=0
                    word.lang1_asked_when=t.time()
                    print(word.lang1_asked_when)
                else:
                    if success==True:
                        word.lang2_times_asked+=1
                    else:
                        word.lang2_times_asked=0
                    word.lang2_asked_when=t.time()
                break
            
    def get_text(self):
        russian=''
        german=''
        for word in self.all_words:
            russian+='[ref='+word.lang1+']'+word.lang1+'[/ref]'+'\n'
            german+='[ref='+word.lang2+']'+word.lang2+'[/ref]'+'\n'        
        return russian, german
    
    def get_text_sorted(self,direction='russian'):
        word_list=[]
        if direction=='russian':
            for word in self.all_words:
                word_list.append(word.lang1+'#'+word.lang2)
        else:            
            for word in self.all_words:
                word_list.append(word.lang2+'#'+word.lang1)
        #sort the word list
        word_list.sort()
        russian=''
        german=''
        if direction=='russian':
            for word_combo in word_list:
                words=word_combo.split('#')
                russian+='[ref='+words[0]+']'+words[0]+'[/ref]'+'\n'
                german+='[ref='+words[1]+']'+words[1]+'[/ref]'+'\n'  
            return russian,german
        else:
            for word_combo in word_list:
                words=word_combo.split('#')
                russian+='[ref='+words[1]+']'+words[1]+'[/ref]'+'\n'
                german+='[ref='+words[0]+']'+words[0]+'[/ref]'+'\n'  
            return russian,german 
        
    
    def get_sample_words(self,max_words_at_once,time_keys,direction='dir1'):
        to_ask=[]
        for word in self.all_words:
            if word.time_to_ask(time_keys,direction)==True:
                to_ask.append(cp.deepcopy(word))
        #randomly select max words out of it
        if len(to_ask)<=max_words_at_once:
            return to_ask
        else:
            return rd.sample(to_ask,k=max_words_at_once)
    
class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
class VokabelTrainer(ScreenManager):
    #structure of all_words:
    # list of words_objects
    all_words=Words()
    german_text=StringProperty('')
    russian_text=StringProperty('')
    russian_new_word=ObjectProperty('')
    german_new_word=ObjectProperty('')
    russian_new_ex=ObjectProperty('')
    german_new_ex=ObjectProperty('')
    filename='my_words2.txt'
    lang1='Russian'
    lang2='German'
    #filename='v2.anjavoc'
    
    #setting parameters
    max_words_at_once=20
    id_maxAmountWords=ObjectProperty('')
    times_to_repeat=3
    id_timesToRepeat=ObjectProperty()
    #unit of time in hours
    time_first=12
    id_1stTime=ObjectProperty()
    time_second=24  
    id_2ndTime=ObjectProperty()
    time_third=48   
    id_3rdTime=ObjectProperty()
    time_fourth=7*24    
    id_4thTime=ObjectProperty()
    time_fifth=14*24
    time_keys={0:0,1:12*60*60,2:24*60*60,3:48*60*60,4:7*24*60*60,5:14*24*60*60}
    
    #define all the properties for direction1
    dir1_russian_word=ObjectProperty()
    dir1_german_word=StringProperty('')
    dir1_russian_ex=StringProperty('')
    dir1_german_ex=StringProperty('')
    dir1_words=[]
    dir1_chosen_word_index=0
    dir1_check_button_text='Check!'
    
    #define all the properties for direction2
    dir2_german_word=ObjectProperty()
    dir2_russian_word=StringProperty('')
    dir2_russian_ex=StringProperty('')
    dir2_german_ex=StringProperty('')
    dir2_words=[]
    dir2_chosen_word_index=0
    dir2_check_button_text='Check!'
    
    #define stuff for modifying words
    word_to_modify=None
    
    def initial(self,folder):
        self.app_folder=folder
        try:
            f=open(os.path.join(self.app_folder,self.filename))
            all_lines=f.readlines()
            f.close()
        except FileNotFoundError:
            f=open(os.path.join(self.app_folder,self.filename),'w+')
            f.close()
        print('try to load this initially',self.filename)
        print(os.path.join(self.app_folder,self.filename))
        self.load_words(os.path.join(self.app_folder,self.filename))
        german_text,russian_text=self.all_words.get_text()
        for word in self.all_words.all_words:
            print(word.lang1,word.lang1_asked_when)
        pass
        
    def load_words_from_file_part_1(self):
        #print('connected!')
        
        content = LoadDialog(load=self.load_words_from_file_part_2, cancel=self.dismiss_popup)
        content.ids.filechooser.path=self.app_folder
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()
        pass
    
    def load_words_from_file_part_2(self,path,filename):
        print('path',path,filename)
        self.dismiss_popup()
        if 'anjavoc' or 'txt' in str(filename).split('.')[-1]:
            print('loading files')
            self.load_words(filename[0])
        
    def load_words(self,filename):
        #filename='all_words.txt'
        #'''
        print(os.path.join(self.app_folder,self.filename))
        try:
            print('try to open a file')
            f=open(filename)
            all_lines=f.readlines()
            f.close()
        except FileNotFoundError:
            print('not found?')
            all_lines=[]
        for line in all_lines:
            print(line)
            if line[:3]=='# #':
                continue
            elif line[:11]=='# language1':
                continue
            elif line[:11]=='# language2':
                continue
            elif line=='':
                continue
            elif line=='\n':
                continue
            else:
                g=line.split('<>')
                if int(float(g[4]))>5 and int(float(g[5]))>5:
                    new_word=Word(g[0],g[1],g[2],g[3],0,0,0,0)
                elif int(float(g[4]))>5:
                    new_word=Word(g[0],g[1],g[2],g[3],0,g[5],0,g[7])
                elif int(float(g[5]))>5:
                    new_word=Word(g[0],g[1],g[2],g[3],g[4],0,g[6],0)
                else:
                    new_word=Word(g[0],g[1],g[2],g[3],g[4],g[5],g[6],g[7])
                self.all_words.add_words(new_word)
                print('word last asked',g[6],g[7])
            self.save_current_words()     
        german_text,russian_text=self.all_words.get_text()
        #print(german_text)
        self.german_text,self.russian_text=german_text,russian_text       
        #self.german_text,self.russian_text=self.all_words.get_text()
        #'''
        pass
    
    def add_new_words(self):
        
        print('pressed add new words')
        print(self.current_screen)
        self.current='NewWords_Screen'
        
        pass
        
    def return_main_screen(self):
                
        self.german_text,self.russian_text=self.all_words.get_text()
        self.current='start_screen'
        
        pass
    
    def add_one_new_word(self,russian_new_word,german_new_word,russian_new_ex,german_new_ex):
        
        #print('need to implement that...')
        #print('Does this work',russian_new_word)
        if russian_new_word!='' and german_new_word!='':
            #print('added new word!')
            new_word=Word(russian_new_word,german_new_word,russian_new_ex,german_new_ex,
                          0,0,0,0)
            if self.all_words.word_available(new_word)==False:
                self.all_words.all_words.append(new_word)
            #print(len(self.all_words.all_words))
            self.ids.russian_new_word.text=''
            self.ids.german_new_word.text=''
            self.ids.russian_new_ex.text=''
            self.ids.german_new_ex.text=''
            self.save_current_words()
        
            

            

    def dismiss_popup(self):
        
        self._popup.dismiss()
        
        pass
    
    def ask_direction_1(self):
        

        #first get an x amount number of words, which specifiy the requirement of asking (implement in class)
        self.dir1_words=self.all_words.get_sample_words(self.max_words_at_once,self.time_keys,direction='dir1')
        #set all the counters of the words to 1
        for word in self.dir1_words:
            word.counter=1       
        #then ask once after another with the counters going downhill
        print('how many words to ask',self.dir1_words)
        if len(self.dir1_words)!=0:
            self.current='Direction1Screen'
            self.ask_word(direction='dir1')
        
    def ask_direction_2(self):
        

        #first get an x amount number of words, which specifiy the requirement of asking (implement in class)
        self.dir2_words=self.all_words.get_sample_words(self.max_words_at_once,self.time_keys,direction='dir2')
        #set all the counters of the words to 1
        for word in self.dir2_words:
            word.counter=1       
        #then ask once after another with the counters going downhill
        if len(self.dir2_words)!=0:
            self.current='Direction2Screen'
            self.ask_word(direction='dir2')


    def ask_word(self,direction):
        
        if direction=='dir1':
            #choose a word
            self.dir1_check_button_text='Check!'
            self.ids.id_dir1_check_button.text='Check!'
            self.ids.dir1_russian_word.text=''
            self.dir1_chosen_word_index=rd.choice(range(len(self.dir1_words)))
            self.dir1_german_word=self.dir1_words[self.dir1_chosen_word_index].lang2
            self.dir1_russian_ex=self.dir1_words[self.dir1_chosen_word_index].lang1_notes
            self.dir1_german_ex=self.dir1_words[self.dir1_chosen_word_index].lang2_notes
            self.ids.dir1_russian_how_many_label.text='Russian('+str(len(self.dir1_words))+')'
            self.ids.dir1_russian_word.background_color=(1,1,1,1)
        else:
            self.dir2_check_button_text='Check!'
            self.ids.id_dir2_check_button.text='Check!'
            self.ids.dir2_german_word.text=''
            self.dir2_chosen_word_index=rd.choice(range(len(self.dir2_words)))
            self.dir2_russian_word=self.dir2_words[self.dir2_chosen_word_index].lang1
            self.dir2_russian_ex=self.dir2_words[self.dir2_chosen_word_index].lang1_notes
            self.dir2_german_ex=self.dir2_words[self.dir2_chosen_word_index].lang2_notes
            self.ids.dir2_german_how_many_label.text='German('+str(len(self.dir2_words))+')'
            self.ids.dir2_german_word.background_color=(1,1,1,1)


        
        pass
       
    
    def check_word_dir1(self,russian):
        
        print('russian!',russian)
        russian=russian.strip()
        if self.dir1_check_button_text=='Next Word':
            print('called here, counter word',self.dir1_words[self.dir1_chosen_word_index].counter)
            if self.dir1_words[self.dir1_chosen_word_index].counter==0:
                #succesfully learnt this word!
                #update the values in the original array
                self.dir1_words[self.dir1_chosen_word_index].lang1_times_asked+=1
                print('updating word reading for delete')
                self.all_words.update_word(self.dir1_words[self.dir1_chosen_word_index].lang1,
                            self.dir1_words[self.dir1_chosen_word_index].lang2,success=True,direction='dir1')
                #Delete it from the dir1_words
                self.dir1_words.pop(self.dir1_chosen_word_index)
                print('deleted the word',len(self.dir1_words))
                self.save_current_words()
            else:      
                self.all_words.update_word(self.dir1_words[self.dir1_chosen_word_index].lang1,
                            self.dir1_words[self.dir1_chosen_word_index].lang2,success=False,direction='dir1')
            if len(self.dir1_words)==0:
                self.return_main_screen()    
            else:     
                self.ids.dir1_russian_word.background_color=(1,1,1,1)  
                self.ask_word(direction='dir1')
        else:
            print('index',self.dir1_chosen_word_index)
            print('len dir1 words', len(self.dir1_words))
            if russian==self.dir1_words[self.dir1_chosen_word_index].lang1:
                self.ids.dir1_russian_word.background_color=(0,1,0,1)
                print('here1')#successfully answered! Make sth green
                self.dir1_words[self.dir1_chosen_word_index].counter-=1
                self.dir1_check_button_text='Next Word'
                self.ids.id_dir1_check_button.text='Next Word'
            else:
                print('not succesfully answered')#make something red
                self.ids.dir1_russian_word.background_color=(1,0,0,1)
                self.dir1_words[self.dir1_chosen_word_index].counter=3
                self.dir1_words[self.dir1_chosen_word_index].lang1_times_asked=0
                self.dir1_check_button_text='Next Word'
                self.ids.id_dir1_check_button.text='Next Word'
                self.ids.dir1_russian_word.text=self.dir1_words[self.dir1_chosen_word_index].lang1
            self.save_current_words()

    def check_word_dir2(self,russian):
        #print('german!',russian)
        russian=russian.strip()
        if self.dir2_check_button_text=='Next Word':
            if len(self.dir2_words)==0:
                self.return_main_screen()
            else:
                self.ids.dir2_german_word.background_color=(1,1,1,1)
                self.ask_word(direction='dir2')
        else:
            if russian==self.dir2_words[self.dir2_chosen_word_index].lang2:
                #successfully answered! Make sth green
                self.ids.dir2_german_word.background_color=(0,1,0,1)
                self.dir2_words[self.dir2_chosen_word_index].counter-=1
                if self.dir2_words[self.dir2_chosen_word_index].counter==0:
                    #succesfully learnt this word!
                    self.dir2_words[self.dir2_chosen_word_index].lang2_times_asked+=1
                    #update the values in the original array
                    self.all_words.update_word(self.dir2_words[self.dir2_chosen_word_index].lang1,
                                self.dir2_words[self.dir2_chosen_word_index].lang2,success=True,direction='dir2')
                    #Delete it from the dir1_words
                    self.dir2_words.pop(self.dir2_chosen_word_index)
                else:      
                    self.all_words.update_word(self.dir2_words[self.dir2_chosen_word_index].lang1,
                                self.dir2_words[self.dir2_chosen_word_index].lang2,success=False,direction='dir2')
                self.dir2_check_button_text='Next Word'
                self.ids.id_dir2_check_button.text='Next Word'
            else:
                #make something red
                self.dir2_words[self.dir2_chosen_word_index].counter=3
                self.dir2_words[self.dir2_chosen_word_index].lang2_times_asked+=1
                self.dir2_check_button_text='Next Word'
                self.ids.id_dir2_check_button.text='Next Word'
                self.ids.dir2_german_word.text=self.dir2_words[self.dir2_chosen_word_index].lang2
                self.ids.dir2_german_word.background_color=(1,0,0,1) 
            self.save_current_words()
        
        pass

    
    def change_settings(self):
        
        self.current='SettingsScreen'
        self.ids.id_maxAmountWords.text=str(self.max_words_at_once)
        self.ids.id_timesToRepeat.text=str(self.times_to_repeat)
        self.ids.id_1stTime.text=str(self.time_first)
        self.ids.id_2ndTime.text=str(self.time_second)
        self.ids.id_3rdTime.text=str(self.time_third)
        self.ids.id_4thTime.text=str(self.time_fourth)
        
        pass

        
    def apply_changed_settings(self,maxAmountWords,timesToRepeat,
                               id_1stTime,id_2ndTime,id_3rdTime,id_4thTime):
        print('need to implement the apply settings part')
        self.return_main_screen()
        self.max_words_at_once=int(maxAmountWords)
        self.times_to_repeat=int(timesToRepeat)
        self.time_first=float(id_1stTime)
        self.time_second=float(id_2ndTime)
        self.time_third=float(id_3rdTime)
        self.time_fourth=float(id_4thTime)        
        self.time_keys={0:0,1:self.time_first*60*60,2:self.time_second*60*60,
                        3:self.time_third*60*60,4:self.time_fourth*60*60,5:48*60*60}
        #'''
        pass
    
    def scroll_moving(self,which):
        #'''
        #print('starting scrolling')
        if which=='russian':
            #print('adjust the german one!')
            #print(self.ids.id_scrollView_german.scroll_y)
            self.ids.id_scrollView_russian.scroll_y=self.ids.id_scrollView_german.scroll_y
        elif which=='german':
            #print('adjust the russian one')            
            #print(self.ids.id_scrollView_russian.scroll_y) 
            self.ids.id_scrollView_german.scroll_y=self.ids.id_scrollView_russian.scroll_y
        #'''
        #pass

    def save_current_words(self):
        #'''
        
        f=codecs.open(os.path.join(self.app_folder,self.filename),mode='w')
        first_line='# # file for anjavoc program, entries seperated by <>'+'\n'
        second_line='# language1='+self.lang1+'\n'
        third_line='# language2='+self.lang2+'\n'
        f.write(first_line)
        f.write(second_line)
        f.write(third_line)
        #write the data
        #list of the data: structure: [[[french,german],[ex1,ex2][counts,right,wrong]],...]
        for word in self.all_words.all_words:
            line=word.lang1+'<>'+word.lang2+'<>'+word.lang1_notes+'<>'+word.lang2_notes+'<>'+str(word.lang1_times_asked)+'<>'
            line+=str(word.lang2_times_asked)+'<>'+str(word.lang1_asked_when)+'<>'+str(word.lang2_asked_when)+'<>'+'\n'
            f.write(line)
            print('line saved',line)
        f.close()
        #'''
        print('saved in',os.path.join(self.app_folder,self.filename))
        #print('finished saving!')
        
    def call_modify_word_screen(self,text,which):
        #'''
        print('jo',text,which)
        self.current='ModifyWords_Screen'
        #get the word that was selected from the 'text'
        self.word_to_modify=self.all_words.get_word(text,which)
        self.ids.russian_modify_word.text=self.word_to_modify.lang1
        self.ids.german_modify_word.text=self.word_to_modify.lang2
        self.ids.russian_modify_ex.text=self.word_to_modify.lang1_notes
        self.ids.german_modify_ex.text=self.word_to_modify.lang2_notes
        #'''
        pass
        
    def delete_word(self,russian, german, russian_ex, german_ex):
        #''
        print('implement delete word')
        self.return_main_screen()
        #delete the word
        self.all_words.delete_word(self.word_to_modify)
        #show modified word list        
        self.german_text,self.russian_text=self.all_words.get_text()
        #safe it
        self.save_current_words()
        #'''
        pass

    def modify_word(self,russian, german, russian_ex, german_ex):
        #'''
        print('implement modify word')
        self.return_main_screen()
        #delete the word
        self.all_words.delete_word(self.word_to_modify)
        #change the word and add it
        self.word_to_modify.lang1=russian
        self.word_to_modify.lang2=german
        self.word_to_modify.lang1_notes=russian_ex
        self.word_to_modify.lang2_notes=german_ex
        self.word_to_modify.lang1_asked_when=0
        self.word_to_modify.lang2_asked_when=0
        self.all_words.add_words(self.word_to_modify)
        #show modified word list        
        self.german_text,self.russian_text=self.all_words.get_text()
        #safe it
        self.save_current_words()
        #'''
        pass

                 
    def sort_alphabetically(self,direction='russian'):     
        #'''  
        self.german_text,self.russian_text=self.all_words.get_text_sorted(direction)
        #'''
        pass
        
           



class VokabelApp(App):
    
    def build(self):
        trainer=VokabelTrainer()
        app_folder=self.user_data_dir
        trainer.initial(app_folder)
        return trainer


if __name__ == '__main__':
    VokabelApp().run()
'''
notes: stuff to look up when I have internet:
a) how to change the starting folder of loading stuff
b) how to make scroll stuff.

'''
