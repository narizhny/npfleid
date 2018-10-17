#!/usr/bin/env python

class nginx_object(object):
	def __init__(self, pname = None, pvalue = None):
		self.properties = []
		if pname:
			self.properties.append( (pname, pvalue) )

	def add_property(self, name, value):
		self.properties.append((name, value))

class nginx_object_serializer(object):
	def __init__(self, indent):
		self.indent = indent

	def to_string(self, object):
		return self._get_body(object, '')

	def _value_to_string(self, value, indent):
		if type(value) == list:
			return ' '.join([self._value_to_string(v, indent) for v in value])
		if type(value) == nginx_object:
			return '{\n' +  self._get_body(value, indent + self.indent) + '\n' + indent + '}'
		return str(value)

	def _property_to_line(self, name, value, indent):
		result = indent + name + ' ' + self._value_to_string(value, indent)
		if type(value) == nginx_object \
			or type(value) == list and len(value) and type(value[-1]) == nginx_object:
			return result
		return result + ';'

	def _get_body(self, object, indent):
		return '\n'.join([self._property_to_line(p[0], p[1], indent) for p in object.properties])