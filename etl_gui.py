import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import pandas as pd
import numpy as np
import json
import sqlalchemy
from itertools import zip_longest


# Statics
LARGE_FONT = ("Helvetica", 12)
NORMAL_FONT = ("Helvetica",10)
SMALL_FONT = ("Helvetica",8)


settings = {}


tk.have_avbin = True
# df_csv = 'None'
chars = 'Empty'
col_char = 'Empty'


# Defining functions

def grouper(iterable,n,fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=None)


def popupmsg(msg):
    popup = tk.Tk()
    popup.iconbitmap("icon.ico")
    popup.wm_title("!")
    label = ttk.Label(popup, text=msg,font=NORMAL_FONT)
    label.pack(side="top",fill="x",pady=10)
    B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
    B1.pack()
    popup.mainloop()





def load_base():

    file_path = filedialog.askopenfilename(title='Select file',
                                           filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
    global df_csv
    df_csv = pd.read_csv(file_path, encoding="ISO-8859-1")
    popupmsg('File loaded.')
    return df_csv




def save_settings():
    if settings:
        with open('settings.json', 'w') as sett:
            json.dump(settings, sett)

def printara(*args):
    print('I print:',[var_name for var_name in args],'.')



def load():
    global load_parameter
    load_parameter = 1
    with open("settings.json", "r") as infile:
        json_data = json.loads(infile.read())
    settings.update(json_data)





def col_len(df):
    n_cols = {}
    for name in df.columns:
        n_cols[name] = df[name].astype('str').map(len).max()

    return n_cols




class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox('all')
            )
        )

        canvas.create_window((0,0), window=self.scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left',fill='both',expand=True)
        scrollbar.pack(side='right',fill='y')

class DataSQLImport(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.iconbitmap(self, "icon.ico")
        tk.Tk.wm_title(self, 'SQL Load Tool')

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        menubar = tk.Menu(container)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label='Open', command=load_base)
        # filemenu.add_command(label='Save settings', command=lambda: [save_settings(),popupmsg('Settings saved...')])
        # filemenu.add_command(label='Load recent parameters', command=lambda: [load(),popupmsg('Settings loaded ...')])
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=self.destroy)
        menubar.add_cascade(label="File", menu=filemenu)

        tk.Tk.config(self, menu=menubar)

        self.frames = {}

        for F in (StartPage, PageTwo, PageThree):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()




class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        # button1 = ttk.Button(self, text="Importing", command=lambda: controller.show_frame(PageOne))
        # button1.pack()

        button2 = ttk.Button(self, text="Connecting", command=lambda: controller.show_frame(PageTwo))
        button2.pack()

        button3 = ttk.Button(self, text="Validating", command=lambda: controller.show_frame(PageThree))
        button3.pack()



# Connect
class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text="Page Two", font=LARGE_FONT)
        label.pack(pady=10, padx=10)



        tk.Label(self, text="Server").pack()
        e0 = tk.Entry(self)
        e0.pack()

        tk.Label(self, text="Database").pack()
        e1 = tk.Entry(self)
        e1.pack()



        tk.Label(self, text="Table").pack()
        e2 = tk.Entry(self)
        e2.pack()




        def connect(settings):
            settings['server'] = e0.get()
            settings['database'] = e1.get()
            settings['table'] = e2.get()



            SERVER = settings.get('server')
            DATABASE = settings.get('database')
            DRIVER = 'ODBC+Driver+17+for+SQL+Server'
            DATABASE_CONNECTION = f'mssql+pyodbc://@{SERVER}/{DATABASE}?driver={DRIVER}'
            global engine
            engine = sqlalchemy.create_engine(DATABASE_CONNECTION, fast_executemany=True)
            engine.connect()
            popupmsg('Connection made!')
            save_settings()
            return engine

        def fill_parameters():
            load()
            e0.delete(0,tk.END)
            e1.delete(0,tk.END)
            e2.delete(0,tk.END)

            e0.insert(tk.END, settings.get('server',0))
            e1.insert(tk.END, settings.get('database',0))
            e2.insert(tk.END, settings.get('table', 0))


        button0 = ttk.Button(self, text="Connect", command=lambda: connect(settings))
        button0.pack()

        # button1 = ttk.Button(self, text="Validate", command=lambda: controller.show_frame(PageThree))
        # button1.pack()



        button2 = ttk.Button(self, text="Load recent parameters", command=lambda: fill_parameters())
        button2.pack()

        button3 = ttk.Button(self, text="Back to Main", command=lambda: controller.show_frame(StartPage))
        button3.pack()




# Validation page
class PageThree(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)





        frame1 = ScrollableFrame(self)

        frame1.pack(side='left', fill='both', expand=1)

        # Frame 1
        #
        # frame1 = tk.Frame(self)
        # frame1.pack(side='left', fill='both', expand=1)


        def refresh():
            for widget in frame1.scrollable_frame.winfo_children():
                widget.destroy()
            for widget in frame2.scrollable_frame.winfo_children():
                widget.destroy()



        def populate_source(df):
            for i, item in enumerate(col_len(df).keys()):

                index = str(i)
                row_index1 = ttk.Label(frame1.scrollable_frame, text='Source index:', font=LARGE_FONT).grid(row=0,column=0)
                row_name1 = ttk.Label(frame1.scrollable_frame, text='Source column name:', font=LARGE_FONT).grid(row=0,
                                                                                                           column=1)
                item = ttk.Label(frame1.scrollable_frame, text=item, font=NORMAL_FONT)
                index = ttk.Label(frame1.scrollable_frame, text=index, font=NORMAL_FONT)
                index.grid(row=i+1, column=0,padx=5)
                item.grid(row=i+1, column=1,padx=5)
            for i, item in enumerate(col_len(df).values()):
                row_name2 = ttk.Label(frame1.scrollable_frame, text='Source column length:',font=LARGE_FONT).grid(row=0,column=2)
                item = ttk.Label(frame1.scrollable_frame, text=item, font=NORMAL_FONT)
                item.grid(row=i+1, column=2,padx=5)





        # Frame 2

        frame2 = ScrollableFrame(self)
        frame2.pack(side='right', fill='both', expand=1)


        def populate_target():
            schema_info_statement = f"SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{settings['table']}'"
            schema = pd.read_sql(schema_info_statement,engine)
            schema = schema[['COLUMN_NAME', 'CHARACTER_MAXIMUM_LENGTH']]

            for i, item in enumerate(schema.iloc[:,0]):
                index = str(i)
                row_index1 = ttk.Label(frame2.scrollable_frame, text='Target index:', font=LARGE_FONT).grid(row=0, column=0)
                row_name1 = ttk.Label(frame2.scrollable_frame, text='Target column name:', font=LARGE_FONT).grid(row=0,
                                                                                                           column=1)
                item = ttk.Label(frame2.scrollable_frame, text=item, font=NORMAL_FONT)
                index = ttk.Label(frame2.scrollable_frame, text=index, font=NORMAL_FONT)
                index.grid(row=i+1, column=0,padx=5)
                item.grid(row=i + 1, column=1, padx=5)
            for i, item in enumerate(schema.iloc[:,1]):
                row_name2 = ttk.Label(frame2.scrollable_frame, text='Target column length:', font=LARGE_FONT).grid(row=0, column=2)
                item = ttk.Label(frame2.scrollable_frame, text=item, font=NORMAL_FONT)
                item.grid(row=i + 1, column=2, padx=5)






        # Frame 3


        message = tk.StringVar()
        message.set('Please validate before injesting. Column number must be equal, as column names. Make sure for the datasource not to exceed the maxchar of target table')
        message_info = tk.Message(self, textvariable = message,
                                  text=' of target table',
                                  width=200)

        message_info.pack()



        frame3 = tk.Frame(self)
        frame3.pack(side='top', fill='both', expand=1, anchor='n')


        def update_message(element, message):
            element.set(message)






        def popupentry():

            popentry = tk.Tk()
            popentry.iconbitmap("icon.ico")
            popentry.wm_title("!")

            label = ttk.Label(popentry, text='Search field:')
            label.pack()
            source_id = tk.Entry(popentry)
            source_id.pack() #side="top", fill="x", pady=10


            def check_duplicates():
                columnerino = source_id.get()
                sql1 = f"SELECT {columnerino} FROM {settings['table']}"
                df1 = pd.read_sql(sql1, con=engine)
                duplicates = pd.merge(df_csv[columnerino],df1,  how='inner', on=columnerino)
                with open('duplicates.txt', 'w') as dup:
                    dup.write(str(list(duplicates)))
                popupmsg(f'{len(duplicates)} duplicates found!')

            def drop_columns():
                droperino = source_id.get()
                df_csv.drop(columns=droperino,inplace=True)
                popupmsg(f'{droperino} deleted!')

            def rename_columns():
                renamerino = source_id.get()
                source,target = renamerino.split(':')
                df_csv.rename({source:target},inplace=True, axis=1)
                popupmsg(f'{source} changed to {target} successfully!')

            def clean_date():
                cleanerino = source_id.get()
                df_csv[cleanerino] = pd.to_datetime(df_csv[cleanerino])
                df_csv[cleanerino] = df_csv[cleanerino].dt.strftime('%Y-%5-%d %H-%M-%S')
                popupmsg(f'{cleanerino} is cleaned!')





            Button1a = ttk.Button(popentry, text="Check for Duplicates", command= lambda: check_duplicates())
            Button1a.pack()
            Button1b = ttk.Button(popentry, text="Delete column", command= lambda: drop_columns())
            Button1b.pack()
            Button1c = ttk.Button(popentry, text="Rename column", command= lambda: rename_columns())
            Button1c.pack()
            Button1d = ttk.Button(popentry, text="Clean date", command= lambda: clean_date())
            Button1d.pack()
            Button2 = ttk.Button(popentry, text="Exit", command=popentry.destroy)
            Button2.pack()
            popentry.geometry('600x400')
            popentry.mainloop()





        def import_data():
            df_csv.to_sql(settings['table'], con=engine, index=False, if_exists='append')


        button30 = ttk.Button(frame3, text="Populate", command=lambda: [refresh(),populate_source(df_csv),populate_target(),update_message(message,'-1.0 means MAXCHAR. NaN is usually a Date type')])
        button30.pack()

        button30a = ttk.Button(frame3, text="Check and Transform", command=lambda: popupentry())
        button30a.pack()


        button30b = ttk.Button(frame3, text="Import Data", command=lambda: [import_data(),update_message(message,'Data imported in SQL Server successfully!')])
        button30b.pack()

        button31 = ttk.Button(frame3, text="Back to Main",  command=lambda: controller.show_frame(StartPage))
        button31.pack()


        button32 = ttk.Button(frame3, text="Exit", command=lambda: self.destroy)
        button32.pack()


app = DataSQLImport()
app.geometry('1280x720')
app.mainloop()



