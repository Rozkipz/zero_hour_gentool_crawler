import struct
import datetime
from enum import Enum


class Header:
    def __init__(
            self,
            str_magic,
            timestamp_begin,
            timestamp_end,
            num_time_code,
            unknown1=None,
            str_filename=b'',
            date_time=None,
            str_version=b"",
            str_build_date=b"",
            version_minor=None,
            version_major=None,
            magic_hash=None,
            header=None,
            unknown2=None,
            unknown3=None,
            gamespeed=None,
    ):
        self.str_magic = str_magic.decode('ascii')
        self.timestamp_begin = datetime.datetime.fromtimestamp(0) + datetime.timedelta(seconds=timestamp_begin)
        self.timestamp_end = datetime.datetime.fromtimestamp(0) + datetime.timedelta(seconds=timestamp_end)
        self.num_time_code = num_time_code
        self.unknown1 = unknown1
        self.str_filename = str_filename.decode('ascii')
        self.date_time = date_time  # Not sure what to even do with this? Seems to be slightly wrong?
        self.str_version = str_version.decode('ascii')
        self.str_build_date = str_build_date.decode('ascii')
        self.version_minor = version_minor
        self.version_major = version_major
        self.magic_hash = magic_hash
        self.header = [h.decode('ascii') for h in header]
        self.unknown2 = unknown2
        self.unknown3 = unknown3
        self.gamespeed = gamespeed

    def as_dict(self):
        return self.__dict__


def header2dict(names: list, struct_format: str, data: bytes, expect_tuple: bool = False) -> dict:
    """unpack the raw binary into a dict"""
    unpacked_data = struct.unpack(struct_format, data)

    if expect_tuple and len(names) == 1:
        return {names[0]: unpacked_data}

    return dict(zip(names, unpacked_data))


def find_double_zero_termination(data: bytes) -> (bytes, list):
    """The bytes this decodes look like
    `5B 00 56 00 65 00 72 00 73 00 69 00 6F 00 6E 00`
    which translates to `[Version`
    But it has the 00 bytes between the letters
    """
    zero_termed_string, new_data_obj = data.split(b'\x00\x00', 1)
    # print(zero_termed_string)
    new_data_obj = new_data_obj[1:]  # Using split leaves a \x00 that should have be removed, so ignore it.
    zero_termed_string = zero_termed_string.replace(b'\x00', b'')  # Remove the 0 bytes between the letters.

    return zero_termed_string, new_data_obj


def parse_header(replay_bytes: bytes) -> (Header, bytes):
    """ Parse the header part of the replay file.

    https://docs.python.org/3/library/struct.html#format-characters

    Struct doesn't have a way of getting variable length zero terminated strings
    I tried netstruct but couldn't get it working with `s` and `c` formats
    https://github.com/stendec/netstruct/issues/2

    Instead, we split the data on `\x00\x00` and then carry on.
    It means we can't just smack the data into the struct unpacker with a formatted string, but it works.

    Header values courtesy of https://github.com/louisdx/cnc-replayreaders
    # char: one byte, for use in arrays for plain text
    # byte: one byte, used for numeric values
    # uint16_t: unsigned two-byte integer, stored in little-endian order
    # uint32_t: unsigned four-byte integer, stored in little-endian order
    # tb_ch: An unsigned two-byte value used to represent a BMP Unicode codepoint, stored in little-endian order
    # tb_str: null-terminated array of tb_ch's, to be interpreted as raw BMP Unicode codepoints (?)

    Returns:
        Header object containing some info about the battle
        bytes containing the remaining bytes in the replay that represent the body.

    """
    # char             str_magic[6];    6 bytes
    # uint32_t         timestamp_begin; 4 bytes
    # uint32_t         timestamp_end;   4 bytes
    # byte             unknown1[12];    1 byte
    unpacked = header2dict(
        names=["str_magic", "timestamp_begin", "timestamp_end", "num_time_code", "unknown1", "filename"],
        struct_format="<6sIIH12s",
        data=replay_bytes[:28]
    )

    # tb_str           str_filename;    ? bytes
    unpacked["str_filename"], replay_bytes = find_double_zero_termination(replay_bytes[28:])

    # tb_ch            date_time[8];    8 x 2 bytes
    unpacked["date_time"] = struct.unpack("<8H", replay_bytes[:16])

    # tb_str           str_version;     ? bytes
    unpacked["str_version"], replay_bytes = find_double_zero_termination(replay_bytes[16:])

    # tb_str           str_build_date;  ? bytes
    unpacked["str_build_date"], replay_bytes = find_double_zero_termination(replay_bytes)

    # uint16_t         version_minor;   2 bytes
    # uint16_t         version_major;   2 bytes
    unpacked = unpacked | header2dict(
        names=["version_minor", "version_major"],
        struct_format="<HH",
        data=replay_bytes[:4],
    )

    # byte             magic_hash[8]    8 * 1 byte
    unpacked = unpacked | header2dict(
        names=["magic_hash"],
        struct_format="<8B",
        data=replay_bytes[4:12],
        expect_tuple=True
    )

    # char             header[];        ? bytes
    zero_termed_string, replay_bytes = replay_bytes[12:].split(b'\x00', 1)

    unpacked["header"] = zero_termed_string[:-1].split(b';')  # Split the header (except the final `;`) on `;` - we could handle this in the future.

    # uint16_t         unknown2;        2 bytes
    unpacked = unpacked | header2dict(
        names=["unknown2"],
        struct_format="<H",
        data=replay_bytes[:2],
    )

    # uint32_t         unknown3[3];     3 * 4 bytes
    unpacked = unpacked | header2dict(
        names=["unknown3"],
        struct_format="<3I",
        data=replay_bytes[2:14],
        expect_tuple=True
    )

    # uint32_t         gamespeed;       4 bytes
    unpacked = unpacked | header2dict(
        names=["gamespeed"],
        struct_format="<I",
        data=replay_bytes[14:18],
    )
    created_header = Header(**unpacked)

    return created_header, replay_bytes[18:]


def parse_replay_file(data: bytes) -> Header:
    header, pointer = parse_header(data)
    return header


class Chunk:
    def __init__(self, timecode: int = None, chunkcode: int = None, number: int = None, number_of_args: int = None, args: list = None):
        self.timecode: int = timecode
        self.chunkcode: int = chunkcode
        self.number: int = number
        self.number_of_args: int = number_of_args
        self.args: list = args

    def as_dict(self):
        return self.__dict__


class ArgType(Enum):
    """Enum arg types."""
    Integer = 0  # int32 4 bytes
    Float = 1  # float32 4 bytes
    Boolean = 2  # bool 1 byte
    ObjectId = 3  # uint32 4 bytes
    four = 4  # 4 bytes, no idea what it is.
    five = 5  # 0 bytes? No idea again.
    Position = 6  # float32 3 * 12 bytes [x,y,z]
    ScreenPosition = 7  # int32 2 * 8 bytes
    eight = 8  # 16 bytes, no idea what it is.


def read_bytes(arg_type: ArgType, data: bytes):
    if arg_type == ArgType.Boolean:
        return_value = struct.unpack("<B", data[:1])
        data = data[1:]
    elif arg_type in (ArgType.Integer, ArgType.Float, ArgType.ObjectId, ArgType.four):
        return_value = struct.unpack("<I", data[:4])
        data = data[4:]
    elif arg_type == ArgType.ScreenPosition:  # Two floats.
        return_value = struct.unpack("<II", data[:8])
        data = data[8:]
    elif arg_type == ArgType.Position:  # Three floats.
        return_value = struct.unpack("<III", data[:12])
        data = data[12:]
    elif arg_type == ArgType.eight:  # 16 bytes.
        return_value = struct.unpack("<IIII", data[:16])
        data = data[16:]
    else:
        return_value = None

    return return_value, data


def parse_body(data: bytes):
    win = False
    cache = []
    while data:
        unpacked = header2dict(
            names=["timecode", "chunkcode", "number", "number_of_args"],
            struct_format="<IIIB",
            data=data[:13],
        )
        c = Chunk(**unpacked)
        data = data[13:]
        argcount = {}

        for _ in range(unpacked["number_of_args"]):
            arg_type, count = struct.unpack("<BB", data[:2])
            # print(data[:15])
            # print(arg_type, count)
            argcount[ArgType(arg_type)] = count
            data = data[2:]

        chunk_args = {}

        for num, (arg_type, count) in enumerate(argcount.items()):
            arg_values = []

            for each in range(count):
                value, data = read_bytes(arg_type, data)
                arg_values.append(value[0])

            chunk_args[f"arg_{num}"] = {arg_type.name: arg_values}

        c.args = chunk_args

        if c.chunkcode == 1093:
            print(c.as_dict())


with open('your_replay_file.rep', "rb") as f:
    stream = f.read()
    header, body = parse_header(stream)
    print(header.as_dict())
    parse_body(body)
