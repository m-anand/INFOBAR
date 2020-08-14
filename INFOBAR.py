#!/usr/bin/env python3
# INFOBAR Interface for batch processing ICA-AROMA
# Copyright (C) 2020  Manish Anand
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path
from bs4 import BeautifulSoup
import subprocess, json, threading, statistics, time, webbrowser
import concurrent.futures

name='INFOBAR'
version='2.0'

# helper class for common gui widgets
class Elements:
    def __init__(self, master):
        self.master = master

    # method for all button processes
    def button(self, char, funct, lambdaVal, x_, y_, algn, rows):
        if lambdaVal == '':
            self.b = tk.Button(self.master, text=char, command=funct)
        else:
            self.b = tk.Button(self.master, text=char, command=lambda: funct(lambdaVal))
        self.b.grid(row=y_, column=x_, sticky=algn, rowspan=rows, ipadx=5, ipady=5)

    # method for calling a text entry dialog
    def textField(self, lbl, w_, x_, y_):
        textField = tk.Entry(self.master, width=w_)
        textField.grid(row=y_, column=x_ + 1, sticky=tk.W, ipadx=5, ipady=5)
        textField_lbl = tk.Label(self.master, text=lbl)
        textField_lbl.grid(row=y_, column=x_, sticky=tk.E, ipadx=5, ipady=5)
        return textField

    def check(self, char, var, x_, y_):
        check = tk.Checkbutton(self.master, text=char, variable=var)
        check.grid(column=x_, row=y_)

    def label1(self, char, x_, y_, algn, rows, cols):
        self.b = tk.Label(self.master, text=char)
        self.b.grid(row=y_, column=x_, sticky=algn, rowspan=rows, columnspan=cols)

    def label2(self, charVariable, x_, y_, algn):
        self.b = tk.Label(self.master, textvariable=charVariable)
        self.b.grid(row=y_, column=x_, sticky=algn)

# helper class for settings
class config:
    def __init__(self):
        self.readSettings()
        self.allocate()

    def readSettings(self):
        with open(Path(__file__).parent.absolute()/'settings.json') as settingsFile:
            self.settings_dict = json.load(settingsFile)

    def allocate(self):
        self.icaPath = self.settings_dict["icaPath"]
        self.prefeat_identifier = self.settings_dict['prefeat_identifier']
        self.output_identifier = self.settings_dict['output_identifier']
        self.user_options=self.settings_dict["user"]
        self.default_options = self.settings_dict["defaults"]

    def reverse_allocate(self):
        self.settings_dict["icaPath"] = self.icaPath
        self.settings_dict['prefeat_identifier'] = self.prefeat_identifier
        self.settings_dict['output_identifier'] = self.output_identifier
        self.settings_dict['user']=self.user_options

    def writeSettings(self):
        self.reverse_allocate()
        with open(Path(__file__).parent.absolute()/'settings.json', 'w') as json_file:
            json.dump(self.settings_dict, json_file)

    def loadDefaults(self):
        self.settings_dict["user"] = self.settings_dict["defaults"].copy()

#-----------------------------------------------------------------------------------------------------------------------

class Menubar:
    def __init__(self, parent, config, **kwargs):
        self.parent = parent
        self.config=config
        self.menubar = tk.Menu(self.parent)
        self.settings = self.add_menu('Settings',
                                      commands=[("Settings", self.Settings, True), ("Quit", self.ifQuit, False)])
        self.help = self.add_menu("Help", commands=[("Help", self.help, True), ("About", self.about, False)])
        self.parent.config(menu=self.menubar)

    # method to add menu items
    def add_menu(self, menuname, commands):
        menu = tk.Menu(self.menubar, tearoff=0)
        for command in commands:
            menu.add_command(label=command[0], command=command[1])
            if command[2]:
                menu.add_separator()
        self.menubar.add_cascade(label=menuname, menu=menu)

    # Menuitem associated functions
    def Settings(self):
        settings_root = tk.Toplevel()
        Settings(settings_root,self.config)

    def ifQuit(self):
        import sys
        sys.exit()

    def about(self):
        ab = tk.Toplevel()
        About(ab)

    def help(self):
        url = 'help/Manual.pdf'
        webbrowser.open(url, new=1)

class Settings:
    def __init__(self, parent,config):
        self.parent = parent
        self.config=config
        self.parent.geometry('600x200')

        self.parent.title('Settings')
        self.icaPath = tk.StringVar()

        # frames for organization
        self.f1 = tk.Frame(self.parent)
        self.f1.grid(column=0, row=0,columnspan=2)
        self.f2 = tk.LabelFrame(self.parent, text='Parameters')
        self.f2.grid(column=0, row=1)
        self.f3 = tk.Frame(self.parent)
        self.f3.grid(column=0, row=2, sticky='W', pady=5)
        self.f4 = tk.LabelFrame(self.parent, text='File Options')
        self.f4.grid(column=1, row=1, sticky='W')

        # ICA  selection
        self.f_files = Elements(self.f1)
        self.f_files.label2(self.icaPath, 1, 0, tk.E)
        self.f_files.button('ICA-AROMA Location', self.select_icaFile, '', 0, 0, tk.W, 2)

        # Parameters
        self.f_params = Elements(self.f2)
        self.tr = self.f_params.textField('tr (secs)', 5, 0, 1)
        self.D = self.f_params.textField('dim ', 5, 0, 2)
        self.den = self.f_params.textField('den', 5, 0, 3)
        self.tr.insert(0,self.config.user_options[0])
        self.D.insert(0,self.config.user_options[1])
        self.den.insert(0,self.config.user_options[2])

        # File extensions options
        self.file_options=Elements(self.f4)
        # Extensions to remove
        self.extension_identifier = self.file_options.textField("Pre feat Identifier", 20, 0, 0)
        # Output folder identifier
        self.output_identifier = self.file_options.textField("Output Identifier", 20, 0, 1)

        # Save and Defaults options
        self.f_save = Elements(self.f3)
        self.f_save.button('Save', self.save, '', 1, 0, 'W', 1)
        self.f_save.button('Defaults', self.defaults, '', 0, 0, 'W', 1)

        # Load current
        self.icaPath.set(self.config.icaPath)
        self.extension_identifier.insert(0, self.config.prefeat_identifier)
        self.output_identifier.insert(0,self.config.output_identifier)

    def save(self):
        self.config.prefeat_identifier = self.extension_identifier.get()
        self.config.output_identifier = self.output_identifier.get()
        self.config.user_options=[self.tr.get(),self.D.get(),self.den.get()]
        self.config.writeSettings()
        self.parent.destroy()

    def defaults(self):
        self.config.loadDefaults()
        self.tr.delete(0, 'end')
        self.D.delete(0, 'end')
        self.den.delete(0, 'end')

        self.tr.insert(0, self.config.default_options[0])
        self.D.insert(0, self.config.default_options[1])
        self.den.insert(0, self.config.default_options[2])

        print('Defaults loaded')

    # Function calling directory picker
    def select_icaFile(self):
        self.pathToIca = tk.filedialog.askopenfilename(filetypes=[("Python Files","*.py")])
        self.config.icaPath = self.pathToIca
        self.icaPath.set(self.pathToIca)


class About:
    def __init__(self, parent):
        self.parent = parent
        self.parent.title("About "+name)
        self.parent.geometry('400x300')
        self.parent.columnconfigure(0, weight=1)
        self.parent.resizable(width=False, height=False)

        lb1 = tk.Label(self.parent, text=name, font=("Arial Bold", 20))
        lb1.grid(row=0, sticky='NSEW')

        lb2 = tk.Label(self.parent, text=f"Version: {version}\nLicense: LGPL\nCopyright (C) 2020  Manish Anand \n\nThis program comes with ABSOLUTELY NO WARRANTY.\nThis is free software, and you are welcome to redistribute \nit under certain conditions.\n\nSpecial thanks to: \n Jed A. Diekfuss \n Alexis B. Slutsky-Ganesh \n Dustin R. Grooms \n Scott Bonnette \n Gregory D. Myer",justify="left")
        lb2.grid(row=2, sticky='EW')


#-----------------------------------------------------------------------------------------------------------------------

class Viewer:

    def __init__(self,parent):
        self.parent=parent
        parent.protocol("WM_DELETE_WINDOW", self.do_nothing)
        parent.minsize(300, 400)
        self.parent.title(name+': Image Viewer')
        self.fr=tk.Frame(parent,borderwidth=1, padx=20,pady=10)
        self.fr.pack(fill ="both", expand = True)

    def display(self, im_list, mode):
        self.clearFrame(self.fr)

        # Unprocessed viewer
        if mode == 1:
            self.main_im_list = im_list
            self.labels = ['Translation', 'Rotation', 'Displacement']
            frame = self.fr
            self.main_image_viewer(frame)

        # Processed but not post processed
        if mode == 2:
            frame = self.fr
            self.IC_im_list = im_list
            self.scroll_viewer_setup(frame)
            self.scroll_viewer()

        # Post processed
        if mode == 3:
            self.main_im_list = [im_list[-2], im_list[-1]]
            self.labels = ['zstat Lightbox', 'Model Fit']
            # Post processed viewer frame
            frame = tk.Frame(self.fr,borderwidth=1, padx=20,pady=10)
            frame.pack(side='right')
            self.main_image_viewer(frame)

            # Motion IC viewer frame
            frame_left = tk.Frame(self.fr,borderwidth=1,  padx=20, pady=10)
            frame_left.pack(side='left')
            self.IC_im_list = im_list[:len(im_list) - 2]
            self.scroll_viewer_setup(frame_left)
            self.scroll_viewer()


    def main_image_viewer(self, frame):
        el = Elements(frame)
        for i in range(0, len(self.main_im_list)):
            el.label1(self.labels[i], 0, 2*i, 'nesw', 1, 1)
            self.fr.rowconfigure(2*i+1, weight=1)
            im_path = self.main_im_list[i]
            photo = tk.PhotoImage(file=im_path)
            label = tk.Label(frame, image=photo, pady=20)
            label.photo = photo
            label.grid(row=2*i+1)


    def scroll_viewer_setup(self,fr):
        self.ic = len(self.IC_im_list)
        self.j = 0
        self.count = tk.StringVar()
        self.count.set(f'{self.j + 1} of {self.ic} Motion associated independent components')
        el = Elements(fr)
        el.button('Previous', self.scroll, -1, 0, 0, 'e', 1)
        el.button('  Next  ', self.scroll, 1, 1, 0, 'w', 1)
        el.label2(self.count, 2, 0, 'w')
        self.frame_scroll = tk.Frame(fr, borderwidth=1,  padx=20, pady=10)
        self.frame_scroll.grid(row=1, columnspan=10, sticky='nsew')


    def scroll(self, scr):
        self.j += scr
        if (self.j >= self.ic):
            self.j = self.ic-1
        if self.j<0:
            self.j = 0
        self.count.set(f'{self.j + 1} of {self.ic} components')
        self.clearFrame(self.frame_scroll)
        self.scroll_viewer()

    def scroll_viewer(self):
        ic_im_path = self.IC_im_list[self.j]
        photo = tk.PhotoImage(file=ic_im_path)
        label = tk.Label(self.frame_scroll, image=photo, pady=20)
        label.photo = photo
        label.grid(row=0, sticky='nsew')

    def clearFrame(self,frame):
        # destroy all widgets from frame
        for widget in frame.winfo_children():
           widget.destroy()

    @staticmethod
    def do_nothing():
        pass

#-----------------------------------------------------------------------------------------------------------------------

class MainArea(tk.Frame):
    def __init__(self, master, stat, viewer, config, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)

        self.stat = stat
        self.viewer=viewer
        self.config=config
        self.overwrite = tk.IntVar()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.master = master

        # Frame for all controls
        self.f1 = tk.LabelFrame(self, text='Controls', borderwidth=1, padx=10, pady=10, relief='raised')
        self.f1.grid(row=0, column=0, sticky='NSEW')

        # Frame for Tree View
        self.f2 = tk.Frame(self, borderwidth=0, relief='raised', pady=10)
        self.f2.grid(row=1, column=0, sticky='NSEW')
        self.f2.columnconfigure(0, weight=1)
        self.f2.rowconfigure(0, weight=1)


        # Individual elements

        # Display results and status
        self.result_tree = result_window(self.f2, viewer, stat)
        # Controls
        el = Elements(self.f1)
        el.button("Database", self.selectPath, '', 0, 0, tk.W + tk.E, 1)        # Selection of root directory
        el.button("Process", self.processThreader, '', 0, 1, tk.W + tk.E, 1)    # Process all data
        self.dataset = el.textField("Task/Dataset", 20, 1, 0)                   # Task or Dataset to be searched for
        self.filters = el.textField("Filters", 20, 1, 1)                        # keywords to filter individual datasets
        el.button("Search", self.search, '', 3, 0, tk.N + tk.S, 1)              # button press to start search
        el.button("Clear", self.result_tree.clear, '', 3, 1, tk.N, 1)           # button press to clear selection
        el.check('Overwrite', self.overwrite, 4, 1)                             # checkbox for overwite option

        self.file_path=''

    # method for calling directory picker
    def selectPath(self):
        self.file_path = appFuncs.selectPath(self.file_path)
        self.stat.set('Database Selected: %s', self.file_path)
        self.result_tree.file_path = self.file_path

    # executed on clicking search button
    def search(self):
        self.viewer.clearFrame(self.viewer.fr)
        dataset = self.dataset.get()
        identifier=f'*{dataset}*.feat'
        if dataset=='':identifier=f'*.feat'
        # Search for all files that match task
        search_list = Path(self.file_path).rglob(identifier)
        search_list = self.verify_dataset(search_list)
        filtered_list = self.apply_filters(search_list)
        self.result_tree.fileList = self.aggregated_list(filtered_list)
        # Refresh results display
        self.result_tree.display()  # display the results

    # Checks if the selected dataset is a preprocessed dataset for one individual.
    # Filters out based on presence of a report_prestat.html file
    @staticmethod
    def verify_dataset(file_list):
        fl = [dataset for dataset in file_list if (Path(dataset/'report_prestats.html').exists()) and not(Path(dataset/'cluster_zstat1.html').exists())]
        return fl

    def apply_filters(self,file_list):
        # List of datasets as string for display purposes
        filters = self.filters.get()
        if len(filters) != 0:
            filters = filters.split(";")
            fl = [row for row in file_list if any(f in str(row) for f in filters)]

        else:
            fl = file_list
        return fl

    def aggregated_list(self, filtered_list):
        prefix = self.config.prefeat_identifier
        suffix = self.config.output_identifier
        fl = []
        iid = 0
        for inpath in filtered_list:
            pop=0
            # is the resulting file a post-processed file from ICA-AROMA processed data
            pop_i = appFuncs.postProcessed_identifier(inpath)
            if pop_i == 0:
                # generate output path of file
                outpath = appFuncs.generateOutpath(inpath, prefix, suffix)
                pvp = appFuncs.prevProcessed(outpath)
                if pvp == 1:    pop = appFuncs.postProcessed(outpath)
                head_motion_stats = appFuncs.headMotion_stats(inpath)
                fl.append([inpath, outpath, head_motion_stats, pvp, pop, iid])
                iid += 1
        return fl

    # Routed here from processThreader when Process button is pressed
    def process(self):
        self.stat.set('Processing...')
        queue = self.result_tree.queue()
        t1=time.perf_counter()
        process_queue = executor(queue, self.config.icaPath, self.overwrite.get(), self.result_tree.processing_status, self.config.user_options, self.result_tree.fileList)
        process_queue.threader()        # put the queue on multi-threaded processing
        t2 = time.perf_counter()
        self.stat.set(f'Processing Completed in {round((t2-t1)/60)} minutes')

    def processThreader(self):
        self.update_idletasks()
        x = threading.Thread(target=self.process)
        x.daemon = True
        x.start()


#   class for tkinter Treeview and related functions
class result_window:

    def __init__(self, parent,viewer,stat):
        # Draw a treeview of a fixed type
        self.viewer=viewer
        self.stat=stat
        self.parent=parent
        self.fileList=[]
        self.tree = ttk.Treeview(self.parent, show='headings', columns=['Number', 'Name', 'Motion','Status'])
        self.tree.grid(sticky='NSEW')
        self.tree.heading("Number", text="#")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Motion", text="Motion Stats")
        self.tree.heading("Status", text="Status")

        self.tree.column("Number", width=30, stretch=tk.NO, anchor='e')
        self.tree.column("Name", width=400)
        self.tree.column("Motion", width=150, stretch=tk.NO, anchor='center')
        self.tree.column("Status", width=100, stretch=tk.NO, anchor='center')

        self.tree.bind('<Button-1>',self.left_click)
        self.tree.bind('d', self.delete_entry)
        self.tree.bind(('<Button-3>' ), self.double_left_click)
        self.tree.bind(('<Button-2>'), self.double_left_click)
        self.tree.bind(('w'), self.double_left_click)
        self.last_focus=None


    def display(self):
        self.delete()
        index = iid = 0
        self.abs=[]
        self.rel=[]
        for row in self.fileList:
            inPath = row[0]
            motion = row[2]
            pvp = row[3]
            pop = row[4]

            p1 = inPath.relative_to(self.file_path)
            disp = '  >>  '.join(p1.parts)
            self.tree.insert("", index, iid, values=(iid + 1, disp))
            self.motion_stats(iid, motion)

            if pvp == 0:
                self.processing_status(iid, 'Not Processed')
            elif pop==0:
                self.processing_status(iid, 'Processed')
            else:
                self.processing_status(iid, 'Post-Processed')
            index = iid = index + 1

            self.abs.append(float(motion[0]))
            self.rel.append(float(motion[1]))

        if len(self.abs)>1:
            self.absolute = [statistics.mean(self.abs), statistics.stdev(self.abs)]
            self.relative = [statistics.mean(self.rel), statistics.stdev(self.rel)]
        else:
            try:
                self.absolute = [statistics.mean(self.abs), 0]
                self.relative = [statistics.mean(self.rel), 0]
            except:
                self.absolute = [0, 0]
                self.relative = [0, 0]
        self.set_motion_stat()

    # generate queue for processing
    def queue(self):
        fl = self.fileList
        # id = list(range(0, len(fl)))
        index = self.tree.selection()
        # if any items are selected, modify the file list to be processed
        if len(index) != 0:
            N = [int(i) for i in index]
            fl = [fl[j] for j in N]
            # id = N
        return fl
    # clears selection of all items in treeview
    def clear(self):
        for item in self.tree.selection(): self.tree.selection_remove(item)
        self.viewer.clearFrame()

    def delete(self):
        self.tree.delete(*self.tree.get_children())

    # display status of a treeview item
    def processing_status(self, iid, stsMsg):
        self.tree.set(iid, 'Status', stsMsg)
        self.parent.update_idletasks()

    def set_motion_stat(self):
        self.stat.set('Matches Found: %d   |    Absolute Motion = %.2f +/- %.2f mm   |    Relative Motion = %.2f  +/- %.2f mm',
                      len(self.fileList), self.absolute[0], self.absolute[1], self.relative[0],
                      self.relative[1])

    def motion_stats(self, iid, motion):
        MotionStats = 'Abs:' + str(motion[0]) + ' Rel: ' + str(motion[1])
        self.tree.set(iid, 'Motion', MotionStats)

    def left_click(self, event):
        iid = self.tree.identify_row(event.y)
        self.clickID =iid
        if not iid == '':
            iid=int(iid)
            path = self.fileList[iid][0] / 'mc'
            name = ['trans.png', 'rot.png', 'disp.png']
            im_list=[]
            for i in name:
                im_list.append(path/i)
            self.viewer.display(im_list,mode=1)

    def double_left_click(self, event):
        iid = self.clickID
        if iid != '':
            self.clickID = ''
            iid = int(iid)
            outpath = self.fileList[iid][1]
            path = appFuncs.generateProcessedOutpath(outpath)
            pvp = self.fileList[iid][3]
            pop=self.fileList[iid][4]
            if pvp == 1:
                motion_IC_file = outpath / 'classified_motion_ICs.txt'
                h = open(motion_IC_file,'r')
                content =h.readlines()
                for line in content:
                    motion_IC = line.split(',')
                    motion_IC = list(map(int,motion_IC))
                im_list= []
                for IC in motion_IC:
                    im_list.append(outpath/'melodic.ica'/'report'/f'IC_{IC}_thresh.png')
                    mode = 2

            if pop == 1 and pvp == 1:
                im_list_post = [path / 'rendered_thresh_zstat1.png', path / 'tsplot' / 'tsplot_zstat1.png']
                im_list += im_list_post
                mode = 3
            if pvp == 1:
                self.viewer.display(im_list, mode)


    def delete_entry(self, event):
        iid = self.clickID
        if not iid=='':
            iid=int(iid)
            del self.fileList[iid]
            self.delete()
            self.display()
            self.clickID = ''

#   helper class for common use functions
class appFuncs:

    # Generates file dialog box
    @staticmethod
    def selectPath(file_path):
        f = tk.filedialog.askdirectory()
        if f!='':
            file_path=f
        return file_path

    # generates output folder path
    @staticmethod
    def generateOutpath(inPath, prefix, suffix):
        z=inPath.stem.replace(prefix,'');  z=z+suffix
        outPath = (Path(inPath).parent) / z
        return outPath

    @staticmethod
    def generateProcessedOutpath(path):
        fo=Path(path).glob('*.feat')
        processedOutpath=''
        for i in fo:
           processedOutpath=i
        return processedOutpath

    # Identify previously processed datasets
    @staticmethod
    def prevProcessed(outPath):
        pvp = 0
        if Path(outPath).is_dir(): pvp = 1
        return pvp

    @staticmethod
    def postProcessed(path):
        # idenitfy if the dataset has been processed through ICA and post-processed as well
        pop = 0
        # is feat file present?
        # print(path)
        fo=Path(path).glob('*.feat')
        for i in fo:
            if i.is_dir() == True:
                pop = 1
        return pop

    @staticmethod
    def postProcessed_identifier(path):
        # if melodic.ica is a sibling directory, then this is assumed to be post-processed dataset generated from
        # ICA-AROMA processed data
        pop_i = 0
        fo = Path(path).parent/'melodic.ica'
        if fo.is_dir() == True: pop_i = 1
        return pop_i

    @staticmethod
    def headMotion_stats(path):
        motion = [0, 0]
        if path.is_dir():
            a=path/"report_prestats.html"
            f = open(str(a), encoding="utf8")
            soup = BeautifulSoup(f,'lxml')
            f.close
            try:
                W=soup.find_all('p')[-4]
                E=''.join(W.find('br').next_siblings)
                S=E.split('mm')
                motion=[S[0].split('=')[1],S[1].split('=')[1]]
            except:
                motion=[0,0]
        return motion

#  class for parallelization and execution
class executor:
    def __init__(self, list, icaPath, overwrite, status, user_options, result_tree):
        self.fl = list
        self.icaPath = icaPath
        self.ov = overwrite
        self.status = status
        self.result_tree = result_tree
        # self.aux_args=[]
        self.aux_args=['-dim',user_options[1],'-den',user_options[2]]
        if user_options[0]!='': self.aux_args.extend(['-tr',user_options[0]])
        if self.ov == 1: self.aux_args.append("-overwrite")

    def call_ICA(self, que):
        args = que[0]
        id = que[1]
        # print(args)
        self.status(id, 'Processing...')
        subprocess.run(args)
        self.status(id, 'Processed')
        self.result_tree[id][3] = 1

    def threader(self):
        que=self.queue_prep()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self.call_ICA, que)

    def queue_prep(self):
        que=[]
        for row in self.fl:
            args = ["python2.7", str(self.icaPath), "-feat", str(row[0]), "-out", str(row[1])] + self.aux_args
            que.append([args, row[-1]])
        return que


#-----------------------------------------------------------------------------------------------------------------------

class StatusBar(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.label = tk.Label(self, bd=1, relief='sunken', anchor='w')
        self.label.pack(fill=tk.X)

    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()

#-----------------------------------------------------------------------------------------------------------------------

class MainApp(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        parent.title(name)
        parent.minsize(800,500)
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        # draw a viewer window
        viewer_root=tk.Toplevel()
        self.config=config()
        # Components
        self.viewer = Viewer(viewer_root)
        self.menubar = Menubar(parent,self.config)
        self.statusbar = StatusBar(parent)
        self.mainarea = MainArea(parent, self.statusbar, self.viewer, self.config, borderwidth=1, relief=tk.RAISED)

        # configurations
        self.mainarea.grid(column=0, row=0, sticky='WENS')
        self.statusbar.grid(column=0, row=1, sticky='WE')
        self.statusbar.set('Ready')

#-----------------------------------------------------------------------------------------------------------------------
root = tk.Tk()
PR = MainApp(root)
root.mainloop()
