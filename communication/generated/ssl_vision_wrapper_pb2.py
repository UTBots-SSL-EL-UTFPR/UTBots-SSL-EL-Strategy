# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: ssl_vision_wrapper.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from communication.generated import ssl_vision_detection_pb2 as ssl__vision__detection__pb2
from communication.generated import ssl_vision_geometry_pb2 as ssl__vision__geometry__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x18ssl_vision_wrapper.proto\x1a\x1assl_vision_detection.proto\x1a\x19ssl_vision_geometry.proto\"`\n\x11SSL_WrapperPacket\x12&\n\tdetection\x18\x01 \x01(\x0b\x32\x13.SSL_DetectionFrame\x12#\n\x08geometry\x18\x02 \x01(\x0b\x32\x11.SSL_GeometryDataB@Z>github.com/RoboCup-SSL/ssl-game-controller/internal/app/vision')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ssl_vision_wrapper_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'Z>github.com/RoboCup-SSL/ssl-game-controller/internal/app/vision'
  _SSL_WRAPPERPACKET._serialized_start=83
  _SSL_WRAPPERPACKET._serialized_end=179
# @@protoc_insertion_point(module_scope)
