# Multicore Processor Simulation

A digital design and software simulation project demonstrating the architecture and operation of a multicore processor using **Logisim** and **Python/Pygame**.

## Overview

Modern computing systems rely heavily on multicore processors to improve performance, multitasking, and parallel execution. This project explores the fundamental concepts behind multicore processor architecture by designing and simulating a simplified processor from the ground up.

The project consists of two complementary simulations:

* **Hardware-level processor simulation** developed in Logisim
* **Interactive software-based multicore simulation** developed in Python using Pygame

The Logisim implementation demonstrates how individual digital components can be combined to form a functional CPU core and subsequently extended into a multicore processor. The Python simulation provides a visual representation of parallel execution, shared memory, cache behavior, bus arbitration, and processor performance.

## Features

### Logisim Processor

The processor was designed using fundamental digital logic components and includes:

* 8-bit arithmetic unit
* 8-bit logical unit
* Arithmetic Logic Unit (ALU)
* 8 general-purpose 8-bit registers
* Instruction memory
* Data memory
* Program counter
* Instruction register
* Control unit
* CPU datapath
* Status flags
* Two independent processor cores
* Shared instruction memory
* Shared data memory
* Memory access arbitration

### ALU Operations

The ALU supports configurable arithmetic and logical operations using a 4-bit opcode.

Logical operations include:

* AND
* OR
* XOR

The arithmetic unit supports:

* 8-bit binary addition
* Carry-in
* Carry-out
* Overflow detection

The ALU also generates processor status flags:

* **Z** — Zero flag
* **N** — Negative flag
* **V** — Overflow flag
* **C** — Carry flag

## Processor Architecture

The project was developed incrementally, beginning with individual components and eventually integrating them into a complete multicore architecture.

### 1. Logical Unit

The logical unit performs bitwise operations on two 8-bit operands. A multiplexer selects the desired operation according to the function selector.

Supported operations:

| Function | Operation |
| -------- | --------- |
| `00`     | AND       |
| `01`     | OR        |
| `10`     | XOR       |
| `11`     | Reserved  |

### 2. Arithmetic Unit

The arithmetic unit implements an 8-bit ripple-carry adder using eight full adders.

It supports:

* Two 8-bit operands
* Carry-in
* Carry-out
* Overflow detection
* 8-bit sum output

### 3. Arithmetic Logic Unit

The ALU combines the arithmetic and logical units into a single processing component.

It uses multiplexers and opcode-controlled signals to select operands and determine the required operation.

The ALU also generates the processor status flags used during instruction execution.

### 4. Register File

The processor contains eight general-purpose registers:

`R0 – R7`

Each register stores 8 bits.

The register file supports:

* Two simultaneous register reads
* One register write
* 3-bit register selection
* Clock-synchronized writing

### 5. CPU Core

The individual CPU core contains the main components required for instruction execution:

```text
Program Counter
      ↓
Instruction Memory
      ↓
Instruction Register
      ↓
Control Unit
      ↓
Register File
      ↓
ALU
      ↓
Data Memory / Registers
```

The processor follows the basic instruction cycle:

1. Fetch
2. Decode
3. Execute
4. Memory Access
5. Write Back

### 6. Multicore Processor

After completing and testing the single-core processor, the architecture was extended to a two-core processor.

Each core has its own:

* Program counter
* Control unit
* Register file
* ALU
* Internal datapath

The cores share:

* Instruction memory
* Data memory

This allows both cores to execute instructions independently while demonstrating the challenges associated with shared resources.

## Shared Memory and Arbitration

One of the main challenges of the multicore design is controlling access to shared data memory.

If both cores attempt to access shared memory simultaneously, conflicts can occur. To address this, the simulation implements a simple arbitration mechanism using multiplexers and demultiplexers.

A clock-based time-sharing approach is used so that memory access alternates between the two cores.

This provides a simplified demonstration of:

* Shared resource management
* Memory contention
* Synchronization
* Bus arbitration

While suitable for a two-core educational simulation, this approach would not scale efficiently to a large number of processor cores. More advanced systems could use priority-based arbitration, queues, bus locking, or dedicated memory controllers.

## Python Multicore Simulation

The project also includes an interactive multicore processor simulation written in **Python using Pygame**.

The simulation provides a graphical representation of multiple processor cores executing instructions concurrently.

Supported instructions include:

* `LOAD`
* `STORE`
* `ADD`
* `SUB`
* `AND`
* `OR`
* `MOV`

Each simulated core contains:

* Local registers
* Program counter
* Local cache
* Instruction execution logic

The cores communicate with shared global memory through a shared system bus.

### Simulation Features

* Real-time core activity visualization
* Multiple configurable processor cores
* Instruction execution visualization
* Shared memory visualization
* Cache hit/miss simulation
* Shared bus arbitration
* Execution timing
* Core utilization monitoring
* Speedup visualization
* Pause/resume controls
* Adjustable simulation speed

## Technologies Used

* **Logisim** — Digital logic and processor simulation
* **Python** — Software simulation
* **Pygame** — Graphical interface and visualization


## Results

The project successfully demonstrates the transition from individual digital logic components to a functional processor core and finally to a multicore processor architecture.

The Logisim implementation demonstrates the hardware-level organization of a processor, while the Python simulation provides a higher-level visualization of multicore execution and resource sharing.

Together, the two implementations provide an educational view of:

* CPU architecture
* Digital logic design
* Instruction execution
* Parallelism
* Shared memory
* Synchronization
* Bus arbitration
* Cache behavior
* Multicore performance


## Authors

**Hena Šehović**
**Berina Juković**
**Berin Žunić**
Computer Science and Engineering
International University of Sarajevo

## Academic Context

This project was developed as part of a computer architecture course project and was designed for educational purposes to explore the fundamental principles of processor and multicore system design.
