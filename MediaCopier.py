#from tkinter import Tk, Frame
from tkinter import Tk, Menu, Frame, Label, Button, Entry, Toplevel, StringVar
from tkinter.messagebox import showinfo, showerror
from tkinter.filedialog import askdirectory
from tkinter.ttk import Progressbar
from VerticalScrollFrame import VerticalScrolledFrame
import os
from datetime import datetime
import time
from glob import glob
from queue import Queue
from threading import Thread
from math import ceil

class MediaCopierGui(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.protocol('WM_DELETE_WINDOW', self.check_if_process_running_or_not)
        self.resizable(False, False)
        self.geometry('750x200')
        self.title('Media Copier')
        self.sourceDir = None
        self.destDir = None
        self.ext = None
        self.__ButtonState = False
        self.files = []
        self.chunkSize = 1024 * 1000
        self.filenameQueue = []
        self.makeWidgets()

###################################################################################
##-------------------------------- GUI PART -------------------------------------##
###################################################################################

    def makeWidgets(self):
        self.makeMenubar()
        self.buttonBox()
        self.operationBox()
        self.scrollFrame()
        #self.tableBox1()

    def makeMenubar(self):
        self.menuBar = Menu(self)
        self.config(menu=self.menuBar)
        self.mainMenu()
        self.helpMenu()

    def mainMenu(self):
        pulldown = Menu(self.menuBar, tearoff=0)
        pulldown.add_command(label='Settings', command=self.settingField)
        pulldown.add_command(label='Exit', command=self.quit)
        self.menuBar.add_cascade(label='Main', menu=pulldown)
    
    def helpMenu(self):
        pulldown = Menu(self.menuBar, tearoff=0)
        pulldown.add_command(label='How-to', command=self.howToInfo)
        pulldown.add_command(label='About', command=self.aboutinfo)
        self.menuBar.add_cascade(label='Help', menu=pulldown)

    def enable_menu(self):
        self.menuBar.entryconfig('Main', state='normal')
       
    def disable_menu(self):
        self.menuBar.entryconfig('Main', state='disabled')
        
    
    def operationBox(self):
        row = Frame(self)
        sourceLab = Label(row, text='Source Path', relief='ridge',  width=30)
        destLab = Label(row, text='Destination Path', relief='ridge',  width=30)
        oprtnLab = Label(row, text='Operation', relief='ridge',  width=40)
        row.pack(side='top', expand='yes', fill='both')
        sourceLab.pack(side='left')
        destLab.pack(side='left')
        oprtnLab.pack(side='left')

    def tableBox1(self):
        while self.filenameQueue:
            if self.__ButtonState:
                paths = self.filenameQueue[0]
                if not os.path.exists(paths[1]):
                    sourceFilename = os.path.split(paths[0])[1]
                    destFilename = os.path.split(paths[1])[1]
                    maximumValue = os.path.getsize(paths[0])
                    #print(maximumValue)

                    row = Frame(self.__veriticalScrollFrame.interior)
                    sourceLab = Label(row, text=r'..\%s\%s' %(self.currentDate, sourceFilename), relief='sunken',  width=30)
                    destLab = Label(row, text=r'..\%s\%s' %(self.currentDate, destFilename), relief='sunken',  width=30)
                    oprtnProgress = Progressbar(row, orient='horizontal', length=250, maximum=maximumValue, mode='determinate', value=0)
 
                    row.pack(side='top', expand='yes', fill='both')
                    sourceLab.pack(side='left', expand='yes', fill='both')
                    destLab.pack(side='left', expand='yes', fill='both')
                    oprtnProgress.pack(side='left', expand='yes', fill='both')

                    """

                    updateQueueValue = Queue()
                    copying_in_thread = Thread(target=self.copyingFiles, args=(maximumValue, paths[0], paths[1], updateQueueValue))
                    copying_in_thread.start()
           
                    while True:
                        time.sleep(0.25)
                        if not updateQueueValue.empty():
                            value = updateQueueValue.get()
                            print(value)
                            oprtnProgress['value'] = value
                            oprtnProgress.update()
                        else:
                            print('job done')
                            break
                    updateQueueValue.task_done()
                    copying_in_thread.join()

                    """

                    updateValue = self.chunkSize
                    with open(paths[0], 'rb') as fileFrom:
                        with open(paths[1], 'wb') as fileTo:
                            for _ in range(int(ceil(maximumValue//self.chunkSize)+1)):
                                bytesForm = fileFrom.read(self.chunkSize)
                                if bytesForm:
                                    fileTo.write(bytesForm)
                                oprtnProgress['value'] = updateValue
                                oprtnProgress.update()
                                updateValue = updateValue+self.chunkSize

                    self.update()
                    self.filenameQueue.remove(paths)
                else:
                    self.filenameQueue.remove(paths)
            else:
                print('operation Interrupted')
                break
        else:
            self.after(3000, self.tableBox1)
        
    def scrollFrame(self):
        self.__veriticalScrollFrame = VerticalScrolledFrame(self)
        self.__veriticalScrollFrame.pack(side='left', expand='yes', fill='both')

    def buttonBox(self):
        def toggleButton():
            if self.__b1['text'] == 'Start':
                self.disable_menu()
                self.__b1.config(text='Stop')
                self.__ButtonState = True
                self.fileNames_fetch_in_threads()
                self.tableBox1()
            else:
                self.enable_menu()
                self.__b1.config(text='Start')
                self.__ButtonState = False

        self.__b1 = Button(self, text='Start', command=toggleButton)
        self.__b1.pack(side='right', expand='yes', anchor='sw', fill='x')
        self.__b1.config(fg='red', font=('courier', 9, 'bold italic'), padx=5, state='disabled')

    def enable_button(self):
        self.__b1.configure(state='normal')

    def disable_button(self):
        self.__b1.configure(state='disabled')

    def settingField(self):
        base = Toplevel(self)
        base.title('Setting')
        base.resizable(False, False)
        base.grab_set()
        root1 = Frame(base)
        root1.pack()
        sourceLabel = Label(root1, text='Source Path')
        sourceLabel.pack(side='left', padx=21)
        self.__sourcevar = StringVar() 
        sourceEntry = Entry(root1, textvariable=self.__sourcevar)
        sourceEntry.pack(side='left')
        button1 = Button(root1, text='Browse', command=self.sourceOpenDirectory)
        button1.pack(side='left')
        sourceEntry.insert('end', self.__sourcevar.get())

        root2 = Frame(base)
        root2.pack()
        destLabel = Label(root2, text='Destination Path')
        destLabel.pack(side='left', padx=10)
        self.__destvar = StringVar()
        destEntry = Entry(root2, textvariable=self.__destvar)
        destEntry.pack(side='left')
        button2 = Button(root2, text='Browse', command=self.destOpenDirectory)
        destEntry.insert('end', self.__destvar.get())
        button2.pack(side='left')

        root3 = Frame(base)
        root3.pack()
        extLabel = Label(root3, text='Name of the Extension')
        extLabel.pack(side='left')
        self.__extvar = StringVar()
        extEntry = Entry(root3, textvariable=self.__extvar)
        extEntry.pack(side='left')

        root4 = Frame(base)
        root4.pack(side='bottom')
        ApplyButton = Button(root4, text='Apply', command=self.setSettings, padx=8)
        ApplyButton.grid(row=0, column=1, padx=8)
        OkButton = Button(root4, text='OK', command=base.destroy)
        OkButton.grid(row=0, column=0)

    def setSettings(self):
        validPath = self.are_SettingFields_valid()
        if validPath:
            self.sourceDir = self.__sourcevar.get()
            self.destDir = self.__destvar.get()
            self.ext = self.__extvar.get()
            self.enable_button()
            #print(M.sourceDir, M.destDir, M.ext)
        else:
            self.disable_button()
            showerror('Setting Field Error!', 'Please input valid paths')

    def are_SettingFields_valid(self):
        paths = False
        for i in (self.__sourcevar, self.__destvar):
            paths = os.path.exists(i.get())
        return paths
            
    def sourceOpenDirectory(self):
        sourcePath = askdirectory()
        if sourcePath:
            self.__sourcevar.set(sourcePath)

    def destOpenDirectory(self):
        destPath = askdirectory()
        if destPath:
            self.__destvar.set(destPath)

    def howToInfo(self):
        showinfo('How-to', 'Goto Main > Setting\n\n1. Select Source Path\n2. Select Destination Path\n3. Give the extension name\n4. Press "Apply" then "OK"')
    
    def aboutinfo(self):
        showinfo('About', 'Media Copier\n\nVERSION: 1.0')

    def check_if_process_running_or_not(self):
        if self.__ButtonState:
            showerror('Process is running','To close the application\nPress "STOP" button to stop copy process')
        else:
            self.quit()


###################################################################################
##------------------------------- LOGIC PART ------------------------------------##
###################################################################################

    def filesNamesFetch(self):
        self.fetchDate()
        currentSourceDateDir = os.path.join(self.sourceDir, self.currentDate)
        currentDestDateDir = os.path.join(self.destDir, self.currentDate)

        if self.is_Source_Dest_Path_Exist(currentSourceDateDir, currentDestDateDir):
            for fileName in glob(r'%s\*.%s' %(currentSourceDateDir, self.ext)):
                if not fileName in self.files:
                    source = fileName
                    destination = os.path.join(currentDestDateDir, os.path.split(fileName)[1])
                    if self.is_sourceFile_completely_received(source):
                        self.filenameQueue.append((source, destination))
                        self.files.append(fileName)

    def fetchDate(self):
        dateNow = datetime.now()
        self.currentDate = dateNow.strftime('%d%m%y')

    def is_Source_Dest_Path_Exist(self, sourcePath, destPath):
        if os.path.exists(sourcePath) and (not os.path.exists(destPath)):
            os.mkdir(destPath)
            return True
        elif os.path.exists(sourcePath) and os.path.exists(destPath):
            return True

    def is_sourceFile_completely_received(self, sourcePath):
        try:
            sourceFileObj = open(sourcePath, 'rb')
        except PermissionError: return False
        else:
            sourceFileObj.close()
            return True

    
    """
    def copyingFiles(self, value, sourceFile, destFile, updateQueueValue):
        updateValue = self.chunkSize
        with open(sourceFile, 'rb') as fileFrom:
            with open(destFile, 'wb') as fileTo:
                for _ in range(int(ceil(value//self.chunkSize)+1)):
                    bytesForm = fileFrom.read(self.chunkSize)
                    if bytesForm:
                        fileTo.write(bytesForm)
                    updateQueueValue.put(updateValue)
                    updateValue = updateValue+self.chunkSize
    """


###################################################################################
##------------------------------- LINK  PART ------------------------------------##
###################################################################################


    def fileNames_fetch_in_threads(self):
        if self.__ButtonState:
            t1 = Thread(target=self.filesNamesFetch)
            t1.start()
            t1.join()
            self.after(30000, self.fileNames_fetch_in_threads)

     

if __name__ == '__main__':
    M = MediaCopierGui()
    M.mainloop()
