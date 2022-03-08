import struct

def calculate_checksum(packet):
    """Calculate the ICMPv6 checksum for a packet.

    :param packet: The packet bytes to checksum.
    :returns: The checksum integer.
    """
    total = 0

    # Add up 16-bit words
    num_words = len(packet) // 2
    for chunk in struct.unpack("!%sH" % num_words, packet[0:num_words * 2]):
        total += chunk

    # Add any left over byte
    if len(packet) % 2:
        total += packet[-1] << 8

    # Fold 32-bits into 16-bits
    total = (total >> 16) + (total & 0xffff)
    total += total >> 16
    return ~total + 0x10000 & 0xffff

def create_packet(s, seq, payload, total_packets):
    checksum = calculate_checksum(payload)
    header = s.pack(seq, checksum, total_packets)
    return (header + payload)

def dessemble_packet(packet):
    header = struct.unpack('!IHH', packet[0:8])
    sequenceNum, checkSum, total_packets, data = header[0], header[1], header[2], packet[8:]
    return sequenceNum, checkSum, total_packets, data
