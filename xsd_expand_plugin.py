from gi.repository import GObject, Gedit, Gtk

ui_str = """<ui>
<menubar name="MenuBar">
<menu name="EditMenu" action="Edit">
<placeholder name="EditOps_2">
<menuitem name="Go to defitintion" action="Go_to_definition"/>
</placeholder>
</menu>
</menubar>
</ui>
"""

class ExamplePyPlugin(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "ExamplePyPlugin"

    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        self._insert_menu()

    def do_deactivate(self):
        self._remove_menu()
        self._action_group = None
    
    def _insert_menu(self):
        manager = self.window.get_ui_manager()
        self._action_group = Gtk.ActionGroup("DuplicateLinePluginActions")
        self._action_group.add_actions([(
            "Go_to_definition",
            None,
            _("Go to definition"),
            "<control>e",
            _("Duplicate current line, current selection or selected lines"),
            self.hello
        )])
        
        manager.insert_action_group(self._action_group, -1)
        
        self._ui_id = manager.add_ui_from_string(ui_str)

    def hello(self, action):
        print("""
        ide jest taka ze wciskam klawisz i jak plik jest .xsd to sie
        otwiera jako nowy .xsd iw nim zapisuje to co daje py/geditxmlgo.py
        - uwaga musi te wyszukiwac includy!!!
        i musi zapisywac z includami by byly dostepne
        i wtedy mozna znow i znow sie otworzy
        ostroznie na includy""")
        doc = self.window.get_active_document()
        if doc:
            insert_mark = doc.get_insert()
            start = doc.get_iter_at_mark(insert_mark)
            end = doc.get_iter_at_mark(insert_mark)
            if not end.ends_word():
                end.forward_word_end()
            if not start.starts_word():
                start.backward_word_start()
                
            print(start.get_text(end))

    def _remove_menu(self):
        manager = self.window.get_ui_manager()
        manager.remove_ui(self._ui_id)
        manager.remove_action_group(self._action_group)
        manager.ensure_update()

    def do_update_state(self):
        pass
