# -*- Mode: Python; coding: utf-8 -*-

##
## Copyright (C) 2010 Mandriva S.A. <http://www.mandriva.com>
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

import gtk
import gobject


DISPATCHER_CLASS_ATTR = '__ugtk_dispatcher_class'


def dispatcher_for(klass):
    """Class decorator to mark a class as a ugtk action dispatcher, by
    placing a speciall class attribute."""
    def class_decorator(decorated_klass):
        setattr(decorated_klass, DISPATCHER_CLASS_ATTR, klass)
        return decorated_klass
    return class_decorator


class ActionDispatcher(object):
    """Base class for ugtk action dispatchers."""

    signals = []
    set_actions = {}

    def dispatch(self, method, widget, actions):
        """Method for dispatching actions."""

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
