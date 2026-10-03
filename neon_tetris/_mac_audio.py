"""Small, typed Objective-C bridge to macOS's preloaded AVAudioPlayer."""

from contextlib import contextmanager
import ctypes as C
from dataclasses import dataclass


class _ObjC:
    def __init__(self):
        self.foundation = C.CDLL("/System/Library/Frameworks/Foundation.framework/Foundation")
        self.core = C.CDLL("/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation")
        self.core.CFRunLoopRunInMode.argtypes = [C.c_void_p, C.c_double, C.c_uint8]
        self.core.CFRunLoopRunInMode.restype = C.c_int32
        self._run_mode = C.c_void_p.in_dll(self.core, "kCFRunLoopDefaultMode")
        self.audio = C.CDLL("/System/Library/Frameworks/AVFoundation.framework/AVFoundation")
        self.lib = C.CDLL("/usr/lib/libobjc.A.dylib")
        self.lib.objc_getClass.argtypes = [C.c_char_p]
        self.lib.objc_getClass.restype = C.c_void_p
        self.lib.sel_registerName.argtypes = [C.c_char_p]
        self.lib.sel_registerName.restype = C.c_void_p
        self._classes = {}
        self._selectors = {}
        self._calls = {}

    def cls(self, name):
        if name not in self._classes:
            value = self.lib.objc_getClass(name.encode("ascii"))
            if not value:
                raise OSError(f"macOS audio class unavailable: {name}")
            self._classes[name] = value
        return self._classes[name]

    def send(self, receiver, selector, result=C.c_void_p, *arguments):
        if selector not in self._selectors:
            self._selectors[selector] = self.lib.sel_registerName(selector.encode("ascii"))
        signature = (result, *(type(arg) for arg in arguments))
        if signature not in self._calls:
            # objc_msgSend must have a concrete ABI signature, including float arguments.
            self._calls[signature] = C.CFUNCTYPE(result, C.c_void_p, C.c_void_p, *signature[1:])(
                ("objc_msgSend", self.lib))
        return self._calls[signature](receiver, self._selectors[selector], *arguments)

    def poll(self):
        # Curses has no Cocoa event loop; completed players need these callbacks before reuse.
        self.core.CFRunLoopRunInMode(self._run_mode, 0.0, False)

    @contextmanager
    def pool(self):
        pool = self.send(self.send(self.cls("NSAutoreleasePool"), "alloc"), "init")
        try:
            yield
        finally:
            self.send(pool, "drain", None)


@dataclass
class _Voice:
    handle: int
    ready: bool = True
    order: int = 0


class MacPlayer:
    """Two reusable voices per sample; no per-click file reads or subprocesses."""

    def __init__(self, paths):
        self._objc = _ObjC()
        self._voices = {}
        self._order = 0
        try:
            with self._objc.pool():
                for path in dict.fromkeys(paths):
                    data = path.read_bytes()
                    buffer = self._objc.send(self._objc.cls("NSData"), "dataWithBytes:length:",
                                             C.c_void_p, C.c_char_p(data), C.c_size_t(len(data)))
                    if not buffer:
                        raise OSError(f"Cannot allocate keyboard sound: {path.name}")
                    self._voices[path] = []
                    for _ in range(2):
                        self._load(path, buffer)
        except BaseException:
            self.close()
            raise

    def _load(self, path, buffer):
        objc = self._objc
        error = C.c_void_p()
        handle = objc.send(objc.send(objc.cls("AVAudioPlayer"), "alloc"),
                           "initWithData:error:", C.c_void_p,
                           C.c_void_p(buffer), C.pointer(error))
        if not handle:
            description = objc.send(error.value, "localizedDescription")
            message = objc.send(description, "UTF8String", C.c_char_p)
            raise OSError(f"Cannot load {path.name}: {message.decode() if message else 'invalid audio'}")
        self._voices[path].append(_Voice(handle))
        if not objc.send(handle, "prepareToPlay", C.c_bool):
            raise OSError(f"Cannot prepare keyboard sound: {path.name}")

    @property
    def ready(self):
        return bool(self._voices)

    def play(self, path):
        voices = self._voices[path]
        voice = next((v for v in voices if v.ready), min(voices, key=lambda v: v.order))
        with self._objc.pool():
            if not voice.ready:
                self._objc.send(voice.handle, "pause", None)
                self._objc.send(voice.handle, "setCurrentTime:", None, C.c_double(0.0))
            if not self._objc.send(voice.handle, "play", C.c_bool):
                raise OSError(f"Cannot play keyboard sound: {path.name}")
        self._order += 1
        voice.order = self._order
        voice.ready = False

    def tick(self):
        with self._objc.pool():
            self._objc.poll()
            for voices in self._voices.values():
                for voice in voices:
                    if not voice.ready and not self._objc.send(voice.handle, "isPlaying", C.c_bool):
                        # Completion releases preparation; keep idle voices warm for the next key.
                        self._objc.send(voice.handle, "setCurrentTime:", None, C.c_double(0.0))
                        if not self._objc.send(voice.handle, "prepareToPlay", C.c_bool):
                            raise OSError("Cannot reprepare keyboard audio.")
                        voice.ready = True

    def stop(self):
        with self._objc.pool():
            for voices in self._voices.values():
                for voice in voices:
                    self._objc.send(voice.handle, "pause", None)
                    self._objc.send(voice.handle, "setCurrentTime:", None, C.c_double(0.0))

    def close(self):
        if not self._voices:
            return
        with self._objc.pool():
            for voices in self._voices.values():
                for voice in voices:
                    self._objc.send(voice.handle, "stop", None)
                    self._objc.send(voice.handle, "release", None)
        self._voices.clear()
