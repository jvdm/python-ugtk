# -*- Mode: Python; coding: utf-8 -*-

##
## Copyright (C) 2013 J. Victor Martins <jvdm@sdf.org>
## All rights reserved
##
## This program is free software: you can redistribute it and/or modify it
## under the terms of the GNU General Public License as published by the Free
## Software Foundation, either version 3 of the License, or any later version.
##
## This program is distributed in the hope that it will be useful, but WITHOUT
## ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
## FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
## more details.
##
## You should have received a copy of the GNU General Public License along with
## this program.  If not, see <http://www.gnu.org/licenses/>.
##
##   Contributor(s):	J. Victor Duarte Martins <jvictor@mandriva.com>
##
"""
Default ugtk dispatchers.
"""

import gtk
import gobject
from ugtk.dispatchers.base import ActionDispatcher, dispatcher_for


@dispatcher_for(gobject.GObject)
class GObject(ActionDispatcher):

    def on_connect__callback(self, method, widget, signals):
        if type(signals) != dict:
            raise ValueError("'connect' action arg must be a dict")
        for signal in signals.keys():
            widget.connect(signal, signals.pop(signal))


@dispatcher_for(gtk.Widget)
class Widget(ActionDispatcher):

    def on_start_dispatch(self, method, widget, actions):
        if method == 'new':
            widget.show()

        if 'hide' in actions and 'show' in actions:
            raise ValueError("can't have both 'hide' and 'show' actions")


    def on_hide__callback(self, method, widget, value):
        if value:
            widget.hide()
        else:
            widget.show()


    def on_show__callback(self, method, widget, value):
        if value:
            widget.show()
        else:
            widget.hide()


@dispatcher_for(gtk.Container)
class Container(ActionDispatcher):

    set_actions = {'border_width': '', 'child': 'add'}


@dispatcher_for(gtk.Label)
class Label(ActionDispatcher):

    signals = ['copy_clipboard', 'move_cursor', 'populate_popup']
    set_actions = {'text': '', 'selectable': ''}

    def on_create(self, klass, actions):
        widget = gtk.Label()
        return widget


@dispatcher_for(gtk.TreeSortable)
class TreeSortable(ActionDispatcher):

    def on_sort_column_id__callback(self, method, tree, arg):
        tree.set_sort_column_id(*arg)


@dispatcher_for(gtk.TreeView)
class TreeView(ActionDispatcher):

    set_actions = {'model': '', 'headers_visible': '', 'headers_clickable': ''}

    def on_create(self, klass, actions):
        return gtk.TreeView()

    def on_selection_mode__callback(self, method, tview, arg):
        tview.get_selection().set_mode(arg)

    def on_selection_connect__callback(self, method, tview, arg):
        if arg.__class__ != dict:
            raise ValueError("'connect' action arg must be a dict")
        for a in arg:
            tview.get_selection().connect(a, arg[a])

    def on_columns__callback(self, method, tview, arg):
        if method == 'set':
            # remove all current columns in tview...
            for col in tview.get_columns():
                tview.remove_column(col)

        for col in arg:
            tview.append_column(col)

    def on_text_column__callback(self, method, tview, arg):
        col = gtk.TreeViewColumn(arg['title'],
                                 gtk.CellRendererText(),
                                 text=arg['text'])
        if 'position' in arg:
            tview.insert_column(col, arg['position'])
        else:
            tview.append_column(col)


@dispatcher_for(gtk.ScrolledWindow)
class ScrolledWindow(ActionDispatcher):

    set_actions = {'hadjusment': '', 'vadjusment': ''}

    def on_create(self, klass, actions):
        hadjusment = actions.pop('hadjusment', None)
        vadjusment = actions.pop('vadjusment', None)
        return gtk.ScrolledWindow(hadjusment, vadjusment)


@dispatcher_for(gtk.Box)
class Box(ActionDispatcher):

    set_actions = {'homogeneous': '', 'spacing': ''}

    def on_start_dispatch(self, method, widget, actions):
        self.specs = {}
        for pack_action in ('expand', 'fill', 'padding', 'order'):
            try:
                self.specs[pack_action] = actions.pop(pack_action)
            except KeyError:
                continue

    def on_children__callback(self, method, box, arg):
        """Callback for children action.

        'children' argument is a list of gtk.Widget or dicts.
        """

        if method == 'set':
            # remove all children from this box...
            for chd in box.get_children():
                box.remove(chd)

        for a in arg:
            if a.__class__ == tuple:
                (child, specs) = a
                self.specs.update(specs)
            elif issubclass(a.__class__, gtk.Widget):
                child = a
            else:
                msg = ("'children' action with argument which "
                       "isn't a gtk.Widget or a tuple.")
                raise ValueError(msg)
            method = 'pack_%s' % self.specs.pop('order', 'start')
            getattr(box, method)(child, **self.specs)
            child.show()


@dispatcher_for(gtk.VBox)
class VBox(ActionDispatcher):

    def on_create(self, klass, actions):
        return gtk.VBox()


@dispatcher_for(gtk.HBox)
class HBox(ActionDispatcher):

    def on_create(self, klass, actions):
        return gtk.HBox()


@dispatcher_for(gtk.Button)
class Button(ActionDispatcher):

    set_actions = {'label': ''}

    def on_create(self, klass, actions):
        label = actions.pop('label', None)
        return gtk.Button(label)


@dispatcher_for(gtk.Entry)
class Entry(ActionDispatcher):

    set_actions = {'max': 'set_max_length',
                   'text': ''}

    def on_create(self, klass, actions):
        max = actions.pop('max', 0)
        return gtk.Entry(max)


@dispatcher_for(gtk.Window)
class Window(ActionDispatcher):

    set_actions = {'title': '',
                   'border': 'set_border_width'}

    def on_create(self, klass, actions):
        return gtk.Window(actions.pop('type', 'toplevel'))


    def on_start_dispatch(self, method, window, actions):
        if method == 'new':
            window.set_default_size(actions.pop('default_width', -1),
                                    actions.pop('default_height', -1))


    def on_resize__callback(self, method, window, value):
        if type(value) != tuple:
            ValueError("'resize' action arg must be a tuple (width, height)")

        if method in ('set'):
            widget.resize(*value)
