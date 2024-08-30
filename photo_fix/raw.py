from pathlib import Path

import rawpy
from PIL import Image, ImageFile

exts = [".nef", ".cr2", ".dng", ".arw"]


class RawPyImageFile(ImageFile.ImageFile):
    format = "RAWPY"
    format_description = "camera raw image"

    def _open(self):
        try:
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
        except Exception:
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
