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


class Actions(object):
    def __init__(self, method, actions):
        self.method = method
        self.actions = actions


class ActionHandler(object):
    """Represent a ugtk action handler class."""

    signals = []
    set_actions = {}

    def handle(self, widget, actions):
        """Apply actions to the widget the method."""

        self.on_start_dispatch(method, widget, actions)
        self.__dispatch_set_action(widget, actions)
        # Dispatch the remaining actions to callbacks, ignore if they
        # don't exist ...
        for action in actions.keys():
            callback_name = 'on_%s__callback' % action
            if hasattr(self, callback_name):
                callback = getattr(self, callback_name)
                callback(method, widget, actions.pop(action))
        self.on_finalize_dispatch(method, widget, actions)

    def __dispatch_set_action(self, widget, actions):
        for action in self.set_actions:
            if action in actions:
                method = self.set_actions[action]
                if not method:
                    method = "set_%s" % action
                getattr(widget, method)(actions.pop(action))

    def on_start_dispatch(self, method, widget, actions):
        """Called before any other operation during a dispatch."""
        pass

    def on_finalize_dispatch(self, method, widget, actions):
        """Called after all other operations during a dispatch."""
        pass

    def on_create(self, klass, actions):
        """Called to create an object of the class."""
        raise ValueError("creating widget for class %s is not supported"
                         % klass.__name__)


_dispatchers = {}

def register(gtk_cls, dispatcher_cls):
    """Register a new dispatcher for the selected GTK class."""
    try:
        registered[gtk_cls]
    except KeyError:
    if not issubclass(dispatcher_cls, ActionDispatcher):
        raise ValueError('%s must be a subclass of %s to be registered as '
                         'a ugtk action dispatcher.'
                         % (klass.__name__, ActionDispatcher.__name__))

    registered[klass] = dispatcher_class
