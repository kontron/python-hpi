# Copyright (c) 2014  Kontron Europe GmbH
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

class SaHpiError(Exception):
    """This class represents an SA HPI error."""
    def __init__(self, errno, error):
        self.errno = errno
        self.error = error

    def __str__(self):
        return '%s: %s' % (self.__class__.__name__, self.error)

    def __repr__(self):
        return '%s(%d,"%s")' % (self.__class__.__name__, self.errno, self.error)

class RetriesExceededError(Exception):
    """Maximum number of retries was exceeded."""
    pass

class DecodingError(Exception):
    """Error while decoding data."""
    def __init__(self, error):
        self.error = error

    def __str__(self):
        return '%s: %s' % (self.__class__.__name__, self.error)

class EncodingError(Exception):
    """Error while encoding data."""
    def __init__(self, error):
        self.error = error

    def __str__(self):
        return '%s: %s' % (self.__class__.__name__, self.error)
