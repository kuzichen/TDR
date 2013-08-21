from hotlib.hp_config import *
from hotdata.syntactic_node import *
import sys
import os


class Walker:
	EN_HST_VALUE = 0,
	EN_HST_PARAMETER = 1,
	EN_HST_FIELD = 2,
	EN_HST_ENUM = 3,
	EN_HST_STRUCT = 4,
	EN_HST_UNION = 5,

	def __init__(self, document, target_dir):
		self.document = document
		self.symbols = {}
		self.domain = None
		self.target_dir = target_dir
		self.file_name = document['file_name'][:-3].replace('\\', '/').lstrip('./')

		file_name = self.file_name.split('/')[-1]
		output_path = target_dir.rstrip('/\\') + '/' + '/'.join(self.file_name.split('/')[:-1])
		os.makedirs(output_path, 0o777, True)

	def print_file_prefix(self):
		self.print_line(0, '/**')
		self.print_line(0, ' * Autogenerated by HotData (' + HOTPOT_VERSION + ')')
		self.print_line(0, ' *')
		self.print_line(0, ' * DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING')
		self.print_line(0, ' *  @generated')
		self.print_line(0, ' */')
		self.print_line(0, '')

	def print_line(self, n, str):
		for i in range(0,n):
			self.fout.write('    ')
		self.fout.write(str)
		self.fout.write('\n')

	def save_symbol(self, k, v):
		if(self.domain == None):
			self.symbols[k] = v
		else:
			self.symbols[self.domain + ':' + k] = v

	def find_symbol(self, k):
		if(self.domain != None):
			local_k = self.domain + ':' + k
			if(local_k in self.symbols):
				return self.symbols[local_k]
			elif(k in self.symbols):
				return self.symbols[k]
			else:
				return None
		elif(k in self.symbols):
			return self.symbols[k]
		else:
			return None

	def on_const(self, const):
		pass

	def on_typedef(self, typedef):
		pass

	def on_enum_begin(self, enum):
		pass

	def on_enum_field(self, enum_field):
		pass

	def on_enum_end(self, enum):
		pass

	def on_struct_begin(self, struct):
		pass

	def on_struct_field(self, struct_field):
		pass

	def on_struct_end(self, struct):
		pass

	def on_union_begin(self, union):
		pass

	def on_union_field(self, union_field):
		pass

	def on_union_end(self, union):
		pass

	def on_import(self, de_import):
		pass

	def on_unix_comment(self, unix_import):
		pass

	def on_document_begin(self, document):
		pass

	def on_document_end(self, document):
		pass

	def walk_const(self, const):
		self.save_symbol(const['identifier'], {'type' : Walker.EN_HST_VALUE})
		self.on_const(const)
		pass

	def walk_typedef(self, typedef):
		if(typedef['type']['type'] == E_SNT_REFER):
			self.save_symbol(typedef['name'], self.find_symbol(typedef['type']['ot']))
		self.on_typedef(typedef)
		pass

	def walk_enum(self, enum):
		self.save_symbol(enum['name'], {'type' : Walker.EN_HST_ENUM})
		self.on_enum_begin(enum)
		for enum_field in enum['enum_def_list']:
			self.save_symbol(enum_field['identifier'], {'type' : Walker.EN_HST_VALUE})
			self.on_enum_field(enum_field)
		self.on_enum_end(enum)

	def walk_struct(self, struct):
		self.save_symbol(struct['name'], {'type' : Walker.EN_HST_STRUCT})
		self.domain = struct['name']
		self.on_struct_begin(struct)
		for par in struct['parameters']['par_list']:
			self.save_symbol(par['identifier'], {'type' : Walker.EN_HST_PARAMETER})

		for struct_field in struct['field_list']['field_list']:
			self.save_symbol(struct_field['identifier'], {'type' : Walker.EN_HST_FIELD})
			self.on_struct_field(struct_field)
		self.on_struct_end(struct)
		self.domain = None

	def walk_union(self, union):
		self.save_symbol(union['name'], {'type' : Walker.EN_HST_UNION})
		self.domain = union['name']
		self.on_union_begin(union)
		for par in union['parameters']['par_list']:
			self.save_symbol(par['identifier'], {'type' : Walker.EN_HST_PARAMETER, 'para' : par})

		for union_field in union['field_list']['field_list']:
			self.save_symbol(union_field['identifier'], {'type' : Walker.EN_HST_FIELD})
			self.on_union_field(union_field)
		self.on_union_end(union)
		self.domain = None

	def walk_import(self, de_import):
		self.on_import(de_import)
		pass

	def walk_unix_comment(self, de_unix_comment):
		self.on_unix_comment(de_unix_comment)
		pass

	def walk(self):
		self.on_document_begin(self.document)
		for definition in self.document['definition_list']:
			if(definition['type'] == E_DT_CONST):
				self.walk_const(definition['definition']['de_const'])
			elif(definition['type'] == E_DT_TYPEDEF):
				self.walk_typedef(definition['definition']['de_typedef'])
			elif(definition['type'] == E_DT_ENUM):
				self.walk_enum(definition['definition']['de_enum'])
			elif(definition['type'] == E_DT_STRUCT):
				self.walk_struct(definition['definition']['de_struct'])
			elif(definition['type'] == E_DT_UNION):
				self.walk_union(definition['definition']['de_union'])
			elif(definition['type'] == E_DT_IMPORT):
				self.walk_import(definition['definition']['de_import'])
			elif(definition['type'] == E_DT_UNIX_COMMENT):
				self.walk_unix_comment(definition['definition']['de_unix_comment'])
		self.on_document_end(self.document)
		return True
