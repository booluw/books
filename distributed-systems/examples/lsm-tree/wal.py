"""Write-ahead log: an append-only file of changes, replayed after a crash.

Every put or delete is appended here *before* it goes into the in-memory
memtable. If the process dies, the memtable is lost but the log is not, so
reopening the tree replays the log and rebuilds the memtable.

Record layout (big-endian)::

    crc32 (4 bytes) | key length (4) | value length (4, signed; -1 = tombstone) | key | value

The CRC (cyclic redundancy check) covers everything after it. A crash in
the middle of an append leaves a **torn** final record: too short, or with a
CRC that does not match. Replay stops at the first such record, which is
safe because a torn record was never acknowledged to the caller.
"""

from __future__ import annotations

import os
import struct
import zlib

HEADER = struct.Struct(">IIi")
TOMBSTONE_LEN = -1


def encode_record(key: bytes, value: bytes | None) -> bytes:
    vlen = TOMBSTONE_LEN if value is None else len(value)
    body = struct.pack(">Ii", len(key), vlen) + key + (value or b"")
    return struct.pack(">I", zlib.crc32(body)) + body


class WriteAheadLog:
    def __init__(self, path: str, sync: bool = False):
        self.path = path
        self.sync = sync                 # fsync every record: durable but slow
        self.file = open(path, "ab")
        self.bytes_written = 0

    def append(self, key: bytes, value: bytes | None) -> None:
        record = encode_record(key, value)
        self.file.write(record)
        self.file.flush()                # hand it to the operating system
        if self.sync:
            os.fsync(self.file.fileno())  # and make the OS put it on disk
        self.bytes_written += len(record)

    def reset(self) -> None:
        """Start an empty log (called once the memtable is safely in an SSTable)."""
        self.file.close()
        self.file = open(self.path, "wb")

    def close(self) -> None:
        self.file.close()

    @staticmethod
    def replay(path: str):
        """Yield (key, value-or-None) for every intact record, in order."""
        if not os.path.exists(path):
            return
        with open(path, "rb") as f:
            data = f.read()
        pos = 0
        while pos + HEADER.size <= len(data):
            crc, klen, vlen = HEADER.unpack_from(data, pos)
            body_len = 8 + klen + max(vlen, 0)
            end = pos + 4 + body_len
            if end > len(data) or zlib.crc32(data[pos + 4:end]) != crc:
                return                   # torn or corrupt tail: stop here
            key_start = pos + HEADER.size
            key = data[key_start:key_start + klen]
            value = None if vlen == TOMBSTONE_LEN else data[key_start + klen:end]
            yield key, value
            pos = end
