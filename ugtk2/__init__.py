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


"""ugtk is a module providing a functional layer upon PyGObject/GTK+."""


import sys
import re
import inspect
import functools
from gi.repository import GObject, Gtk


_handlers_table = {}


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

    for subclass in klass.__mro__:
        try:
            handler = _handlers_table[subclass](method, actions, widget)
        except KeyError:
            # don't apply actions to a class that doesn't have an
            # agent, but ignore in the case of subclasses
            if subclass == klass:
                raise ValueError("missing handler for class: %s"
                                 % klass.__name__)
        else:
            widget = agent()

    if actions:
        # Some actions were not used, currently this is an error:
        raise ValueError("Unknow action(s) for '%s' on %s: %s."
                         % (method, klass.__name__, ', '.join(actions)))

    return widget


def new(klass, **actions):
    return _dispatch('new', actions, klass=klass)

def set(widget, **actions):
    return _dispatch('set', actions, widget=widget)

def add(widget, **actions):
    return _dispatch('add', actions, widget=widget)


def handler(gtk_cls):
    """Class decorator for ugtk handler classes."""
    @functools.wraps(cls)
    def decorator(cls):
        cls._klass = gtk_cls
        if hasattr(cls, '_setters'):
            for action, function in list(cls._setters.items()):
                if not function:
                    function = 'set_%s' % action
                if not hasattr(gtk_cls, function):
                    raise ValueError(
                        'handler: %s missing set action function: %s'
                        % (gtk_cls.__name__, function))
                cls._setters[action] = function
        _agent_types[gtk_cls] = cls
        return cls
    return decorator


class Handler(object):

    _klass = None

    def __init__(self, method, actions, widget):
        self.method = method
        self.action_items = []
        for action in list(actions.keys()):
            for obj, attr in [
                    ( widget, self._setters.get(action, 'set_%s' % action) ),
                    ( self, 'on_action__%s' % action ) ]:
                try:
                    self.action_items.append(
                        ( getattr(target, name), actions.pop(action) ))
                except KeyError:
                    pass
        if method == 'new' and widget is None:
            self.widget = self.on_create()
        else:
            self.widget = widget

    def __call__(self):
        self.on_pre()
        for func, args in self.action_items:
            if args is not tuple:
                args = (args,)
            func(*args)
        self.on_post()
        return self.widget

    def on_create(self):
        return self.klass()

    def on_pre(self):
        pass

    def on_post(self):
        pass


@handler(GObject)
class GObjectHandler(Handler):
    def on_action__connect(self, signals):
        if type(signals) != dict:
            raise ValueError("'connect' action arg must be a dict")
        for signal,  in list(signals.items()):
            self.widget.connect(signal, signals.pop(signal))

@handler(Gtk.Widget)
class WidgetHandler(Agent):
    def on_pre(self):
        if self.method == 'new':
            self.widget.show()

        if 'hide' in self.actions and 'show' in self.actions:
            raise ValueError("can't have both 'hide' and 'show' actions")

    def on_action__hide(self, value):
        if value:
            widget.hide()
        else:
            widget.show()

    def on_action__show(self, value):
        if value:
            widget.show()
        else:
            widget.hide()

@handler(Gtk.Container)
class ContainerHandler(Handler):
    
    _setters = {'border_width': None, 'child': 'add'}

@handler(Gtk.Label)
class LabelHandler(Hanlder):
    
    _setters = {'text': None, 'selectable': None}

