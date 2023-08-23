#!/usr/bin/env python3

import typing


class StructTextParserNode(object):
	def __init__(self, key: str, value: typing.Union[None, list, str],
			parent=None, **kw):
		super().__init__(**kw)
		self.key = key
		self.value = value
		self.parent = parent
		return

	def _serialize_value(self, indent="\t", indent_level=0, eol="\n") -> str:
		if self.value is None:
			return ""
		elif isinstance(self.value, str):
			return self.value
		else:
			indent_str = indent * indent_level
			lines = [indent_str + "{"] \
				+ [node.serialize(indent=indent, indent_level=indent_level + 1,
					eol=eol) for node in self.value] \
				+ [indent_str + "}"]
			return eol.join(lines) + eol

	def serialize(self, indent="\t", indent_level=0, eol="\n") -> str:
		indent_str = indent * indent_level

		value_str = self._serialize_value(indent=indent,
			indent_level=indent_level, eol=eol)

		if ((self.key is not None) and (self.value is not None)):
			return indent_str + self.key + " " + value_str
		elif self.value is None:
			return indent_str + self.key
		elif self.key is None:
			return value_str


class StructTextParserNodeRoot(StructTextParserNode):
	def __init__(self):
		super().__init__(key="root", value=list(), parent=None)
		return

	def serialize(self, indent="\t", indent_level=0, eol="\n") -> str:
		lines = [node.serialize(indent=indent, indent_level=indent_level,
			eol=eol) for node in self.value]
		return eol.join(lines)


class StructTextParser(object):
	def __init__(self, *ka, **kw):
		super().__init__(*ka, **kw)
		self._cur_key = None
		self.root = StructTextParserNodeRoot()
		self._cur_node = self.root
		return

	class ParsingError(ValueError):
		pass

	def _insert_node(self, key, value):
		node = StructTextParserNode(key=key, value=value, parent=self._cur_node)
		self._cur_node.value.append(node)
		self._cur_key = None
		return node

	def _parse_line(self, il: int, line: str):
		line = line.strip()
		if line == "":
			pass
		elif line == "{":
			self._cur_node = self._insert_node(key=None, value=list())
		elif line == "}":
			self._cur_node = self._cur_node.parent
			if self._cur_node is None:
				raise self.ParsingError("line %u: invalid '}'" % (il + 1))
		else:
			kv = line.split(" ", maxsplit=1)
			if len(kv) == 1:
				self._insert_node(key=kv[0], value=None)
			else:
				self._insert_node(key=kv[0], value=kv[1])
		return

	@classmethod
	def load(cls, fname, **kw):
		with open(fname, "r") as fp:
			new = cls.loads(fp.read(), **kw)
		return new

	@classmethod
	def loads(cls, s: str, **kw):
		new = cls(**kw)

		for il, line in enumerate(s.splitlines()):
			new._parse_line(il, line)

		if new._cur_node is not new.root:
			raise cls.ParsingError(
				"line %u: unexpected end of file" % (il + 1)
			)

		return new

	def dumps(self, indent="\t", eol="\n"):
		return self.root.serialize(indent=indent, indent_level=0, eol=eol)

	def dump(self, fname, indent="\t", eol="\n"):
		with open(fname, "w") as fp:
			fp.write(self.dumps(indent=indent, eol=eol))
		return


if __name__ == "__main__":
	pass
