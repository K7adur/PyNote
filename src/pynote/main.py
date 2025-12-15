# src/pynote/main.py
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from themes import get_theme, apply_theme

APP_TITLE = "PyNote"

class PyNoteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry('800x600')
        self.current_theme = 'dark'   # default theme
        self.theme = get_theme(self.current_theme)
        self._filepath = None
        self._create_widgets()
        self._create_menu()
        self._bind_shortcuts()

    def _create_widgets(self):
        # Text widget with scrollbar

        self.text = tk.Text(self, wrap='word', undo=True)
        apply_theme(self.text, self.theme)
        self.vsb = ttk.Scrollbar(self, orient='vertical', command=self.text.yview)
        self.text.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side='right', fill='y')
        self.text.pack(side='left', fill='both', expand=True)

        # status bar
        self.status = tk.StringVar(value='Ln 1, Col 0')

        # CREATE the status bar first
        self.status_bar = tk.Label(self,textvariable=self.status,anchor='w',
        bg=self.theme['status_bg'],fg=self.theme['status_fg'],padx=8)

        # THEN apply optional polish
        self.status_bar.configure(relief='sunken',bd=1,font=('Segoe UI', 9))

        # THEN pack it
        self.status_bar.pack(side='bottom', fill='x')

        # update cursor position
        self.text.bind('<KeyRelease>', self._update_status)
        self.text.bind('<ButtonRelease>', self._update_status)


    def toggle_theme(self):
        # switch theme name
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.theme = get_theme(self.current_theme)

        # apply to text editor
        apply_theme(self.text, self.theme)

        # apply to status bar
        self.status_bar.configure(bg=self.theme['status_bg'],fg=self.theme['status_fg'])


    def _create_menu(self):
        menu = tk.Menu(self)
        filemenu = tk.Menu(menu, tearoff=0)
        filemenu.add_command(label='New', command=self.new_file)
        filemenu.add_command(label='Open', command=self.open_file)
        filemenu.add_command(label='Save', command=self.save_file)
        filemenu.add_command(label='Save As', command=self.save_as)
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=self.quit)
        menu.add_cascade(label='File', menu=filemenu)
        self.config(menu=menu)

    def _bind_shortcuts(self):
        self.bind('<Control-s>', lambda e: self.save_file())
        self.bind('<Control-o>', lambda e: self.open_file())
        self.bind('<Control-n>', lambda e: self.new_file())
        self.bind('<Control-z>', lambda e: self.text.event_generate('<<Undo>>'))
        self.bind('<Control-y>', lambda e: self.text.event_generate('<<Redo>>'))
        self.bind('<Control-t>', lambda e: self.toggle_theme())


    def new_file(self):
        if self._confirm_discard():
            self.text.delete('1.0', tk.END)
            self._filepath = None
            self.title(APP_TITLE)

    def open_file(self):
        if not self._confirm_discard():
            return
        path = filedialog.askopenfilename(
            filetypes=[('Text Files', '*.txt;*.md;*.py'), ('All Files', '*.*')]
        )
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = f.read()
                self.text.delete('1.0', tk.END)
                self.text.insert('1.0', data)
                self._filepath = path
                self.title(f"{APP_TITLE} - {path}")
            except Exception as e:
                messagebox.showerror('Error', f'Failed to open file: {str(e)}')

    def save_file(self):
        if self._filepath:
            try:
                with open(self._filepath, 'w', encoding='utf-8') as f:
                    f.write(self.text.get('1.0', tk.END))
                self.text.edit_modified(False)
                messagebox.showinfo('Saved', 'File saved successfully')
            except Exception as e:
                messagebox.showerror('Error', f'Failed to save file: {str(e)}')
        else:
            self.save_as()

    def save_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension='.txt',
            filetypes=[('Text Files', '*.txt;*.md;*.py'), ('All Files', '*.*')]
        )
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.text.get('1.0', tk.END))
                self._filepath = path
                self.title(f"{APP_TITLE} - {path}")
                self.text.edit_modified(False)
                messagebox.showinfo('Saved', 'File saved successfully')
            except Exception as e:
                messagebox.showerror('Error', f'Failed to save file: {str(e)}')

    def _update_status(self, event=None):
        # cursor position
        line, col = self.text.index(tk.INSERT).split('.')

        # full text content
        content = self.text.get('1.0', 'end-1c')

        # character count (excluding trailing newline)
        char_count = len(content)

        # word count (split by whitespace)
        word_count = len(content.split()) if content.strip() else 0

        # update status bar
        self.status.set(f'Ln {line}, Col {col} | Words: {word_count} | Chars: {char_count}')


    def _confirm_discard(self):
        if self.text.edit_modified():
            resp = messagebox.askyesnocancel(
                'Unsaved changes',
                'You have unsaved changes. Save before continuing?'
            )
            if resp is None:
                return False
            if resp:
                self.save_file()
        return True


if __name__ == '__main__':
    app = PyNoteApp()
    app.mainloop()

