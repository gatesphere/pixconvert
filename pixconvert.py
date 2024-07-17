#!/usr/bin/env python

from struct import unpack
from PIL import Image
from argparse import ArgumentParser
from sys import exit
from os.path import basename, splitext


# first four bytes of a PIX file
IDENT = b'PIXB'

# Dimension is a flag in the file header:
# 0 = 16x16, skip of 8
# 1 = 24x24, skip of 4
# 2 = 32x32, skip of 0
# the 'skip' value allows packing different amounts 
# of pixel data in the same constant filesize
DIMS = [(16,8), (24,4), (32,0)]

# palette extracted from firmware
COLOR_MAP = [ 0xffffff, 0xa8bfe9, 0xacc7ec, 0xb0cfef,
              0xb7ddf4, 0xbbe4f7, 0xbbe4f7, 0xbeebfa,
              0xc1f2fd, 0xc4f9ff, 0xc3f2f2, 0xc5ebe3,
              0xc0e3d4, 0xbedbc5, 0xccddc5, 0xdadec4,
              0xe8e0c4, 0xf5e1c4, 0xeed9c8, 0xe6d0cb,
              0xdec5ce, 0xd5bad0, 0xcbbbd6, 0xc0bddd,
              0xb4bee3, 0xd2d1d1, 0x5978d3, 0x5f8ad8,
              0x649bde, 0x69abe3, 0x6ebae9, 0x72c9ef,
              0x77d7f4, 0x7ae5fa, 0x87f3ff, 0x7ee4e4,
              0x7dd5c6, 0x7cc5a5, 0x7bb482, 0x98b781,
              0xb5ba7f, 0xd0bd7d, 0xe9bf7b, 0xddb48a,
              0xcea396, 0xbb8e9f, 0xa672a5, 0x9574b1,
              0x8376bd, 0x6f77c8, 0x7f7e7d, 0x1f00c1,
              0x1f3fc6, 0x1e5ecc, 0x1d79d4, 0x1a93dc,
              0x14abe5, 0x00c2ee, 0x00d8f6, 0x00ecff,
              0x1dd5d4, 0x30bda2, 0x3aa56b, 0x408f11,
              0x669200, 0x8e9500, 0xb79900, 0xdd9c00,
              0xcb8e34, 0xb2765a, 0x96546f, 0x7a177e,
              0x661390, 0x500ea2, 0x3900b2, 0x211e1f,
              0x151455, 0x17255f, 0x183669, 0x194875,
              0x1a5b82, 0x1a708f, 0x19859e, 0x169bad,
              0x12acba, 0x1f9898, 0x27816f, 0x2b6c45,
              0x2c5a00, 0x456100, 0x646800, 0x867000,
              0xa47700, 0x926926, 0x7a533f, 0x62374a,
              0x4d0d50, 0x3e0c56, 0x2e1058, 0x201359 ]

PLAYDATE_WHITE_VAL = 0xffffff
PLAYDATE_BLACK_VAL = 0x211e1f

class PIXFile:
  @classmethod
  def open(cls, path):
    with open(path, 'rb') as buffer:
      return cls(buffer)

  def __init__(self, buffer):
    self.buffer = buffer
    self.dim = None
    self.pix_dim = None
    self.skip = None
    self.data = None
    self.read_header()
    self.read_body()

  def read_header(self):
    # read header info
    self.buffer.seek(0x00)
    ident = self.buffer.read(4)
    assert ident == IDENT, 'Ident incorrect.'
    self.buffer.seek(0x06)
    d = bytes(self.buffer.read(2))
    dim = unpack('<h',d)[0]
    assert dim in [0,1,2], f'Invalid dimension: {dim}'
    self.dim = dim
    self.pix_dim, self.skip = DIMS[dim]
    # the rest of the header is unknown to me, but also appears 
    # unnecessary to decode the file properly

  def read_body(self):
    # header is 0x20 bytes long
    self.buffer.seek(0x20)
    body = self.buffer.read()
    self.data = []
    body_index = 0
    for idx in range(0x80):
      # read 8 bytes into file_data, and copy it (padded if necessary) into current_bytes
      file_data = list(body[body_index:body_index+8])
      if len(file_data) < 8:
        current_bytes = [ 0 for _ in range(8-len(file_data)) ] + list(file_data)
      else:
        current_bytes = list(file_data)

      # magic bit shuffling nonsense, reverse engineered
      current_bytes[0] = (file_data[0] & 0x7f)
      current_bytes[1] = (file_data[1] & 0x3f) << 1
      current_bytes[1] = current_bytes[1] + (file_data[0] >> 7)
      current_bytes[2] = (file_data[2] & 0x1f) << 2
      current_bytes[2] = current_bytes[2] + (file_data[1] >> 6)
      current_bytes[3] = (file_data[3] & 0xf) << 3
      current_bytes[3] = current_bytes[3] + (file_data[2] >> 5)
      current_bytes[4] = (file_data[4] & 0x7) << 4
      current_bytes[4] = current_bytes[4] + (file_data[3] >> 4)
      current_bytes[5] = (file_data[5] & 0x3) << 5
      current_bytes[5] = current_bytes[5] + (file_data[4] >> 3)
      current_bytes[6] = (file_data[6] & 0x1) << 6
      current_bytes[6] = current_bytes[6] + (file_data[5] >> 2)
      current_bytes[7] = file_data[6] >> 1

      # set up for next iteration
      self.data.extend(current_bytes)
      body_index += 7

  def get_color_data(self):
    # interpret the inflated data into palette indexes
    color_data = [ [0]*self.pix_dim for _ in range(self.pix_dim) ]
    for pix_x in range(self.pix_dim):
      for pix_y in range(self.pix_dim):
        v = self.skip + ((self.skip + pix_y) * 0x20) + pix_x
        pixel_idx = self.data[v]
        if pixel_idx < len(COLOR_MAP):
          out_color = COLOR_MAP[pixel_idx]
        else:
          out_color = 0xffffff # white for any invalid colors
        color_data[pix_x][pix_y] = out_color
    return color_data

if __name__ == '__main__':
  parser = ArgumentParser(prog="pixconvert.py", 
      description="Converts Minbay Pixel Artboard .PIX files to PNG or BMP files")
  parser.add_argument("-i", "--infile", help="input filename", dest="in_file", 
      required=True)
  parser.add_argument("-o", "--outfile", default=None, help="output filename", 
      dest="out_file", required=False)
  parser.add_argument("-b", "--bmp", help="produce BMP instead of PNG outut", 
      action="store_true", dest="bmp", required=False)
  parser.add_argument("-p", "--playdate", help="produce Playdate-compatible PNG output", 
      action="store_true", dest="playdate", required=False)
  args = parser.parse_args()

  if args.playdate and args.bmp:
    print("Options --bmp and --playdate are mutually exclusive.")
    exit()

  if args.out_file is None:
    args.out_file = splitext(basename(args.in_file))[0]
    if args.bmp:
      args.out_file += '.bmp'
    else:
      args.out_file += '.png'
    print(f"No outfile provided, defaulting to {args.out_file}")

  pixfile = PIXFile.open(args.in_file)
  color_data = pixfile.get_color_data()

  # open as an image
  i = Image.new('RGBA', (pixfile.pix_dim, pixfile.pix_dim))
  # there's definitely a better way to do this, but this works 
  # and it's performant enough for the tiny images we're working with.
  px = i.load()
  for x in range(pixfile.pix_dim):
    for y in range(pixfile.pix_dim):
      c = color_data[x][y]
      if args.playdate:
        if c == PLAYDATE_BLACK_VAL:
          c = 0xff000000
        elif c == PLAYDATE_WHITE_VAL:
          c = 0xffffffff
        else: # every other color is 100% transparent
          c = 0x00000000
      else:
        c += 0xff000000 # add 100% alpha (full opaque)
      px[x,y] = c
  i.save(args.out_file)
