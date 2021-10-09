from tkinter import *
from tkinter import ttk

from tagger import cmd

def make_gui():

    # TODO
    # - optional inputs/ default values / hint
    # - larger main frame
    # - Advanced options toggle
    # - radio switch for action / tabs?
    # - text input defaults, (can these be saved on the system somewhere?)
    # - display errors; log messaging; loading messages;
    # - return values?
    # - misc gui function cleanup
    # - file selection?
    # - styling

    def create_backup__click():
        # TODO figure out how this wonky namespacing shit works
        result = cmd.create_backup(lib_type, libpath, output_dir, output_filename)
        ...

    def generate_tags__click():
        result = cmd.generate_metadata_tags_from_library(lib_type, libpath, output_dir, output_filename)
        ...

    def apply__click():
        result = cmd.restore_metadata_tags_from_backup(json_filename)
        ...

    # TODO
    # - file path finder
    # - validation


    root = Tk()
    root.title("Audio File Tagger")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

    typeframe = ttk.Frame(mainframe)
    typeframe.grid()
    ttk.Label(typeframe, text="Library Type:").grid()

    lib_type = StringVar()
    ttk.Radiobutton(typeframe, text='Mixxx', variable=lib_type, value='mixxx').grid()
    ttk.Radiobutton(typeframe, text='Serato', variable=lib_type, value='serato').grid()

    ttk.Label(mainframe, text="Library Path:").grid()
    libpath = StringVar()
    libpath_entry = ttk.Entry(mainframe, textvariable=libpath)
    libpath_entry.grid()

    ttk.Label(mainframe, text="Output Directory:").grid()
    output_dir = StringVar()
    output_dir_entry = ttk.Entry(mainframe, textvariable=output_dir)
    output_dir_entry.grid()

    ttk.Label(mainframe, text="Output Filename:").grid()
    output_filename = StringVar()
    output_filename_entry = ttk.Entry(mainframe, textvariable=output_filename)
    output_filename_entry.grid()

    create_backup_button = ttk.Button(mainframe, text="Create Backup", command=create_backup__click)
    create_backup_button.grid()
    generate_tags_button = ttk.Button(mainframe, text="Generate Tags", command=generate_tags__click)
    generate_tags_button.grid()

    # TODO horizontal rule?


    ttk.Label(mainframe, text="Json file:").grid()
    json_filename = StringVar()
    json_filename_entry = ttk.Entry(mainframe, textvariable=json_filename)
    json_filename_entry.grid()

    apply_button = ttk.Button(mainframe, text="Apply Tags", command=apply__click)
    apply_button.grid()

    # output_filename = StringVar()
    # output_filename_entry = ttk.Entry(mainframe, width=7, textvariable=output_filename)
    # # output_filename_entry.grid(column=2, sticky=(W, E))

    # ttk.Button(mainframe, text="Create Backup", command=launch_missiles)

    # feet = StringVar()
    # feet_entry = ttk.Entry(mainframe, width=7, textvariable=feet)
    # feet_entry.grid(column=2, row=1, sticky=(W, E))

    # meters = StringVar()
    # ttk.Label(mainframe, textvariable=meters).grid(column=2, row=2, sticky=(W, E))
    # ttk.Button(mainframe, text="Calculate", command=calculate).grid(column=3, row=3, sticky=W)

    # ttk.Label(mainframe, text="feet").grid(column=3, row=1, sticky=W)
    # ttk.Label(mainframe, text="is equivalent to").grid(column=1, row=2, sticky=E)
    # ttk.Label(mainframe, text="meters").grid(column=3, row=2, sticky=W)

    # for child in mainframe.winfo_children():
    #     child.grid_configure(padx=5, pady=5)

    # feet_entry.focus()
    # root.bind("<Return>", calculate)

    root.mainloop()


make_gui()



# def calculate(*args):
#     try:
#         value = float(feet.get())
#         meters.set(int(0.3048 * value * 10000.0 + 0.5)/10000.0)
#     except ValueError:
#         pass

# root = Tk()
# root.title("Feet to Meters")

# mainframe = ttk.Frame(root, padding="3 3 12 12")
# mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
# root.columnconfigure(0, weight=1)
# root.rowconfigure(0, weight=1)

# feet = StringVar()
# feet_entry = ttk.Entry(mainframe, width=7, textvariable=feet)
# feet_entry.grid(column=2, row=1, sticky=(W, E))

# meters = StringVar()
# ttk.Label(mainframe, textvariable=meters).grid(column=2, row=2, sticky=(W, E))

# ttk.Button(mainframe, text="Calculate", command=calculate).grid(column=3, row=3, sticky=W)

# ttk.Label(mainframe, text="feet").grid(column=3, row=1, sticky=W)
# ttk.Label(mainframe, text="is equivalent to").grid(column=1, row=2, sticky=E)
# ttk.Label(mainframe, text="meters").grid(column=3, row=2, sticky=W)

# for child in mainframe.winfo_children():
#     child.grid_configure(padx=5, pady=5)

# feet_entry.focus()
# root.bind("<Return>", calculate)

# root.mainloop()
