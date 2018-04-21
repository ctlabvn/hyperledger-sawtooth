# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: sawtooth_validator/protobuf/authorization.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='sawtooth_validator/protobuf/authorization.proto',
  package='',
  syntax='proto3',
  serialized_pb=_b('\n/sawtooth_validator/protobuf/authorization.proto\"%\n\x11\x43onnectionRequest\x12\x10\n\x08\x65ndpoint\x18\x01 \x01(\t\"\xca\x02\n\x12\x43onnectionResponse\x12,\n\x05roles\x18\x01 \x03(\x0b\x32\x1d.ConnectionResponse.RoleEntry\x12*\n\x06status\x18\x02 \x01(\x0e\x32\x1a.ConnectionResponse.Status\x1a^\n\tRoleEntry\x12\x17\n\x04role\x18\x01 \x01(\x0e\x32\t.RoleType\x12\x38\n\tauth_type\x18\x02 \x01(\x0e\x32%.ConnectionResponse.AuthorizationType\"-\n\x06Status\x12\x10\n\x0cSTATUS_UNSET\x10\x00\x12\x06\n\x02OK\x10\x01\x12\t\n\x05\x45RROR\x10\x02\"K\n\x11\x41uthorizationType\x12\x1c\n\x18\x41UTHORIZATION_TYPE_UNSET\x10\x00\x12\t\n\x05TRUST\x10\x01\x12\r\n\tCHALLENGE\x10\x02\"I\n\x19\x41uthorizationTrustRequest\x12\x18\n\x05roles\x18\x01 \x03(\x0e\x32\t.RoleType\x12\x12\n\npublic_key\x18\x02 \x01(\t\"6\n\x1a\x41uthorizationTrustResponse\x12\x18\n\x05roles\x18\x01 \x03(\x0e\x32\t.RoleType\"6\n\x16\x41uthorizationViolation\x12\x1c\n\tviolation\x18\x01 \x01(\x0e\x32\t.RoleType\"\x1f\n\x1d\x41uthorizationChallengeRequest\"1\n\x1e\x41uthorizationChallengeResponse\x12\x0f\n\x07payload\x18\x01 \x01(\x0c\"_\n\x1c\x41uthorizationChallengeSubmit\x12\x12\n\npublic_key\x18\x01 \x01(\t\x12\x11\n\tsignature\x18\x03 \x01(\t\x12\x18\n\x05roles\x18\x04 \x03(\x0e\x32\t.RoleType\"8\n\x1c\x41uthorizationChallengeResult\x12\x18\n\x05roles\x18\x01 \x03(\x0e\x32\t.RoleType*5\n\x08RoleType\x12\x13\n\x0fROLE_TYPE_UNSET\x10\x00\x12\x07\n\x03\x41LL\x10\x01\x12\x0b\n\x07NETWORK\x10\x02\x42,\n\x15sawtooth.sdk.protobufP\x01Z\x11\x61uthorization_pb2b\x06proto3')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

_ROLETYPE = _descriptor.EnumDescriptor(
  name='RoleType',
  full_name='RoleType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='ROLE_TYPE_UNSET', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ALL', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='NETWORK', index=2, number=2,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=849,
  serialized_end=902,
)
_sym_db.RegisterEnumDescriptor(_ROLETYPE)

RoleType = enum_type_wrapper.EnumTypeWrapper(_ROLETYPE)
ROLE_TYPE_UNSET = 0
ALL = 1
NETWORK = 2


_CONNECTIONRESPONSE_STATUS = _descriptor.EnumDescriptor(
  name='Status',
  full_name='ConnectionResponse.Status',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='STATUS_UNSET', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='OK', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ERROR', index=2, number=2,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=299,
  serialized_end=344,
)
_sym_db.RegisterEnumDescriptor(_CONNECTIONRESPONSE_STATUS)

_CONNECTIONRESPONSE_AUTHORIZATIONTYPE = _descriptor.EnumDescriptor(
  name='AuthorizationType',
  full_name='ConnectionResponse.AuthorizationType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='AUTHORIZATION_TYPE_UNSET', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='TRUST', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CHALLENGE', index=2, number=2,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=346,
  serialized_end=421,
)
_sym_db.RegisterEnumDescriptor(_CONNECTIONRESPONSE_AUTHORIZATIONTYPE)


_CONNECTIONREQUEST = _descriptor.Descriptor(
  name='ConnectionRequest',
  full_name='ConnectionRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='endpoint', full_name='ConnectionRequest.endpoint', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=51,
  serialized_end=88,
)


_CONNECTIONRESPONSE_ROLEENTRY = _descriptor.Descriptor(
  name='RoleEntry',
  full_name='ConnectionResponse.RoleEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='role', full_name='ConnectionResponse.RoleEntry.role', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='auth_type', full_name='ConnectionResponse.RoleEntry.auth_type', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=203,
  serialized_end=297,
)

_CONNECTIONRESPONSE = _descriptor.Descriptor(
  name='ConnectionResponse',
  full_name='ConnectionResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='roles', full_name='ConnectionResponse.roles', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='status', full_name='ConnectionResponse.status', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_CONNECTIONRESPONSE_ROLEENTRY, ],
  enum_types=[
    _CONNECTIONRESPONSE_STATUS,
    _CONNECTIONRESPONSE_AUTHORIZATIONTYPE,
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=91,
  serialized_end=421,
)


_AUTHORIZATIONTRUSTREQUEST = _descriptor.Descriptor(
  name='AuthorizationTrustRequest',
  full_name='AuthorizationTrustRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='roles', full_name='AuthorizationTrustRequest.roles', index=0,
      number=1, type=14, cpp_type=8, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='public_key', full_name='AuthorizationTrustRequest.public_key', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=423,
  serialized_end=496,
)


_AUTHORIZATIONTRUSTRESPONSE = _descriptor.Descriptor(
  name='AuthorizationTrustResponse',
  full_name='AuthorizationTrustResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='roles', full_name='AuthorizationTrustResponse.roles', index=0,
      number=1, type=14, cpp_type=8, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=498,
  serialized_end=552,
)


_AUTHORIZATIONVIOLATION = _descriptor.Descriptor(
  name='AuthorizationViolation',
  full_name='AuthorizationViolation',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='violation', full_name='AuthorizationViolation.violation', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=554,
  serialized_end=608,
)


_AUTHORIZATIONCHALLENGEREQUEST = _descriptor.Descriptor(
  name='AuthorizationChallengeRequest',
  full_name='AuthorizationChallengeRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=610,
  serialized_end=641,
)


_AUTHORIZATIONCHALLENGERESPONSE = _descriptor.Descriptor(
  name='AuthorizationChallengeResponse',
  full_name='AuthorizationChallengeResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='payload', full_name='AuthorizationChallengeResponse.payload', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=643,
  serialized_end=692,
)


_AUTHORIZATIONCHALLENGESUBMIT = _descriptor.Descriptor(
  name='AuthorizationChallengeSubmit',
  full_name='AuthorizationChallengeSubmit',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='public_key', full_name='AuthorizationChallengeSubmit.public_key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='signature', full_name='AuthorizationChallengeSubmit.signature', index=1,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='roles', full_name='AuthorizationChallengeSubmit.roles', index=2,
      number=4, type=14, cpp_type=8, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=694,
  serialized_end=789,
)


_AUTHORIZATIONCHALLENGERESULT = _descriptor.Descriptor(
  name='AuthorizationChallengeResult',
  full_name='AuthorizationChallengeResult',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='roles', full_name='AuthorizationChallengeResult.roles', index=0,
      number=1, type=14, cpp_type=8, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=791,
  serialized_end=847,
)

_CONNECTIONRESPONSE_ROLEENTRY.fields_by_name['role'].enum_type = _ROLETYPE
_CONNECTIONRESPONSE_ROLEENTRY.fields_by_name['auth_type'].enum_type = _CONNECTIONRESPONSE_AUTHORIZATIONTYPE
_CONNECTIONRESPONSE_ROLEENTRY.containing_type = _CONNECTIONRESPONSE
_CONNECTIONRESPONSE.fields_by_name['roles'].message_type = _CONNECTIONRESPONSE_ROLEENTRY
_CONNECTIONRESPONSE.fields_by_name['status'].enum_type = _CONNECTIONRESPONSE_STATUS
_CONNECTIONRESPONSE_STATUS.containing_type = _CONNECTIONRESPONSE
_CONNECTIONRESPONSE_AUTHORIZATIONTYPE.containing_type = _CONNECTIONRESPONSE
_AUTHORIZATIONTRUSTREQUEST.fields_by_name['roles'].enum_type = _ROLETYPE
_AUTHORIZATIONTRUSTRESPONSE.fields_by_name['roles'].enum_type = _ROLETYPE
_AUTHORIZATIONVIOLATION.fields_by_name['violation'].enum_type = _ROLETYPE
_AUTHORIZATIONCHALLENGESUBMIT.fields_by_name['roles'].enum_type = _ROLETYPE
_AUTHORIZATIONCHALLENGERESULT.fields_by_name['roles'].enum_type = _ROLETYPE
DESCRIPTOR.message_types_by_name['ConnectionRequest'] = _CONNECTIONREQUEST
DESCRIPTOR.message_types_by_name['ConnectionResponse'] = _CONNECTIONRESPONSE
DESCRIPTOR.message_types_by_name['AuthorizationTrustRequest'] = _AUTHORIZATIONTRUSTREQUEST
DESCRIPTOR.message_types_by_name['AuthorizationTrustResponse'] = _AUTHORIZATIONTRUSTRESPONSE
DESCRIPTOR.message_types_by_name['AuthorizationViolation'] = _AUTHORIZATIONVIOLATION
DESCRIPTOR.message_types_by_name['AuthorizationChallengeRequest'] = _AUTHORIZATIONCHALLENGEREQUEST
DESCRIPTOR.message_types_by_name['AuthorizationChallengeResponse'] = _AUTHORIZATIONCHALLENGERESPONSE
DESCRIPTOR.message_types_by_name['AuthorizationChallengeSubmit'] = _AUTHORIZATIONCHALLENGESUBMIT
DESCRIPTOR.message_types_by_name['AuthorizationChallengeResult'] = _AUTHORIZATIONCHALLENGERESULT
DESCRIPTOR.enum_types_by_name['RoleType'] = _ROLETYPE

ConnectionRequest = _reflection.GeneratedProtocolMessageType('ConnectionRequest', (_message.Message,), dict(
  DESCRIPTOR = _CONNECTIONREQUEST,
  __module__ = 'sawtooth_validator.protobuf.authorization_pb2'
  # @@protoc_insertion_point(class_scope:ConnectionRequest)
  ))
_sym_db.RegisterMessage(ConnectionRequest)

ConnectionResponse = _reflection.GeneratedProtocolMessageType('ConnectionResponse', (_message.Message,), dict(

  RoleEntry = _reflection.GeneratedProtocolMessageType('RoleEntry', (_message.Message,), dict(
    DESCRIPTOR = _CONNECTIONRESPONSE_ROLEENTRY,
    __module__ = 'sawtooth_validator.protobuf.authorization_pb2'
    # @@protoc_insertion_point(class_scope:ConnectionResponse.RoleEntry)
    ))
  ,
  DESCRIPTOR = _CONNECTIONRESPONSE,
  __module__ = 'sawtooth_validator.protobuf.authorization_pb2'
  # @@protoc_insertion_point(class_scope:ConnectionResponse)
  ))
_sym_db.RegisterMessage(ConnectionResponse)
_sym_db.RegisterMessage(ConnectionResponse.RoleEntry)

AuthorizationTrustRequest = _reflection.GeneratedProtocolMessageType('AuthorizationTrustRequest', (_message.Message,), dict(
  DESCRIPTOR = _AUTHORIZATIONTRUSTREQUEST,
  __module__ = 'sawtooth_validator.protobuf.authorization_pb2'
  # @@protoc_insertion_point(class_scope:AuthorizationTrustRequest)
  ))
_sym_db.RegisterMessage(AuthorizationTrustRequest)

AuthorizationTrustResponse = _reflection.GeneratedProtocolMessageType('AuthorizationTrustResponse', (_message.Message,), dict(
  DESCRIPTOR = _AUTHORIZATIONTRUSTRESPONSE,
  __module__ = 'sawtooth_validator.protobuf.authorization_pb2'
  # @@protoc_insertion_point(class_scope:AuthorizationTrustResponse)
  ))
_sym_db.RegisterMessage(AuthorizationTrustResponse)

AuthorizationViolation = _reflection.GeneratedProtocolMessageType('AuthorizationViolation', (_message.Message,), dict(
  DESCRIPTOR = _AUTHORIZATIONVIOLATION,
  __module__ = 'sawtooth_validator.protobuf.authorization_pb2'
  # @@protoc_insertion_point(class_scope:AuthorizationViolation)
  ))
_sym_db.RegisterMessage(AuthorizationViolation)

AuthorizationChallengeRequest = _reflection.GeneratedProtocolMessageType('AuthorizationChallengeRequest', (_message.Message,), dict(
  DESCRIPTOR = _AUTHORIZATIONCHALLENGEREQUEST,
  __module__ = 'sawtooth_validator.protobuf.authorization_pb2'
  # @@protoc_insertion_point(class_scope:AuthorizationChallengeRequest)
  ))
_sym_db.RegisterMessage(AuthorizationChallengeRequest)

AuthorizationChallengeResponse = _reflection.GeneratedProtocolMessageType('AuthorizationChallengeResponse', (_message.Message,), dict(
  DESCRIPTOR = _AUTHORIZATIONCHALLENGERESPONSE,
  __module__ = 'sawtooth_validator.protobuf.authorization_pb2'
  # @@protoc_insertion_point(class_scope:AuthorizationChallengeResponse)
  ))
_sym_db.RegisterMessage(AuthorizationChallengeResponse)

AuthorizationChallengeSubmit = _reflection.GeneratedProtocolMessageType('AuthorizationChallengeSubmit', (_message.Message,), dict(
  DESCRIPTOR = _AUTHORIZATIONCHALLENGESUBMIT,
  __module__ = 'sawtooth_validator.protobuf.authorization_pb2'
  # @@protoc_insertion_point(class_scope:AuthorizationChallengeSubmit)
  ))
_sym_db.RegisterMessage(AuthorizationChallengeSubmit)

AuthorizationChallengeResult = _reflection.GeneratedProtocolMessageType('AuthorizationChallengeResult', (_message.Message,), dict(
  DESCRIPTOR = _AUTHORIZATIONCHALLENGERESULT,
  __module__ = 'sawtooth_validator.protobuf.authorization_pb2'
  # @@protoc_insertion_point(class_scope:AuthorizationChallengeResult)
  ))
_sym_db.RegisterMessage(AuthorizationChallengeResult)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('\n\025sawtooth.sdk.protobufP\001Z\021authorization_pb2'))
# @@protoc_insertion_point(module_scope)
