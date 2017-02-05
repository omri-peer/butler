import win32ui
import marshal
from Tkinter import *
import tkFileDialog

USER_FILE = 'info.pkl'
TEMP = 'temp.pkl'


class Service:
    def __init__(self, name='', description='', trigger=None, action=None):
        self.name = name
        self.description = description
        self.trigger = trigger
        self.action = action

    def is_installed(self, database):
        names = database.get_value('names')
        if self.name in names:
            return database.get_value('service: ' + self.name)[-1]
        return False

    def edit_parameters(self, database):
        top = Toplevel()
        trigger_editors = {}
        action_editors = {}

        def browse(dic, key):
            dic[key] = tkFileDialog.askopenfilename()

        i = 0

        if self.trigger[-1]:
            Label(top, text='Trigger:').grid(row=0, column=0, columnspan=2)

            i += 1
            for parameter in self.trigger[-1].keys():
                Label(top, text=parameter).grid(row=i, column=0)

                if self.trigger[-1][parameter] == 'text':
                    trigger_editors[parameter] = Entry(top)
                    trigger_editors[parameter].insert(END, self.trigger[2][parameter])
                elif self.trigger[-1][parameter] == 'file':
                    trigger_editors[parameter] = Button(top, text='Browse', command=lambda p=parameter: browse(self.trigger[2], p))

                trigger_editors[parameter].grid(row=i, column=1)
                i += 1

            i += 1

        if self.action[-1]:
            Label(top, text='Action:').grid(row=i, column=0, columnspan=2)

            i += 1
            for parameter in self.action[-1].keys():
                Label(top, text=parameter).grid(row=i, column=0)

                if self.action[-1][parameter] == 'text':
                    action_editors[parameter] = Entry(top)
                    action_editors[parameter].insert(END, self.action[2][parameter])
                elif self.action[-1][parameter] == 'file':
                    action_editors[parameter] = Button(top, text='Browse', command=lambda p=parameter: browse(self.trigger[2], p))

                action_editors[parameter].grid(row=i, column=1)
                i += 1

        def update(database):
            for parameter in trigger_editors:
                try:
                    self.trigger[2][parameter] = trigger_editors[parameter].get() if trigger_editors[parameter].get() else self.trigger[2][parameter]
                except:
                    pass
            for parameter in action_editors:
                try:
                    self.action[2][parameter] = action_editors[parameter].get() if action_editors[parameter].get() else self.action[2][parameter]
                except:
                    pass

            installed = self.is_installed(database)
            database.remove(self)
            database.insert(self)
            if not installed:
                database.uninstall(self)

            top.destroy()

        Button(top, text='Done', command=lambda: update(database)).grid(row=i, column=0, columnspan=2)


class Database:
    def __init__(self, source):
        self.source = source

    def get(self):
        f = open(self.source, 'rb')
        data = marshal.load(f)
        f.close()
        return data

    def get_value(self, key):
        data = self.get()
        if key in data.keys():
            return data[key]
        else:
            return None

    def set_value(self, key, value):
        data = self.get()
        data[key] = value
        f = open(self.source, 'wb')
        marshal.dump(data, f)
        f.close()

    def del_key(self, key):
        data = self.get()
        data.pop(key)
        f = open(self.source, 'wb')
        marshal.dump(data, f)
        f.close()

    def insert(self, service):
        names = self.get_value('names')
        if names:
            self.set_value('names', names + [service.name])
        else:
            self.set_value('names', [service.name])
        self.set_value('service: ' + service.name, (service.name, service.description, service.trigger, service.action, True))

    def remove(self, service):
        names = self.get_value('names')
        if service.name in names:
            names.remove(service.name)
            self.set_value('names', names)
            self.del_key('service: ' + service.name)

    def install(self, service):
        names = self.get_value('names')
        if service.name in names:
            self.set_value('service: ' + service.name, self.get_value('service: ' + service.name)[:-1] + (True,))
        else:
            self.insert(service)

    def uninstall(self, service):
        names = self.get_value('names')
        if service.name in names:
            self.set_value('service: ' + service.name, self.get_value('service: ' + service.name)[:-1] + (False,))


def draw_background(x1, y1, x2, y2, color):
    x = (x2-x1)/15
    y = (x2-x1)/15

    canvas.create_rectangle(x1, y1, x2, y2, fill=color)

    #SE
    canvas.create_rectangle(x2-x, y2-y, x2, y2, fill=canvas['background'], outline=canvas['background'])
    canvas.create_arc((x2-2*x, y2-2*y, x2, y2), start=270, extent=90, fill=color, outline=color)
    canvas.create_arc((x2-2*x, y2-2*y, x2, y2), start=270, extent=90, style=ARC)

    #SW
    canvas.create_rectangle(x1, y2-y, x1+x, y2, fill=canvas['background'], outline=canvas['background'])
    canvas.create_arc((x1, y2-2*y, x1+2*x, y2), start=180, extent=90, fill=color, outline=color)
    canvas.create_arc((x1, y2-2*y, x1+2*x, y2), start=180, extent=90, style=ARC)

    #NW
    canvas.create_rectangle(x1, y1, x1+x, y1+y, fill=canvas['background'], outline=canvas['background'])
    canvas.create_arc((x1, y1, x1+2*x, y1+2*y), start=90, extent=90, fill=color, outline=color)
    canvas.create_arc((x1, y1, x1+2*x, y1+2*y), start=90, extent=90, style=ARC)

    #NE
    canvas.create_rectangle(x2-x, y1, x2, y1+y, fill=canvas['background'], outline=canvas['background'])
    canvas.create_arc((x2-2*x, y1, x2, y1+2*y), start=0, extent=90, fill=color, outline=color)
    canvas.create_arc((x2-2*x, y1, x2, y1+2*y), start=0, extent=90, style=ARC)


def draw_service(canvas, database, temp, service, x1, y1, x2, y2):
    color = 'chartreuse2' if service.is_installed(database) else 'orange red'

    draw_background(x1, y1, x2, y2, color)

    content = Frame(canvas, height=14*(y2-y1)/16, width=7*(x2-x1)/9, bg=color)
    content.place(x=(8*x1+x2)/9, y=(15*y1+y2)/16)

    name = Label(content, text=service.name, bg=color, font=("Helvetica", 16), wraplength=(x2-x1-40))
    description = Label(content, text=service.description, bg=color, font=("Helvetica", 12), wraplength=(x2-x1-40), pady=10)
    settings_button = Button(content, text='Settings', command=lambda: service.edit_parameters(database), bg=color)
    switch_button = Button(content, text='Stop' if service.is_installed(database) else 'Start', command=lambda: switch(x1, y1, x2, y2, service, database, temp, [content, name, description, settings_button, switch_button], switch_button), bg=color)

    name.pack(side=TOP)
    description.pack(side=TOP)
    settings_button.pack(side=TOP)
    switch_button.pack(side=TOP)

    content.update()


def switch(x1, y1, x2, y2, service, database, temp, widgets, button):
    if service.is_installed(database):
        database.uninstall(service)
        temp.uninstall(service)
        draw_background(x1, y1, x2, y2, 'orange red')
        for widget in widgets:
            widget.config(bg='orange red')
        button.config(text='Start')
    else:
        database.install(service)
        temp.install(service)
        draw_background(x1, y1, x2, y2, 'chartreuse2')
        for widget in widgets:
            widget.config(bg='chartreuse2')
        button.config(text='Stop')


#
# triggers
#


def real_trigger():
    global const_trigger_parameters
    global temp_trigger_parameters
    try:
        f = open(const_trigger_parameters['file'], 'r+')
        f.close()
        temp_trigger_parameters['known'] = False
        return False
    except:
        answer = not temp_trigger_parameters['known']
        temp_trigger_parameters['known'] = True
        return answer


def started():
    global const_trigger_parameters
    global temp_trigger_parameters
    answer = not temp_trigger_parameters['passed']
    temp_trigger_parameters['passed'] = True
    return answer


#
# actions
#


def action():
    global const_action_parameters
    global temp_action_parameters
    import win32gui
    win32gui.MessageBox(None, const_action_parameters['greeting'], const_action_parameters['title'], 0)


root = Tk()

database = Database(USER_FILE)
temp = Database(TEMP)

canvas = Canvas(root, bg='cornflower blue')
canvas.pack()

services = []


WIDTH = 150
HEIGHT = 270

x = 30
y = 30
for name in database.get_value('names'):
    info = database.get_value('service: ' + name)
    services.append(Service(*info[:-1]))

    draw_service(canvas, database, temp, services[-1], x, y, x+WIDTH, y+HEIGHT)
    canvas.config(width=x+WIDTH+20, height=y+HEIGHT+20)
    x += 200


print database.get()

mainloop()

