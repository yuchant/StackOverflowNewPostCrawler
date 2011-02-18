"""
Stack Overflow Post Checker
===========================

Parse stackoverflow HTML for questions, store in sqlite database
and send notifications of new questions.

By Yuji Tomita
2/7/2011
"""
import os
import sqlite3
import urllib2
import BeautifulSoup
import Growl


class StackOverflowFetcher:
    def __init__(self):
        self.base_url = 'http://stackoverflow.com/questions/tagged/'
        self.get_or_create_database()
        
        self.growl = Growl.GrowlNotifier(applicationName='StackOverflowChecker', notifications=['new'])
        self.growl.register()
        
        for tag in ('django','python'):
            self.get_questions(tag)
            
        self.close_connection()
        
    def get_questions(self, tag):
        """
        Parse target URL for new questions.
        """
        url = self.base_url + tag
        html = urllib2.urlopen(url).read()
        soup = BeautifulSoup.BeautifulSoup(html)
        
        questions = soup.findAll('h3')
        
        for question in questions:
            element = question.find('a')
            link = element.get('href')
            question = element.text
            
            if self.check_if_new(link):
                self.growl.notify(noteType='new', title='[%s] StackOverflow Post' % tag, description=question, sticky=True)
                self.record_question(link, question)
                
        
        
        
    def get_or_create_database(self):
        """
        Check if database file exists. Create if not.
        Open file and send query. 
        If query fails, create tables. 
        """
        path = os.path.join(os.path.dirname(__file__), 'questions.db')
        
        try:
            f = open(path)
        except IOError:
            f = open(path, 'w')
        f.close()
        
        self.conn = sqlite3.connect(path)
        
        try:
            self.conn.execute('SELECT * from questions')
        except sqlite3.OperationalError:
            self.create_database()
            
            
    def create_database(self):
        self.conn.execute('CREATE TABLE questions(link VARCHAR(400), text VARCHAR(300));')
        
        
    def check_if_new(self, link):
        results = self.conn.execute('SELECT * FROM questions WHERE questions.link = "%s";' % link).fetchall()
        if not results:
            return True
        return False
    
    
    def record_question(self, link, question):
        results = self.conn.execute('INSERT INTO questions(link, text) VALUES ("%s", "%s");' % (link, question))
    
    
    def close_connection(self):
        self.conn.commit()
        self.conn.close()


stack = StackOverflowFetcher()
