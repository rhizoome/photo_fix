import magic
import rawpy
from PIL import Image, ImageFile

exts = [".nef", ".cr2", ".dng", ".arw"]

starts = set(
    [
        "XML 1.0 document",
        "JPEG image data",
        "Rich Text Format data",
        "PostScript document text",
        "PNG image data",
        "Netpbm image data",
        "RIFF (little-endian) data",
        "SQLite 3.x database",
        "Adobe Photoshop Image",
        "ASCII text",
        "PDF document",
    ]
)


class RawPyImageFile(ImageFile.ImageFile):
    format = "RAWPY"
    format_description = "camera raw image"

    def _open(self):
        try:
            sig = magic.from_file(self.filename)
            for start in starts:
                if sig.startswith(start):
                    raise TypeError("rawpy can't decode this")
            raw = rawpy.imread(self.fp)
            array = raw.postprocess()

            # size in pixels (width, height)
            self._size = (array.shape[1], array.shape[0])

            # mode setting
            typekey = (1, 1) + array.shape[2:], array.__array_interface__["typestr"]
            try:
                self.mode = Image._fromarray_typemap[typekey][1]
            except KeyError as e:
                raise TypeError("Cannot handle this data type: %s, %s" % typekey) from e

            # TODO extract exif?

            offset = self.fp.tell()
            self.tile = [
                (
                    "RAWPYDEC",
                    (0, 0) + self.size,
                    offset,
                    (
                        array,
                        self.mode,
                    ),
                )
            ]
        except Exception as e:
            raise TypeError("rawpy can't decode this")


class RawPyDecoder(ImageFile.PyDecoder):
    _pulls_fd = True

    def decode(self, buffer):
        (data, mode) = self.args[0], self.args[1]
        raw_decoder = Image._getdecoder(mode, "raw", (mode, data.strides[0]))
        raw_decoder.setimage(self.im)
        return raw_decoder.decode(data)


def register_raw_opener():
    Image.register_open(RawPyImageFile.format, RawPyImageFile)
    Image.register_decoder("RAWPYDEC", RawPyDecoder)
    Image.register_extensions(RawPyImageFile.format, exts)
