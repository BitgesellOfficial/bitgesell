#E#Importing the libraries
from playsound import playsound
from gtts import gTTS
import sys
from selenium import webdriver

#Creating a function for text to speech to be used in a user friendly manner
def speak(text, filename):
        tts = gTTS(text = text, lang = 'en') #Defining the text to speech handle
        tts.save(filename + '.mp3') #Saving the audio file
        playsound(filename + '.mp3') #Playing the audio
        
print("Welcome to bitgesell!") #Greeting the user

speak("Welcome to bitgesell!", '111') #First impplementation of text to speech protocol

speak('''
Enter 1 to know about bitgesell
Enter 2 to watch tutorial on bitgesell
Enter 3 to contribute to the bitgesell community through writing code
Enter anything else to exit''', '112') #Providing the user with a bunch of options

command1 = int(input('''
Enter 1 to know about bitgesell
Enter 2 to watch tutorial on bitgesell
Enter 3 to contribute to the bitgesell community through writing code
Enter anything else to exit'''))

#Flow of control begins here
if command1 == 1:
    print('''
    BGL is an experimental digital currency that enables instant payments to anyone, anywhere in the world. 
    BGL uses peer-to-peer technology to operate with no central authority: managing transactions and issuing money are 
    carried out collectively by the network. BGL Core is the name of open source software which enables the use of 
    this currency.

    For more information read the original BGL whitepaper.

    ''')
    
    input("Press Enter to exit....")
    
    sys.exit() #Exiting the system
    
elif command1 == 2:
    driver = webdriver.Chrome('chromedriver.exe')
    driver.get("https://www.youtube.com/watch?v=_ggEdYZK6eI")
    
    input('Press Enter to exit....')
    
    sys.exit() #Exiting the system
    
elif command1 == 3:
    driver = webdriver.Chrome('chromedriver.exe')
    driver.get("https://github.com/bitgesellofficial/bitgesell")
    
    speak('''Go through the code files and make pull requests to contribute through code changes. Find bugs and resolve 
          them for the community.''', '113')
    print('''Go through the code files and make pull requests to contribute through code changes. Find bugs and resolve 
          them for the community.''')
    
    input("Press enter to exit....")
    
    sys.exit() #Exiting the system
    
#Flow of control ends here

#End of program
