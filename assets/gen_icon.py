import struct
import zlib
import os


def make_png(size=32):
    width = height = size
    pixels = []
    for y in range(height):
        row = []
        for x in range(width):
            nx = (x / width) * 2 - 1
            ny = (y / height) * 2 - 1
            r, g, b, a = 30, 90, 160, 255
            thickness = 0.18
            left_dist = abs(ny - (-nx - 0.1))
            right_dist = abs(ny - (nx - 0.1))
            in_left = left_dist < thickness and nx < 0.1 and ny > -0.85
            in_right = right_dist < thickness and nx > -0.1 and ny > -0.85
            if (in_left or in_right) and ny < 0.8:
                r, g, b, a = 255, 255, 255, 255
            row.extend([r, g, b, a])
        pixels.append(row)

    def make_chunk(ct, data):
        crc = zlib.crc32(ct + data) & 0xFFFFFFFF
        return struct.pack('>I', len(data)) + ct + data + struct.pack('>I', crc)

    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    raw = b''
    for row in pixels:
        raw += b'\x00' + bytes(row)
    compressed = zlib.compress(raw, 9)

    png = b'\x89PNG\r\n\x1a\n'
    png += make_chunk(b'IHDR', ihdr)
    png += make_chunk(b'IDAT', compressed)
    png += make_chunk(b'IEND', b'')
    return png


sizes = [16, 32, 48, 256]
png_images = {s: make_png(s) for s in sizes}
num_images = len(sizes)
header = struct.pack('<HHH', 0, 1, num_images)
dir_size = 16 * num_images
offset = 6 + dir_size
entries, blobs = [], []
for size in sizes:
    png = png_images[size]
    w = 0 if size == 256 else size
    h = 0 if size == 256 else size
    entries.append(struct.pack('<BBBBHHII', w, h, 0, 0, 1, 32, len(png), offset))
    blobs.append(png)
    offset += len(png)

ico = header + b''.join(entries) + b''.join(blobs)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.ico')
with open(out, 'wb') as f:
    f.write(ico)
print(f'Created {out} ({len(ico)} bytes)')
