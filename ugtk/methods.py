##
## Copyright (C) 2010 J. Victor Martins, <jvdm@sdf.org.>
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
##
## Contributor(s):	J. Victor Martins <jvdm@sdf.org>
##

import gtk
import inspect
import ugtk.dispatchers


def new(klass, **actions):
    return _execute_method('new', klass, None, actions)


def set(widget, **actions):
    return _execute_method('set', widget.__class__, widget, actions)


def add(widget, **actions):
    return _execute_method('add', widget.__class__, widget, actions)


def _execute_method(method, klass, widget, actions):
    """Dispatch actions for each subclass of widget."""

    for subclass in inspect.getmro(klass):
        dispatcher = ugtk.dispatchers.create_dispatcher(subclass)
        if dispatcher == None:
            if subclass == klass:
                # ugtk doesn't support calling a method for this class:
                raise ValueError("ugtk.%s is not supported for class %s"
                                 % (method, klass.__name__))
        else:
            # We create the object here, instead of dispatching
            # creation to the dispatcher ...
            if subclass == klass and method == 'new':
                widget = dispatcher.on_create(klass, actions)
            dispatcher.dispatch(method, widget, actions)

    if actions:
        # Some action were not used, currently this is an error:
        raise ValueError("Unknow action(s) for '%s' on %s: %s."
                         % (method,
                            klass.__name__,
                            ', '.join(actions)))
    return widget
