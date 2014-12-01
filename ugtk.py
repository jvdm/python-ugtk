# python-ugtk - a functional layer upon PyGObject
# Copyright (C) 2014, J. Victor Martins <jvdm@sdf.org.>
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Contributor(s):	J. Victor Martins <jvdm@sdf.org>
#


"""ugtk provides a functional layer upon PyGObject/GTK+."""


import sys
import re
import inspect
import functools
from gi.repository import GObject, Gtk


_handlers_table = {}

#
# Dispatching
#

def _dispatch(method, actions, *, klass=None, widget=None):
    """Dispatch actions over to GTK class/widget.

    Each action is to be applied in the class or a parent class in
    MRO, as long as if there is an action handler available for that
    class.

    """

    if bool(klass) == bool(widget):
        raise ValueError("You can't specify both klass and widget")

    if widget:
        klass = type(widget)

    handlers = []
    for subclass in klass.__mro__:
        try:
            handlers.append(_handlers_table[subclass](method, actions))
        except KeyError:
            # don't apply actions to a class that doesn't have an
            # handler, but ignore in the case of subclasses
            if subclass == klass:
                raise ValueError("missing handler for class: %s"
                                 % klass.__name__)

    for handler in handlers:
        widget = handler(widget)

    if actions:
        # Some actions were not used, currently this is an error:
        raise ValueError("unknown action(s) for method '%s' on %s: %s."
                         % (method, klass.__name__, ', '.join(actions)))

    return widget


def new(klass, **actions):
    return _dispatch('new', actions, klass=klass)

def set(widget, **actions):
    return _dispatch('set', actions, widget=widget)

def add(widget, **actions):
    return _dispatch('add', actions, widget=widget)

#
# Base Handler class and decorator
#

def handler(gtk_cls):
    """Class decorator for ugtk handler classes."""
    def decorator(cls):
        cls._klass = gtk_cls
        if hasattr(cls, 'setters'):
            for action, function in list(cls.setters.items()):
                if not function:
                    function = 'set_%s' % action
                if not hasattr(gtk_cls, function):
                    raise ValueError(
                        'handler: %s missing set action function: %s'
                        % (gtk_cls.__name__, function))
                cls._setters[action] = function
        _handlers_table[gtk_cls] = cls
        return cls
    return decorator


class Handler:

    _methods = ('set', 'new')
    _klass = None
    _setters = {}

    def __init__(self, method, actions):
        if method not in self._methods:
            raise ValueError('unknown method: %s' % method)
        self.method = method
        self.actions = actions

    def __call__(self, widget):
        if self.is_new and widget is None:
            widget = self.on_create(self._klass)
        callbacks = {}
        for action, args in self.actions.items():
            try:
                func_name = self._setters[action]
            except KeyError:
                try:
                    callbacks[action] = (
                        getattr(self, 'on_action__%s' % action), [args])
                except AttributeError:
                    pass
            else:
                callbacks[action] = (
                    self.__on_action_set, [func_name, args])
        self.on_pre(widget)
        for action, (func, args) in callbacks.items():
            keep = func(widget, *args)
            if not keep:
                del self.actions[action]
        self.on_post(widget)
        return widget

    @property
    def is_set(self):
        return self.method == 'set'

    @property
    def is_new(self):
        return self.method == 'new'

    def __on_action_set(self, widget, func_name, args):
        getattr(widget, func_name)(args)
        return False

    def on_create(self, klass):
        return klass()

    def on_pre(self, widget):
        pass

    def on_post(self, widget):
        pass

#
# Default Handlers
#

@handler(GObject.Object)
class GObjectHandler(Handler):
    def on_action__connect(self, widget, signals):
        if type(signals) != dict:
            raise ValueError("'connect' action arg must be a dict")
        for signal in list(signals.keys()):
            widget.connect(signal, signals.pop(signal))


@handler(Gtk.StatusIcon)
class StatusIcondHandler(Handler):
    pass


@handler(Gtk.Widget)
class WidgetHandler(Handler):
    def on_pre(self, widget):
        if self.is_new:
            widget.show()

        if 'hide' in self.actions and 'show' in self.actions:
            raise ValueError("can't have both 'hide' and 'show' actions")

    def on_action__hide(self, widget, value):
        if value:
            widget.hide()
        else:
            widget.show()

    def on_action__show(self, widget, value):
        if value:
            widget.show()
        else:
            widget.hide()


@handler(Gtk.Container)
class ContainerHandler(Handler):

    setters = { 'border_width': None,
                'child': 'add' }


@handler(Gtk.TreeView)
class TreeView(Handler):

    setters = { 'model': None,
                'headers_visible': None,
                'headers_clickable': None }

    def on_action__selection_mode(self, tview, arg):
        tview.get_selection().set_mode(arg)

    def on_action__selection_connect(self, tview, arg):
        if type(arg) is not dict:
            raise ValueError("'connect' action arg must be a dict")
        for a in arg:
            tview.get_selection().connect(a, arg[a])

    def on_action__columns(self, tview, arg):
        if method == 'set':
            # remove all current columns in tview...
            for col in tview.get_columns():
                tview.remove_column(col)

        for col in arg:
            tview.append_column(col)

    def on_action__text_column(self, tview, arg):
        col = Gtk.TreeViewColumn(arg['title'],
                                 Gtk.CellRendererText(),
                                 text=arg['text'])
        if 'position' in arg:
            tview.insert_column(col, arg['position'])
        else:
            tview.append_column(col)


@handler(Gtk.Window)
class WindowHandler(Handler):

    setters = { 'title': None,
                 'border': 'set_border_width' }

    def on_create(self, klass):
        return klass(self.actions.pop('type', 'toplevel'))

    def on_pre(self, widget):
        if self.is_new:
            widget.set_default_size(
                self.actions.pop('default_width', -1),
                self.actions.pop('default_height', -1))

    def on_action__resize(self, widget, value):
        if type(value) != tuple:
            ValueError("'resize' action argument must be a tuple (width, height)")
        if self.is_set:
            widget.resize(*value)


@handler(Gtk.Label)
class LabelHandler(Handler):

    setters = {'text': None, 'selectable': None}


@handler(Gtk.Entry)
class EntryHandler(Handler):

    set_actions = {'max': 'set_max_length',
                   'text': ''}

    def on_create(self, klass):
        return klass(self.actions.pop('max', 0))


@handler(Gtk.Box)
class Box(Handler):

    setters = {'homogeneous': None, 'spacing': None}

    def on_pre(self, widget):
        self.pack_args = {'expand': True, 'fill': True, 'padding': 0, 'order': 'start'}
        for arg, default in list(self.pack_args.items()):
            try:
                self.pack_args[arg] = self.actions.pop(arg)
            except KeyError:
                pass

    def on_action__children(self, widget, arg):
        """Callback for children action.

        'children' argument is a list of gtk.Widget or dicts.
        """

        if self.is_set:
            # remove all children from this box...
            for chd in box.get_children():
                box.remove(chd)

        for child in arg:
            pack_args = {}
            if type(child) is tuple:
                (child, pack_args) = child
                for k,v in self.pack_args.items():
                    if k not in pack_args:
                        pack_args[k] = v
            else:
                pack_args.update(self.pack_args)
            if not isinstance(child, Gtk.Widget):
                raise ValueError("`child' action is not a Gtk.Widget")
            func = getattr(widget, 'pack_%s' % pack_args['order'])
            func(child, *[ pack_args[p] for p in ('expand', 'fill', 'padding') ])
            child.show()


@handler(Gtk.VBox)
class VBox(Handler):
    pass


@handler(Gtk.HBox)
class HBox(Handler):
    pass


@handler(Gtk.Button)
class Button(Handler):

    setters = { 'label': None }

    def on_create(self, klass):
        return klass(self.actions.pop('label', None))
