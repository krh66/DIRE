from collections import OrderedDict
from io import StringIO
import json
from typing import Dict, List


class SyntaxNode(object):
    """represent a node on an AST"""
    def __init__(self, node_id, node_type, address=None, children: List=None, named_fields: Dict=None):
        self.node_id = node_id
        self.node_type = node_type
        self.address = address
        self.children = []
        self.parent = None
        self.named_fields = OrderedDict()

        if named_fields:
            for field_name, field_val in named_fields.items():
                self.named_fields[field_name] = field_val
                setattr(self, field_name, field_val)

        if children:
            for child in children:
                self.add_child(child)

    def add_child(self, child: 'SyntaxNode') -> None:
        self.children.append(child)
        child.parent = self

    @classmethod
    def from_json_dict(cls, json_dict: Dict) -> 'SyntaxNode':
        named_fields = {k: v for k, v in json_dict.items() if k not in {'node_id', 'node_type', 'children', 'address'}}
        node = cls(json_dict['node_id'],
                   json_dict['node_type'],
                   json_dict['address'],
                   named_fields=named_fields)

        if 'children' in json_dict:
            children_list = json_dict['children']
        else:
            children_list = []
            if 'x' in json_dict: children_list.append(json_dict['x'])
            if 'y' in json_dict: children_list.append(json_dict['y'])

        for child_dict in children_list:
            child_node = SyntaxNode.from_json_dict(child_dict)
            node.add_child(child_node)

        return node

    @property
    def descendant_nodes(self):
        def _visit(node):
            yield node

            for child_node in self.children:
                yield from _visit(child_node)
        yield from _visit(self)

    def __iter__(self):
        return iter(self.descendant_nodes)

    def __hash__(self):
        code = hash(self.node_id, self.node_type, self.address)
        for child in self.children:
            code = code + 37 * hash(child)

        return code

    def __eq__(self, other):
        if not isinstance(other, self.__class__): return False

        if self.node_type != other.node_type: return False
        if self.address != other.address: return False
        if self.node_id != other.node_id: return False
        if len(self.children) != len(other.children): return False

        for i in range(len(self.children)):
            if self.children[i] != other.children[i]:
                return False

        if self.named_fields != other.named_fields: return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def to_string(self, sb=None):
        is_root = False
        if sb is None:
            is_root = True
            sb = StringIO()

        sb.write('(')
        sb.write(f'Node_{self.node_id}-{self.node_type}')

        for child in self.children:
            sb.write(' ')
            child.to_string(sb)

        sb.write(')')  # of node

        if is_root:
            return sb.getvalue()

    def __str__(self):
        return f'Node {self.node_id} {self.node_type}@{self.address}'

    __repr__ = __str__


class TerminalNode(SyntaxNode):
    """a terminal AST node representing variables or other terminal syntax tokens"""
    pass


class AbstractSyntaxTree(object):
    def __init__(self, ast: SyntaxNode, compilation_unit: str = None, code: str = None):
        self.ast = ast
        self.compilation_unit = compilation_unit
        self.code = code

    @classmethod
    def from_json_dict(cls, json_dict: Dict) -> 'AbstractSyntaxTree':
        root = SyntaxNode.from_json_dict(json_dict['ast'])
        tree = cls(root, compilation_unit=json_dict['function'], code=json_dict['raw_code'] if 'raw_code' in json_dict else None)

        return tree


if __name__ == '__main__':
    json_str = """
{
    "function": "ft_strncat",
    "raw_code": "__int64 __fastcall ft_strncat(__int64 @@VAR_2@@a1@@s1, __int64 @@VAR_3@@a2@@s2, unsigned __int64 @@VAR_4@@a3@@n)\n{\n  __int64 @@VAR_0@@v4@@i; // [rsp+18h] [rbp-10h]\n  unsigned __int64 @@VAR_1@@v5@@j; // [rsp+20h] [rbp-8h]\n\n  @@VAR_0@@v4@@i = 0LL;\n  @@VAR_1@@v5@@j = 0LL;\n  while ( *(_BYTE *)(@@VAR_2@@a1@@s1 + @@VAR_0@@v4@@i) )\n    ++@@VAR_0@@v4@@i;\n  while ( *(_BYTE *)(@@VAR_3@@a2@@s2 + @@VAR_1@@v5@@j) && @@VAR_1@@v5@@j < @@VAR_4@@a3@@n )\n    *(_BYTE *)(@@VAR_0@@v4@@i++ + @@VAR_2@@a1@@s1) = *(_BYTE *)(@@VAR_3@@a2@@s2 + @@VAR_1@@v5@@j++);\n  *(_BYTE *)(@@VAR_2@@a1@@s1 + @@VAR_0@@v4@@i) = 0;\n  return @@VAR_2@@a1@@s1;\n}\n",
    "ast": {
        "node_type": "block",
        "node_id": 0,
        "children": [
            {
                "node_type": "expr",
                "node_id": 1,
                "children": [
                    {
                        "node_type": "asg",
                        "node_id": 2,
                        "address": "00000010",
                        "y": {
                            "node_type": "num",
                            "node_id": 4,
                            "type": "signed __int64",
                            "name": "0LL",
                            "address": "00000010"
                        },
                        "x": {
                            "new_name": "i",
                            "parent_address": "00000010",
                            "var_id": "VAR_0",
                            "old_name": "v4",
                            "node_type": "var",
                            "node_id": 3,
                            "address": "FFFFFFFFFFFFFFFF",
                            "type": "__int64",
                            "ref_width": 8
                        },
                        "type": "__int64"
                    }
                ],
                "address": "00000010"
            },
            {
                "node_type": "expr",
                "node_id": 5,
                "children": [
                    {
                        "node_type": "asg",
                        "node_id": 6,
                        "address": "00000018",
                        "y": {
                            "node_type": "num",
                            "node_id": 8,
                            "type": "signed __int64",
                            "name": "0LL",
                            "address": "00000018"
                        },
                        "x": {
                            "new_name": "j",
                            "parent_address": "00000018",
                            "var_id": "VAR_1",
                            "old_name": "v5",
                            "node_type": "var",
                            "node_id": 7,
                            "address": "FFFFFFFFFFFFFFFF",
                            "type": "unsigned __int64",
                            "ref_width": 8
                        },
                        "type": "unsigned __int64"
                    }
                ],
                "address": "00000018"
            },
            {
                "node_type": "while",
                "node_id": 9,
                "children": [
                    {
                        "node_type": "block",
                        "node_id": 10,
                        "children": [
                            {
                                "node_type": "expr",
                                "node_id": 11,
                                "children": [
                                    {
                                        "x": {
                                            "new_name": "i",
                                            "parent_address": "00000022",
                                            "var_id": "VAR_0",
                                            "old_name": "v4",
                                            "node_type": "var",
                                            "node_id": 13,
                                            "address": "FFFFFFFFFFFFFFFF",
                                            "type": "__int64",
                                            "ref_width": 8
                                        },
                                        "node_type": "preinc",
                                        "node_id": 12,
                                        "type": "__int64",
                                        "address": "00000022"
                                    }
                                ],
                                "address": "00000022"
                            }
                        ],
                        "address": "00000022"
                    },
                    {
                        "node_type": "ptr",
                        "node_id": 14,
                        "address": "0000002F",
                        "x": {
                            "x": {
                                "node_type": "add",
                                "node_id": 16,
                                "address": "0000002F",
                                "y": {
                                    "new_name": "i",
                                    "parent_address": "0000002F",
                                    "var_id": "VAR_0",
                                    "old_name": "v4",
                                    "node_type": "var",
                                    "node_id": 18,
                                    "address": "FFFFFFFFFFFFFFFF",
                                    "type": "__int64",
                                    "ref_width": 8
                                },
                                "x": {
                                    "new_name": "s1",
                                    "parent_address": "0000002F",
                                    "var_id": "VAR_2",
                                    "old_name": "a1",
                                    "node_type": "var",
                                    "node_id": 17,
                                    "address": "FFFFFFFFFFFFFFFF",
                                    "type": "__int64",
                                    "ref_width": 8
                                },
                                "type": "__int64"
                            },
                            "node_type": "cast",
                            "node_id": 15,
                            "type": "_BYTE *",
                            "address": "0000002F"
                        },
                        "type": "_BYTE",
                        "pointer_size": 1
                    }
                ],
                "address": "00000037"
            },
            {
                "node_type": "while",
                "node_id": 19,
                "children": [
                    {
                        "node_type": "block",
                        "node_id": 20,
                        "children": [
                            {
                                "node_type": "expr",
                                "node_id": 21,
                                "children": [
                                    {
                                        "node_type": "asg",
                                        "node_id": 22,
                                        "address": "00000054",
                                        "y": {
                                            "node_type": "ptr",
                                            "node_id": 29,
                                            "address": "0000004E",
                                            "x": {
                                                "x": {
                                                    "node_type": "add",
                                                    "node_id": 31,
                                                    "address": "0000004E",
                                                    "y": {
                                                        "parent_address": "0000004E",
                                                        "node_type": "postinc",
                                                        "node_id": 33,
                                                        "address": "FFFFFFFFFFFFFFFF",
                                                        "x": {
                                                            "new_name": "j",
                                                            "parent_address": "0000004E",
                                                            "var_id": "VAR_1",
                                                            "old_name": "v5",
                                                            "node_type": "var",
                                                            "node_id": 34,
                                                            "address": "FFFFFFFFFFFFFFFF",
                                                            "type": "unsigned __int64",
                                                            "ref_width": 8
                                                        },
                                                        "type": "unsigned __int64"
                                                    },
                                                    "x": {
                                                        "new_name": "s2",
                                                        "parent_address": "0000004E",
                                                        "var_id": "VAR_3",
                                                        "old_name": "a2",
                                                        "node_type": "var",
                                                        "node_id": 32,
                                                        "address": "FFFFFFFFFFFFFFFF",
                                                        "type": "__int64",
                                                        "ref_width": 8
                                                    },
                                                    "type": "unsigned __int64"
                                                },
                                                "node_type": "cast",
                                                "node_id": 30,
                                                "type": "_BYTE *",
                                                "address": "0000004E"
                                            },
                                            "type": "_BYTE",
                                            "pointer_size": 1
                                        },
                                        "x": {
                                            "node_type": "ptr",
                                            "node_id": 23,
                                            "address": "00000043",
                                            "x": {
                                                "x": {
                                                    "node_type": "add",
                                                    "node_id": 25,
                                                    "address": "00000043",
                                                    "y": {
                                                        "new_name": "s1",
                                                        "parent_address": "00000043",
                                                        "var_id": "VAR_2",
                                                        "old_name": "a1",
                                                        "node_type": "var",
                                                        "node_id": 28,
                                                        "address": "FFFFFFFFFFFFFFFF",
                                                        "type": "__int64",
                                                        "ref_width": 8
                                                    },
                                                    "x": {
                                                        "parent_address": "00000043",
                                                        "node_type": "postinc",
                                                        "node_id": 26,
                                                        "address": "FFFFFFFFFFFFFFFF",
                                                        "x": {
                                                            "new_name": "i",
                                                            "parent_address": "00000043",
                                                            "var_id": "VAR_0",
                                                            "old_name": "v4",
                                                            "node_type": "var",
                                                            "node_id": 27,
                                                            "address": "FFFFFFFFFFFFFFFF",
                                                            "type": "__int64",
                                                            "ref_width": 8
                                                        },
                                                        "type": "__int64"
                                                    },
                                                    "type": "__int64"
                                                },
                                                "node_type": "cast",
                                                "node_id": 24,
                                                "type": "_BYTE *",
                                                "address": "00000043"
                                            },
                                            "type": "_BYTE",
                                            "pointer_size": 1
                                        },
                                        "type": "_BYTE"
                                    }
                                ],
                                "address": "00000054"
                            }
                        ],
                        "address": "00000054"
                    },
                    {
                        "node_type": "land",
                        "node_id": 35,
                        "address": "00000070",
                        "y": {
                            "node_type": "ult",
                            "node_id": 41,
                            "address": "0000007A",
                            "y": {
                                "new_name": "n",
                                "parent_address": "0000007A",
                                "var_id": "VAR_4",
                                "old_name": "a3",
                                "node_type": "var",
                                "node_id": 43,
                                "address": "FFFFFFFFFFFFFFFF",
                                "type": "unsigned __int64",
                                "ref_width": 8
                            },
                            "x": {
                                "new_name": "j",
                                "parent_address": "0000007A",
                                "var_id": "VAR_1",
                                "old_name": "v5",
                                "node_type": "var",
                                "node_id": 42,
                                "address": "FFFFFFFFFFFFFFFF",
                                "type": "unsigned __int64",
                                "ref_width": 8
                            },
                            "type": "bool"
                        },
                        "x": {
                            "node_type": "ptr",
                            "node_id": 36,
                            "address": "00000068",
                            "x": {
                                "x": {
                                    "node_type": "add",
                                    "node_id": 38,
                                    "address": "00000068",
                                    "y": {
                                        "new_name": "j",
                                        "parent_address": "00000068",
                                        "var_id": "VAR_1",
                                        "old_name": "v5",
                                        "node_type": "var",
                                        "node_id": 40,
                                        "address": "FFFFFFFFFFFFFFFF",
                                        "type": "unsigned __int64",
                                        "ref_width": 8
                                    },
                                    "x": {
                                        "new_name": "s2",
                                        "parent_address": "00000068",
                                        "var_id": "VAR_3",
                                        "old_name": "a2",
                                        "node_type": "var",
                                        "node_id": 39,
                                        "address": "FFFFFFFFFFFFFFFF",
                                        "type": "__int64",
                                        "ref_width": 8
                                    },
                                    "type": "unsigned __int64"
                                },
                                "node_type": "cast",
                                "node_id": 37,
                                "type": "_BYTE *",
                                "address": "00000068"
                            },
                            "type": "_BYTE",
                            "pointer_size": 1
                        },
                        "type": "bool"
                    }
                ],
                "address": "0000007A"
            },
            {
                "node_type": "expr",
                "node_id": 44,
                "children": [
                    {
                        "node_type": "asg",
                        "node_id": 45,
                        "address": "00000087",
                        "y": {
                            "node_type": "num",
                            "node_id": 51,
                            "type": "char",
                            "name": "0",
                            "address": "00000087"
                        },
                        "x": {
                            "node_type": "ptr",
                            "node_id": 46,
                            "address": "00000084",
                            "x": {
                                "x": {
                                    "node_type": "add",
                                    "node_id": 48,
                                    "address": "00000084",
                                    "y": {
                                        "new_name": "i",
                                        "parent_address": "00000084",
                                        "var_id": "VAR_0",
                                        "old_name": "v4",
                                        "node_type": "var",
                                        "node_id": 50,
                                        "address": "FFFFFFFFFFFFFFFF",
                                        "type": "__int64",
                                        "ref_width": 8
                                    },
                                    "x": {
                                        "new_name": "s1",
                                        "parent_address": "00000084",
                                        "var_id": "VAR_2",
                                        "old_name": "a1",
                                        "node_type": "var",
                                        "node_id": 49,
                                        "address": "FFFFFFFFFFFFFFFF",
                                        "type": "__int64",
                                        "ref_width": 8
                                    },
                                    "type": "__int64"
                                },
                                "node_type": "cast",
                                "node_id": 47,
                                "type": "_BYTE *",
                                "address": "00000084"
                            },
                            "type": "_BYTE",
                            "pointer_size": 1
                        },
                        "type": "_BYTE"
                    }
                ],
                "address": "00000087"
            },
            {
                "node_type": "return",
                "node_id": 52,
                "children": [
                    {
                        "new_name": "s1",
                        "parent_address": "0000008E",
                        "var_id": "VAR_2",
                        "old_name": "a1",
                        "node_type": "var",
                        "node_id": 53,
                        "address": "FFFFFFFFFFFFFFFF",
                        "type": "__int64",
                        "ref_width": 8
                    }
                ],
                "address": "0000008E"
            }
        ],
        "address": "00000010"
    }
}
"""
    json_dict = json.loads(json_str)
    tree = AbstractSyntaxTree.from_json_dict(json_dict)
    pass