import sublime_plugin
import sublime
import os


class OpenFilesListerCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window = sublime.active_window()

        self.sheets = []
        self.filePaths = []
        self.fileNames = []
        self.viewIds = []

        self.untitled = self.get_setting('show_untitled_files')

        count = 0
        active_group = self.window.active_group()
        sheets = self.window.sheets_in_group(active_group)
        for sheet in sheets:
            if sheet and sheet.view():
                name = sheet.view().file_name()
                if name != None:
                    self.sheets.append(sheet.view())
                    name = os.path.abspath(sheet.view().file_name())
                    self.fileNames.append(name.rsplit(os.sep, -1)[-1])
                    self.filePaths.append(name)
                    self.viewIds.append(sheet.view().id())
                elif name == None and self.untitled:
                    temp = sheet.view().name()
                    self.sheets.append(sheet.view())
                    self.fileNames.append('Untitled-{}* {}'.format(count, temp))
                    self.filePaths.append('Untitled-{}{}'.format(count, temp))
                    self.viewIds.append(sheet.view().id())
                    count = count + 1

        id = self.window.active_sheet().view().id()

        if id not in self.viewIds:
            self.window.run_command('next_view_in_stack')
            id = self.window.active_sheet().view().id()

        self.current = self.viewIds.index(id)
        self.window.run_command('hide_overlay')

        self.show_panel()

    def show_panel(self):
        self.window.show_quick_panel(
            self.fileNames,
            self.on_done,
            flags=sublime.WANT_EVENT | sublime.KEEP_OPEN_ON_FOCUS_LOST,
            selected_index=self.current,
            on_highlight=self.on_highlighted,
        )

    def set_timeout(self):
        sublime.set_timeout_async(lambda: self.close_panel(), 1500)

    def close_panel(self):
        self.window.run_command('hide_overlay')

    def on_done(self, index, event):
        if index == -1:
            index = self.current
        if event.get('modifier_keys', None).get('primary', False):
            self.window.open_file(
                fname=self.sheets[self.current].file_name(), flags=sublime.REPLACE_MRU
            )
            self.window.open_file(
                fname=self.sheets[index].file_name(),
                flags=sublime.ADD_TO_SELECTION | sublime.CLEAR_TO_RIGHT,
            )
        else:
            self.window.open_file(fname=self.sheets[index].file_name())

    def on_highlighted(self, index):
        self.window.open_file(
            fname=self.sheets[index].file_name(),
            flags=sublime.SEMI_TRANSIENT | sublime.REPLACE_MRU,
        )

    def get_settings(self):
        return sublime.load_settings('OpenFilesLister.sublime-settings')

    def get_setting(self, setting):
        return self.get_settings().get(setting)
