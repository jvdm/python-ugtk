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

import inspect
from ugtk.dispatchers import default
from ugtk.dispatchers.base import ActionDispatcher, DISPATCHER_CLASS_ATTR


registered = {}


def register(klass, dispatcher_class):
    # Can't have two dispatchers for the same class:
    assert(registered.get(klass) == None)
    if not issubclass(dispatcher_class, ActionDispatcher):
        raise ValueError('%s must be a subclass of %s to be registered as '
                         'a ugtk action dispatcher.'
                         % (klass.__name__, ActionDispatcher.__name__))

    registered[klass] = dispatcher_class

def create_dispatcher(klass):
    if klass not in registered:
        return None
    return registered[klass]()


# Initialize default dispatchers: go into the default module, look for
# all classes inherited from ActionDispatcher and register if they
# have the DISPATCHER_CLASS_ATTR atttribute ...

for _, klass in inspect.getmembers(default,
                                      lambda o: inspect.isclass(o) \
                                          and issubclass(o, ActionDispatcher)):
    try:
        register(getattr(klass, DISPATCHER_CLASS_ATTR), klass)
    except AttributeError:
        pass
