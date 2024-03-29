# Sourced from with minor changes: https://github.com/Holzhaus/serato-tags/blob/master/scripts/database_v2.py
# Licensed as MIT

import argparse
import struct
import io
import sys


FIELDPARSERS = {
    'b': lambda x: struct.unpack('?', x)[0],
    'o': lambda x: tuple(parse(io.BytesIO(x))),
    'p': lambda x: (x[1:] + b'\00').decode('utf-16'),
    'r': lambda x: tuple(parse(io.BytesIO(x))),
    's': lambda x: struct.unpack('>H', x)[0],
    't': lambda x: (x[1:] + b'\00').decode('utf-16'),
    'u': lambda x: struct.unpack('>I', x)[0],
}

FIELDNAMES = {
    # Database
    'vrsn': 'Version',
    'otrk': 'Track',
    'ttyp': 'File Type',
    'pfil': 'File Path',
    'tsng': 'Song Title',
    'tlen': 'Length',
    'tbit': 'Bitrate',
    'tsmp': 'Sample Rate',
    'tbpm': 'BPM',
    'tadd': 'Date added',
    'uadd': 'Date added',
    'tkey': 'Key',
    'bbgl': 'Beatgrid Locked',
    'tart': 'Artist',
    'utme': 'File Time',
    'bmis': 'Missing',
    # Crates
    'osrt': 'Sorting',
    'brev': 'Reverse Order',
    'ovct': 'Column Title',
    'tvcn': 'Column Name',
    'tvcw': 'Column Width',
    'ptrk': 'Track Path',
}


def parse(fp):
    for i, header in enumerate(iter(lambda: fp.read(8), b'')):
        assert len(header) == 8
        name_ascii, length = struct.unpack('>4sI', header)

        name = name_ascii.decode('ascii')
        type_id = name[0]

        # vrsn field has no type_id, but contains text
        if name == 'vrsn':
            type_id = 't'

        data = fp.read(length)
        assert len(data) == length

        try:
            fieldparser = FIELDPARSERS[type_id]
        except KeyError:
            value = data
        else:
            try:
                # It would appear that not all fields are properly decoded `tvfx` and `tart` fail...
                value = fieldparser(data)
            except UnicodeDecodeError:
                value = None

        yield name, length, value
