from dataclasses import dataclass
import threading
import random
import serial
import serial.tools.list_ports
import struct
import time


@dataclass
class MonaState:
    source: int
    ack_tag: int
    state: int
    world_x: float
    world_y: float
    angle_radians: float
    ir: tuple[int, int, int, int, int]


class MonaUno:
    def __init__(self, port: str | None = None, baud: int = 250000) -> None:
        if port is None:
            devices = serial.tools.list_ports.comports()

            for i in devices:
                # CH340, because we're using a clone Uno not a Genuino
                if i.vid == 0x1A86 and i.pid == 0x7523:
                    port = i.name
                    print(f"Auto selected port {port}")
                    break
            else:
                raise RuntimeError("Unable to locate Arduino Uno (CH340)")

        self.com = serial.Serial(port, baud, timeout=None)
        self.packet_buffer = {}
        self._lock = threading.Lock()

    def _read_framed(self) -> None | bytes:
        with self._lock:
            if not self.com.in_waiting:
                return None
            while self.com.in_waiting:
                sync = self.com.read(1)[0]
                if sync != 0xE0:
                    print(f"WARNING: Babble {sync:02x}")
                    if not self.com.in_waiting:
                        return None
                break

            n = self.com.read(1)[0]
            buffer = bytearray()
            for _ in range(n):
                byte = self.com.read(1)[0]
                if byte == 0xD0:
                    buffer.append(self.com.read(1)[0] + 1)
                else:
                    buffer.append(byte)
            chk = self.com.read(1)[0]

            if chk != (n + sum(buffer)) & 0xff:
                print(f"WARNING: Sum failed on packet")
                return None

            return bytes(buffer)


    def poll_com(self) -> None | MonaState:
        packet = self._read_framed()
        if packet is None:
            return None
        packet = struct.unpack("<BIBfff5h", packet)

        return MonaState(
            packet[0],
            packet[1],
            packet[2],
            packet[3],
            packet[4],
            packet[5],
            packet[6:11],
        )

    def poll_com_for(self, source: int) -> None | MonaState:
        if self.packet_buffer.get(source):
            return self.packet_buffer[source].pop(0)
        while True:
            packet = self.poll_com()
            if packet is None:
                return
            if packet.source == source:
                return packet
            if packet.source not in self.packet_buffer:
                self.packet_buffer[packet.source] = []
            self.packet_buffer[packet.source].append(packet)



class Mona:
    WALL_THRESH = 990  # Woah! So high!! These gummies hit different

    def __init__(self, uno: MonaUno, id_: int) -> None:
        self.uno: MonaUno = uno
        self.id: int = id_

        self._last_tag: int = 0
        self._last_packet: bytes = b""
        self.state: None | MonaState = None

        self.ir_capture = []

        self.allow_when_busy: bool = False

        self._has_poll_thread: bool = False

    def take_ir_capture(self):
        if not self._has_poll_thread:
            raise RuntimeError("take_ir_capture only makes sense when using spawn_poll_thread")
        ir = []
        for _ in range(5):
            ir.append(self.state.ir)
            time.sleep(0.2)
        self.ir_capture = [sum(ir[i]) / 5 for i in range(len(ir))]

    def spawn_poll_thread(self) -> None:
        if self._has_poll_thread:
            return
        self._has_poll_thread = True

        def poll_thread():
            while True:
                self.poll_com()
                time.sleep(10 / 1000)

        threading.Thread(target=poll_thread, daemon=True).start()

    def wait_for_online(self) -> None:
        if not self._has_poll_thread:
            raise RuntimeError("wait_for_online only makes sense when using spawn_poll_thread")
        while self.state is None:
            time.sleep(20 / 1000)

    @property
    def wall_left(self) -> bool:
        if self.state is None:
            return False
        return self.state.ir[0] < self.WALL_THRESH

    @property
    def wall_right(self) -> bool:
        if self.state is None:
            return False
        return self.state.ir[4] < self.WALL_THRESH

    @property
    def wall_front(self) -> bool:
        if self.state is None:
            return False
        return self.state.ir[2] < self.WALL_THRESH

    @property
    def wall_cap_left(self) -> bool:
        if not self.ir_capture:
            return False
        return self.ir_capture[0] < self.WALL_THRESH

    @property
    def wall_cap_right(self) -> bool:
        if not self.ir_capture:
            return False
        return self.ir_capture[4] < self.WALL_THRESH

    @property
    def wall_cap_front(self) -> bool:
        if not self.ir_capture:
            return False
        return self.ir_capture[2] < self.WALL_THRESH

    @property
    def busy(self) -> bool:
        if self.state is None:
            return False
        return self.state.state != 0

    @property
    def _next_tag(self) -> int:
        while True:
            tag = random.randint(0x00000000, 0xffffffff)
            if tag != self._last_tag and tag != 0:
                self._last_tag = tag
                return tag

    def poll_com(self) -> None | MonaState:
        packet = self.uno.poll_com_for(self.id)

        if packet is not None:
            # The lack packet this mona received wasn't what we expect!
            if packet.ack_tag != self._last_tag and self._last_tag != 0:
                self._resend()

            self.state = packet
        return packet

    def _resend(self) -> None:
        print("Warning: Resending", self._last_tag)
        self.uno.com.write(self._last_packet)
        self.uno.com.flush()

    def _busy_check(self) -> None:
        while self.busy:
            time.sleep(0.1)

        if self.allow_when_busy:
            return
        if self.busy:
            raise RuntimeError("Attempted to manipulate Mona while it was busy!!")

    def write_com(self, cmd: int, data: bytes) -> None:
        self._last_packet = (
            bytearray([len(data) + 6 - 1, cmd, self.id])
            + struct.pack("<I", self._next_tag)
            + data
        )
        self.uno.com.write(self._last_packet)
        self.uno.com.flush()

    def move_forward(self, n_tiles: int = 1) -> None:
        self._busy_check()
        self.write_com(2, struct.pack("<HH", n_tiles * 140, 0))

    def move_backward(self, n_tiles: int = 1) -> None:
        self._busy_check()
        self.write_com(3, struct.pack("<HH", n_tiles * 130, 0))

    def move_left(self) -> None:
        self._busy_check()
        self.write_com(2, struct.pack("<HH", 20, 0))
        time.sleep(0.35)
        self.write_com(2, struct.pack("<HH", 130, 270))

    def move_right(self) -> None:
        self._busy_check()
        self.write_com(2, struct.pack("<HH", 20, 0))
        time.sleep(0.35)
        self.write_com(2, struct.pack("<HH", 130, 90))

    def turn_left_90(self) -> None:
        self._busy_check()
        self.write_com(4, struct.pack("<HH", 270, 0))

    def turn_right_90(self) -> None:
        self._busy_check()
        self.write_com(4, struct.pack("<HH", 90, 0))

    def turn_180_and_out(self) -> None:
        if not self._has_poll_thread:
            raise RuntimeError("poll thread required for 180 and out")

        self._busy_check()
        self.write_com(4, struct.pack("<HH", 160, 0))
        time.sleep(0.5)
        while self.busy:
            time.sleep(50 / 1000)
        self.write_com(2, struct.pack("<HH", 90, 0))
        while self.busy:
            time.sleep(50 / 1000)


__all__ = ("MonaUno", "Mona")