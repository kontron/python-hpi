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
