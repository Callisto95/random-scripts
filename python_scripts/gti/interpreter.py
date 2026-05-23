import operator
import re
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from enum import auto, Enum
from math import ceil, log
from pathlib import Path
from typing import Callable


class InvalidLine(Exception):
    def __init__(self, message: str, interpreter: Interpreter):
        super().__init__(f"[{interpreter._cursor}] {message}")


class BadInstruction(Exception):
    def __init__(self, instruction: str, interpreter: Interpreter):
        super().__init__(f"[{interpreter._cursor}] '{instruction}' has invalid call")


class UnknownInstruction(Exception):
    def __init__(self, instruction: str, interpreter: Interpreter):
        super().__init__(f"[{interpreter._cursor}] '{instruction}' is not an instruction")


class NotARegister(Exception):
    def __init__(self, register_name: str, interpreter: Interpreter):
        super().__init__(f"[{interpreter._cursor}] '{register_name}' is not a valid register")


class IndexOutOfBounds(Exception):
    def __init__(self, index: int, max_index: int, interpreter: Interpreter):
        super().__init__(
            f"[{interpreter._cursor}] index out of bounds: is {index}, but must be smaller than {max_index}"
        )


class BadJump(Exception):
    def __init__(self, new_cursor: int, interpreter: Interpreter):
        super().__init__(
            f"[{interpreter._cursor}] jumped to bad line '{new_cursor}' - must be between 0 and "
            f"{len(interpreter._lines)}"
        )


class OffsetType(Enum):
    RELATIVE = auto()
    ABSOLUTE = auto()


@dataclass(frozen=True)
class Offset:
    type: OffsetType
    value: int


MOVE_NORMAL: Offset = Offset(OffsetType.RELATIVE, 1)

Action = Callable[[list[str], "interpreter"], Offset]


def add(parts: list[str], interpreter: Interpreter) -> Offset:
    source1: Register = interpreter.parse_register(parts[0])
    source2: Register = interpreter.parse_register(parts[1])
    dest: Register = interpreter.parse_register(parts[2])
    
    dest.write(source1.read() + source2.read())
    
    return MOVE_NORMAL


def add_immediate(parts: list[str], interpreter: Interpreter) -> Offset:
    source: Register = interpreter.parse_register(parts[0])
    dest: Register = interpreter.parse_register(parts[1])
    const: int = int(parts[2])
    
    dest.write(source.read() + const)
    
    return MOVE_NORMAL


def subtract(parts: list[str], interpreter: Interpreter) -> Offset:
    source1: Register = interpreter.parse_register(parts[0])
    source2: Register = interpreter.parse_register(parts[1])
    dest: Register = interpreter.parse_register(parts[2])
    
    dest.write(source1.read() - source2.read())
    
    return MOVE_NORMAL


def subtract_immediate(parts: list[str], interpreter: Interpreter) -> Offset:
    source: Register = interpreter.parse_register(parts[0])
    dest: Register = interpreter.parse_register(parts[1])
    const: int = int(parts[2])
    
    dest.write(source.read() - const)
    
    return MOVE_NORMAL


def load_from_memory(parts: list[str], interpreter: Interpreter) -> Offset:
    source: Register = interpreter.parse_register(parts[0])
    destination: Register = interpreter.parse_register(parts[1])
    const: int = int(parts[2])
    
    destination.write(interpreter.read_memory(source.read() + const))
    
    return MOVE_NORMAL


def store_to_memory(parts: list[str], interpreter: Interpreter) -> Offset:
    offset: Register = interpreter.parse_register(parts[0])
    source: Register = interpreter.parse_register(parts[1])
    const: int = int(parts[2])
    
    interpreter.write_memory(offset.read() + const, source.read())
    
    return MOVE_NORMAL


def jump(parts: list[str], interpreter: Interpreter) -> Offset:
    destination: int = int(parts[0])
    
    return Offset(
        OffsetType.ABSOLUTE,
        destination
    )


def branch(operation: Callable[[int, int], bool]) -> Action:
    def instruction(parts: list[str], interpreter: Interpreter):
        register1: Register = interpreter.parse_register(parts[0])
        register2: Register = interpreter.parse_register(parts[1])
        const: int = int(parts[2])
        
        if operation(register1.read(), register2.read()):
            return Offset(
                OffsetType.RELATIVE,
                const
            )
        
        return MOVE_NORMAL
    
    return instruction


@dataclass
class Register:
    read: Callable[[], int]
    write: Callable[[int], None]


class Interpreter:
    def __init__(self, registers: int, memory_size: int, constants: list[int], lines: list[str], allow_blanks: bool):
        self._lines: list[str] = lines
        self._cursor = 0
        self._instructions: dict[str, Action] = { }
        self._max_registers: int = registers
        self._registers: list[int] = [0] * (registers + 1)
        self._memory_size: int = memory_size
        self._memory: list[int] = [0] * self._memory_size
        self._memory[0:len(constants)] = constants
        
        self._allow_blanks: bool = allow_blanks
    
    def read_memory(self, index: int) -> int:
        if index >= self._memory_size or index < 0:
            raise IndexOutOfBounds(index, self._memory_size, self)
        return self._memory[index]
    
    def write_memory(self, index: int, value) -> None:
        if index >= self._memory_size or index < 0:
            raise IndexOutOfBounds(index, self._memory_size, self)
        self._memory[index] = value
    
    def read_register(self, index: int) -> int:
        if index == 0:
            return 0
        
        if index > self._max_registers or index < 0:
            raise IndexOutOfBounds(index, self._max_registers - 1, self)
        return self._registers[index]
    
    def write_register(self, index: int, value: int) -> None:
        if index == 0:
            return
        
        if index > self._max_registers or index < 0:
            raise IndexOutOfBounds(index, self._max_registers, self)
        self._registers[index] = value
    
    def add_instruction(self, name: str, required_arguments: int, action: Action) -> bool:
        if name in self._instructions:
            print(f"'{name}' already registered, skipping")
            return False
        
        def instruction(parts: list[str], interpreter: Interpreter) -> Offset:
            if len(parts) != required_arguments:
                raise BadInstruction(name, self)
            
            return action(parts, interpreter)
        
        self._instructions[name] = instruction
        return True
    
    @classmethod
    def create(cls, *args) -> Interpreter:
        instance = cls(*args)
        instance.add_instruction("ADD", 3, add)
        instance.add_instruction("ADDI", 3, add_immediate)
        instance.add_instruction("SUB", 3, subtract)
        instance.add_instruction("SUBI", 3, subtract_immediate)
        instance.add_instruction("LDD", 3, load_from_memory)
        instance.add_instruction("STO", 3, store_to_memory)
        instance.add_instruction("JMP", 1, jump)
        instance.add_instruction("BEQ", 3, branch(operator.eq))
        instance.add_instruction("BNEQ", 3, branch(operator.ne))
        instance.add_instruction("BGT", 3, branch(operator.gt))
        return instance
    
    def parse_register(self, register_name: str) -> Register:
        # ignore trailing , and ;
        match = re.fullmatch(r"R\[(\d+)][,;]?", register_name)
        
        if match is None:
            raise NotARegister(register_name, self)
        
        register_index: int = int(match.group(1))
        
        return Register(
            lambda: self.read_register(register_index),
            lambda value: self.write_register(register_index, value)
        )
    
    def print_state(self) -> None:
        print(
            f"\u001B[0K {str(self._cursor).rjust(ceil(log(len(self._lines), 10)))}: {self._registers} | "
            f"{self._memory} | {"EOF" if self._cursor == len(self._lines) else self._lines[self._cursor]}",
            end="\r"
        )
    
    def run(self, autorun: bool, skip_to_line: int) -> None:
        if skip_to_line >= 0:
            autorun = True
        
        while self._cursor != len(self._lines):
            self.print_state()
            
            if autorun and skip_to_line == self._cursor:
                autorun = False
            
            if not autorun:
                input()
                print("\u001B[A", end="")
            
            current_line: str = self._lines[self._cursor]
            
            if not current_line:
                if not self._allow_blanks:
                    raise InvalidLine("blank lines are not allowed", self)
                
                movement: Offset = MOVE_NORMAL
            else:
                parts: list[str] = current_line.split(" ")
                instruction: str = parts[0]
                
                if instruction not in self._instructions:
                    raise UnknownInstruction(instruction, self)
                
                movement: Offset = self._instructions[instruction](parts[1:], self)
            
            new_cursor: int = self._cursor
            
            match movement.type:
                case OffsetType.RELATIVE:
                    new_cursor += movement.value
                case OffsetType.ABSOLUTE:
                    new_cursor = movement.value
            
            if not (0 <= new_cursor <= len(self._lines)):
                raise BadJump(new_cursor, self)
            
            self._cursor = new_cursor
        
        self.print_state()
        print()


def parse_args() -> Namespace:
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("file", type=Path, help="The file to run")
    parser.add_argument(
        "--registers",
        "-r",
        type=int,
        default=3,
        help="amount of registers (R[0] excluded; available as R[1..n]) [3]"
    )
    parser.add_argument(
        "--memory",
        "-m",
        type=int,
        default=16,
        help="amount of DSp's. Must be bigger than input. [16]"
    )
    parser.add_argument(
        "input",
        type=int,
        nargs="+",
        help="the input of the program (repeatable; available in DSp[0..(n-1)])"
    )
    parser.add_argument("--autorun", action="store_true", help="don't wait for user input before each instruction")
    parser.add_argument(
        "--skip-to",
        dest="skip_to",
        default=-1,
        type=int,
        help="autorun until the specified line is reached"
    )
    parser.add_argument(
        "--allow-blank-lines",
        "-B",
        dest="allow_blanks",
        action="store_true",
        help="Blank lines are not allowed by default. Enable this flag to allow them."
    )
    
    return parser.parse_args()


def main() -> None:
    print("I do not guarantee the correctness of this program. Use it with caution!")
    
    args: Namespace = parse_args()
    
    with open(args.file, "r") as inputFile:
        # just ignore trailing semicolons
        # technically needed, but who cares!
        lines = [line.split(";")[0].strip() for line in inputFile.readlines()]
    
    interpreter: Interpreter = Interpreter.create(args.registers, args.memory, args.input, lines, args.allow_blanks)
    
    interpreter.run(args.autorun, args.skip_to)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print()
        print("The program crashed!")
        print(exc)
