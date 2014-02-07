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

from pyparsing import Word, Or, StringStart, StringEnd, Suppress, Group
from pyparsing import delimitedList, alphanums, nums

tok_entity_type_str = Word(alphanums, alphanums + '_')
tok_entity_type_num = Word(nums).setParseAction(lambda s,l,t: [int(t[0])])
tok_entity_location = Word(nums).setParseAction(lambda s,l,t: [int(t[0])])
tok_entity_sub = (Suppress('{')
        + Or(tok_entity_type_str, tok_entity_type_num)
        + Suppress(',') + tok_entity_location + Suppress('}'))
tok_entity = (StringStart() + tok_entity_sub + StringEnd())
tok_entity_path = (StringStart() + Suppress('{')
        + delimitedList(Group(tok_entity_sub)) + Suppress('}')
        + StringEnd())

if __name__ == '__main__':
    print tok_entity_path.parseString('{{A,1},{B,2}}')
