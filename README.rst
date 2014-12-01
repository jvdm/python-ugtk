 Introduction
==============

``python-ugtk`` is a functional layer upon `PyGobject
<https://wiki.gnome.org/action/show/Projects/PyGObject>`_.  The
purpose of this is to provide a different perspective to GUI
programming towards more maintanable, clean and organized code.

The ugtk layer is based on the concept of actions.  An ugtk action is
a series of directives that can be performed over gtk widgets, usually
by calling their methods, setting their properties or hooking
callbacks to their signals and so on.  Each widget class determines a
set of actions that it support, so the set of availables actions for
each widget is based on its inheritance.

To apply actions you must use a ugtk method, by specifying a kwargs
for each action (where the key is the action name, the value the
action argument).  There are currently two of them::

    ugtk.new(gtkclass, **actions)

    ugtk.set(gtkwidget, **actions)

    ugtk.add(gtkwidget, **actions)

The first is used when you have no widget yet and you want it created.
The second serves only the purpose of applying actions.

Actions change their behaviour depending on the ugtk method used to
perform them.  For example, specifiying ``children=list`` action on a
``Gtk.HBox`` object using ugtk.add() is different from using ugtk.set()
(the later will reset the box childrens, while the former will always
append).

Some actions are available for both methods (e.g. ``text=str`` is
provided both for ugtk.new() and ugtk.add() with ``Gtk.Label`` --
which actually calls gtk.Label.set_text(str)).  Others are only
available for each method.  Some actions for both methods may behave
differently depending on which method they are being applied from.

To better organize actions we can group them by functionality:

set actions
  Actions that in will eventually call ``widget.set_ACTIONNAME`` or
  similar on methods passing their arguments.

wrapper actions
  Actions that generate a series of methods calls on the widget.
  E.g. ``gtkset(hbox, child_tight=[label, entry])`` will call
  ``gtk.Box.pack_start(0, label)`` and ``gtk.Box.pack_start(0,
  entry)``.

To provide a functional paradigm each ugtk method returns the widget
being manipulated, so users can do things like::

    win = ugtk.new(
        Gtk.Window,
        title="ugtk 'Hello, World' window",
        connect={'delete-event': Gtk.main_quit }
    )

    ugtk.set(
        win, 
        child=ugtk.new(
            Gtk.VBox,
            children=[
                ugtk.new(
                    Gtk.Label,
                    text="Hello, World!"
                ),
                (
                    ugtk.new(Gtk.Button,
                             label="Close",
                             connect={
                                 'clicked':
                                 lambda widget: win.close()
                             }),
                    { 'expand': False }
                ),
            ],
            expand=True
        )
    )

    Gtk.main()
    del win
