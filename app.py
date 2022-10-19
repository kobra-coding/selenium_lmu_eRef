import tkinter as tk
import time
import PyPDF2
import os
import shutil
from os import listdir
from os.path import isfile, join


from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from selenium import webdriver
from PyPDF2 import PdfFileMerger


LARGE_FONT = ("Verdana", 16)
NORMAL_FONT = ("Verdana", 12)
SMALL_FONT = ("Verdana", 10)


class PageStart(tk.Frame):
    TITLE = "LMU - Medizin - Thieme"

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text=self.TITLE, font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        self.labelframeUser = tk.LabelFrame(self, text="LMU - Benutzerkennung", padx=20, pady=20)
        self.labelframeUser.pack(pady=50)
        self.labelUser = ttk.Label(self.labelframeUser, text='Benutzername:')
        self.labelUser.pack()
        self.varUser = tk.StringVar()
        self.entryUser = ttk.Entry(self.labelframeUser, width=50, justify="center", textvariable=self.varUser)
        self.entryUser.pack()
        self.labelPwd = ttk.Label(self.labelframeUser, text='Passwort:')
        self.labelPwd.pack()
        self.varPwd = tk.StringVar()
        self.entryPwd = ttk.Entry(self.labelframeUser, width=50, justify="center", textvariable=self.varPwd)
        self.entryPwd.pack()

        self.labelframeBib = tk.LabelFrame(self, text="Thieme - Onlinebibliothek", padx=20, pady=20)
        self.labelframeBib.pack(pady=0)
        self.labelUrl = ttk.Label(self.labelframeBib, text='URL zum Buch:')
        self.labelUrl.pack()
        self.varUrl = tk.StringVar()
        self.entryUrl = ttk.Entry(self.labelframeBib, width=50, justify="center", textvariable=self.varUrl)
        self.entryUrl.pack()
     
        self.btnStart = ttk.Button(self, text="Start", width=50, command=lambda: self.getPdfs())
        self.btnStart.pack(pady=30)

    def getPdfs(self):
        scrape_web(self.entryUrl.get(), self.entryUser.get(), self.entryPwd.get())

class Page2nd(tk.Frame):
    TITLE = "Startseite"

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text=self.TITLE, font=LARGE_FONT)
        label.pack(pady=10, padx=10)


class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # self.attributes('-fullscreen', True)
        self.wm_state('zoomed')
        fn_center_window(self)
        tk.Tk.iconbitmap(self, default="fav.ico")
        tk.Tk.wm_title(self, "LMU - Medizin - Thieme")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # Seiten werden geladen, aber nicht angezeigt
        for F in (PageStart, Page2nd):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(PageStart)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        global active_frame
        active_frame = cont
        # print("var active_frame now: " + str(active_frame))

    def return_frame(self, cont):
        frame = self.frames[cont]
        return frame

    def ask_filename(self):
        filename = filedialog.asksaveasfilename(
            filetypes=[('PDF', '.pdf')], initialfile='Output.pdf'
        )
        if filename:
            return filename
        else:
            return os.path.join(os.path.abspath(os.getcwd()), 'result.pdf')


def fn_center_window(toplevel):
    # https://stackoverrun.com/de/q/754917
    toplevel.update_idletasks()
    w = toplevel.winfo_screenwidth()
    h = toplevel.winfo_screenheight()
    size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
    x = w / 2 - size[0] / 2
    y = h / 2 - size[1] / 3
    toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))


def scrape_web(url, user, pwd):

    path_workingDir = os.path.abspath(os.getcwd())
    path_temp = os.path.join(path_workingDir, "temp")

    try:
        os.mkdir(path_temp)
        print("Ordner erstellt")
    except:
        print("nicht möglich")

    options = webdriver.ChromeOptions()
    options.add_experimental_option('prefs', {
        "download.default_directory": path_temp,
        "download.prompt_for_download": False,  # Download Dialog
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True  # It will not show PDF directly in chrome
    })

    driver = webdriver.Chrome(executable_path='driver/chromedriver.exe', options=options)

    # LOGIN
    driver.get(url) # Url wird aufgerufen
    
    # User
    userfield = driver.find_element_by_xpath('/html/body/div[2]/div[2]/form/table/tbody/tr[1]/td[2]/input')
    userfield.send_keys(user)
    
    # Passwort
    passwordfield = driver.find_element_by_xpath('/html/body/div[2]/div[2]/form/table/tbody/tr[2]/td[2]/input')
    passwordfield.send_keys(pwd)
    
    # Abschicken
    submit = driver.find_element_by_xpath('/html/body/div[2]/div[3]/input')
    submit.click()
    
    # Warten
    time.sleep(2)

    # COOKIES
    btn_cookies = driver.find_element_by_xpath('//*[@id="onetrust-accept-btn-handler"]')
    btn_cookies.click()
    # Warten
    time.sleep(2)

    # Book Information
    try:
        book = {
            "title": driver.find_element_by_xpath('//*[@id="content-container"]/div[1]/div[2]/h1').get_attribute('innerHTML'),
            "author": driver.find_element_by_xpath('/html/body/div[2]/div[11]/div[2]/div[1]/div[1]/a[1]').get_attribute('innerHTML'),
            "date": driver.find_element_by_xpath('/html/body/div[2]/div[6]/div[2]/ul/li[3]').get_attribute('innerHTML')
        }
    except:
        print("Metadaten konnten nicht gelesen werden.")

    # PDF

    i = 1
    while i < 100:
        execute10 = 'time.sleep(1)'
        execute10 += '\nul_elemSub = driver.find_element_by_xpath(\'//*[@id="pdfTocPopover"]/div/div/ul[2]/li[' + str(i) + ']/a[2]\')'
        execute10 += '\nul_elemSub.click()'
        # //*[@id="pdfTocPopover"]/div/div/ul[2]/li[2]/a[2]
        # //*[@id="pdfTocPopover"]/div/div/ul[2]/li[3]/a[2]
        execute11 = 'time.sleep(1)'
        execute11 += '\nul_elemSub = driver.find_element_by_xpath(\'//*[@id="pdfTocPopover"]/div/div/ul[2]/li[' + str(i) + ']/a\')'
        execute11 += '\nul_elemSub.click()'

        btn_pdf = driver.find_element_by_xpath('//*[@id="pdfTocToggle"]')
        btn_pdf.click()
        time.sleep(2)
        try:
            exec(execute10)
        except:
            try:
                exec(execute11)
            except:
                i = 100
        j = 1
        while j < 100:
            execute20 = 'time.sleep(1)'
            execute20 += '\nul_elemSubSubSub = driver.find_element_by_xpath(\'//*[@id="pdfTocPopover"]/div/div/ul[2]/li[' + str(i) + ']/ul/li[' + str(j) + ']/a[2]\')'
            execute20 += '\nul_elemSubSubSub.click()'
            # //*[@id="pdfTocPopover"]/div/div/ul[2]/li[3]/ul/li[1]/a[2]
            # //*[@id="pdfTocPopover"]/div/div/ul[2]/li[2]/ul/li[1]/a[2]
            # //*[@id="pdfTocPopover"]/div/div/ul[2]/li[2]/ul/li[2]/a[2]
            execute21 = 'time.sleep(1)'
            execute21 += '\nul_elemSubSubSub = driver.find_element_by_xpath(\'//*[@id="pdfTocPopover"]/div/div/ul[2]/li[' + str(i) + ']/ul/li[' + str(j) + ']/a\')'
            execute21 += '\nul_elemSubSubSub.click()'
            # //*[@id="pdfTocPopover"]/div/div/ul[2]/li[1]/ul/li[2]/a
            k = 1
            time.sleep(2)
            try:
                exec(execute20)
            except:
                try:
                    exec(execute21)
                except:
                    j = 100
            while k < 100:
                execute3 = 'time.sleep(1)'
                execute3 += '\nul_elemSubSubSubPdf = driver.find_element_by_xpath(\'//*[@id="pdfTocPopover"]/div/div/ul[2]/li[' + str(i) + ']/ul/li[' + str(j) + ']/ul/li[' + str(k) + ']/a\')'
                execute3 += '\nul_elemSubSubSubPdf.click()'
                # //*[@id="pdfTocPopover"]/div/div/ul[2]/li[2]/ul/li[1]/ul/li[1]/a
                # //*[@id="pdfTocPopover"]/div/div/ul[2]/li[2]/ul/li[1]/ul/li[2]/a
                if not k == 1:
                    time.sleep(2)
                    btn_pdf.click()
                    time.sleep(2)
                try:
                    exec(execute3)
                except:
                    k = 100
                k += 1
            j += 1
        i += 1

    driver.quit()

    # Get only files
    onlyfiles = [f for f in listdir(path_temp) if isfile(join(path_temp, f))]
    # print(onlyfiles)

    # PDF merge
    path_temp_file = os.path.join(path_temp, "temp.pdf")
    merger = PdfFileMerger()

    for pdf in onlyfiles:
        merger.append(os.path.join(path_temp, str(pdf)))

    merger.write(path_temp_file)
    merger.close()

    # open temp
    pdfFileObj = open(path_temp_file, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    pages_to_keep = [0]  # page numbering starts from 0
    pages_to_delete = []  # page numbering starts from 0

    i = 1
    while i < pdfReader.numPages:
        pageObj0 = pdfReader.getPage(i)
        pageObj1 = pdfReader.getPage(i - 1)

        text0 = pageObj0.extractText()
        text1 = pageObj1.extractText()
        if text0 == text1:
            pages_to_delete.append(i)
            # print("Match", i)
        else:
            pages_to_keep.append(i)
        i += 1

    # print("keep: ", pages_to_keep)
    # print("delete: ", pages_to_delete)

    output = PyPDF2.PdfFileWriter()

    for i in pages_to_keep:
        p = pdfReader.getPage(i)
        output.addPage(p)

    
    path_result = app.ask_filename()


    with open(path_result, 'wb') as f:
        output.write(f)

    # remove temp PDF
    pdfFileObj.close()
    if os.path.exists(path_temp_file):
        os.remove(path_temp_file)
    else:
        print(path_temp_file + " does not exist")
    
    # remove temp Files
    if os.path.exists(path_temp):
        shutil.rmtree(path_temp, ignore_errors=True)
    else:
        print(path_temp + " does not exist")
    


active_frame = False
app = App()
app.mainloop()
