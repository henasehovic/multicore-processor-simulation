import pygame
import random
import time
import math
from collections import deque

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1200, 800
CORE_SIZE = 120
MEMORY_BLOCKS = 8
BLOCK_SIZE = 70
FONT = pygame.font.SysFont('Arial', 18)
TITLE_FONT = pygame.font.SysFont('Arial', 28, bold=True)
INFO_FONT = pygame.font.SysFont('Arial', 16)
HELP_FONT = pygame.font.SysFont('Arial', 18)

# Colors
WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
LIGHT_GRAY = (240, 240, 240)
DARK_BLUE = (20, 30, 60)
CORE_COLORS = [
    (255, 100, 100),  # Red
    (100, 220, 100),  # Green
    (100, 150, 255),  # Blue
    (255, 220, 100),  # Yellow
    (200, 100, 255),  # Purple
    (100, 220, 220),  # Cyan
]
MEMORY_COLOR = (180, 200, 255)
BUS_COLOR = (150, 150, 180)
CACHE_COLOR = (255, 220, 220)
HIGHLIGHT_COLOR = (255, 255, 150)
HELP_BG = (20, 40, 80)
BG_COLOR = (230, 235, 245)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Interactive Multicore Processor Simulator")

class Core:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.color = CORE_COLORS[id % len(CORE_COLORS)]
        self.cache = {}  # Address: value
        self.current_instruction = "Idle"
        self.registers = [random.randint(0, 99) for _ in range(4)]
        self.pc = 0
        self.active = True
        self.program = self.generate_program()
        self.status = "Ready"
        self.animation_progress = 0
        self.last_accessed_address = None
        self.pulse = 0
        self.pulse_dir = 1
        self.speedup = 1.0
        self.utilization = 0.0
        self.instructions_completed = 0
        self.start_time = time.time()
    
    def generate_program(self):
        """Create a simple program with memory and ALU operations"""
        program = []
        ops = ["LOAD", "STORE", "ADD", "SUB", "AND", "OR", "MOV"]
        for _ in range(20):
            op = random.choice(ops)
            if op in ["LOAD", "STORE"]:
                addr = random.randint(0, MEMORY_BLOCKS-1)
                reg = random.randint(0, 3)
                program.append(f"{op} R{reg} {addr}")
            else:
                reg1 = random.randint(0, 3)
                reg2 = random.randint(0, 3)
                program.append(f"{op} R{reg1} R{reg2}")
        return program
    
    def execute_step(self, memory, bus_available):
        """Execute one instruction step"""
        if self.pc >= len(self.program):
            self.status = "Done"
            self.active = False
            return False
        
        instruction = self.program[self.pc]
        self.current_instruction = instruction
        
        # Memory operations need bus access
        if instruction.startswith(("LOAD", "STORE")):
            if bus_available:
                self.process_memory_operation(memory, instruction)
                self.pc += 1
                self.instructions_completed += 1
                return True  # Used bus
            else:
                self.status = "Waiting for bus"
                return False  # Bus not available
        else:
            # Simulate ALU operation
            self.process_alu_operation(instruction)
            self.pc += 1
            self.instructions_completed += 1
            return False  # Didn't use bus
    
    def process_memory_operation(self, memory, instruction):
        """Process a memory operation (LOAD or STORE)"""
        parts = instruction.split()
        op = parts[0]
        reg = int(parts[1][1:])  # Extract register number
        addr = int(parts[2])
        self.last_accessed_address = addr
        
        if op == "LOAD":
            if addr in self.cache:
                self.status = "Cache Hit!"
                self.registers[reg] = self.cache[addr]
            else:
                self.status = "Cache Miss"
                self.registers[reg] = memory[addr]
                self.cache[addr] = memory[addr]  # Add to cache
        elif op == "STORE":
            memory[addr] = self.registers[reg]
            if addr in self.cache:
                self.cache[addr] = self.registers[reg]
    
    def process_alu_operation(self, instruction):
        """Process an ALU operation"""
        parts = instruction.split()
        op = parts[0]
        reg1 = int(parts[1][1:])
        reg2 = int(parts[2][1:])
        
        if op == "ADD":
            self.registers[reg1] = (self.registers[reg1] + self.registers[reg2]) % 100
        elif op == "SUB":
            self.registers[reg1] = (self.registers[reg1] - self.registers[reg2]) % 100
        elif op == "AND":
            self.registers[reg1] = self.registers[reg1] & self.registers[reg2]
        elif op == "OR":
            self.registers[reg1] = self.registers[reg1] | self.registers[reg2]
        elif op == "MOV":
            self.registers[reg1] = self.registers[reg2]
        
        self.status = "Executing " + op
    
    def update_stats(self, base_time):
        """Update performance statistics"""
        elapsed = time.time() - self.start_time
        if elapsed > 0:
            self.speedup = base_time / elapsed if base_time > 0 else 1.0
            self.utilization = self.instructions_completed / (elapsed * 10)  # Normalized
    
    def update_pulse(self):
        """Update pulsing animation for active cores"""
        if self.active:
            self.pulse += 0.1 * self.pulse_dir
            if self.pulse > 5:
                self.pulse_dir = -1
            elif self.pulse < 0:
                self.pulse_dir = 1

class Simulation:
    def __init__(self):
        self.cores = []
        self.memory = []
        self.bus_available = True
        self.simulation_speed = 1.0
        self.paused = True
        self.show_help = True
        self.show_stats = False
        self.core_count = 4
        self.base_time = 0  # Time taken by single core
        self.history = deque(maxlen=100)  # For performance graphs
        self.initialize_simulation()
    
    def initialize_simulation(self):
        """Initialize simulation components"""
        self.cores = []
        self.memory = [random.randint(1, 99) for _ in range(MEMORY_BLOCKS)]
        
        # Position cores based on count
        cols = min(self.core_count, 4)
        rows = (self.core_count + 3) // 4
        start_x = (WIDTH - cols * (CORE_SIZE + 50)) // 2
        start_y = 150
        
        for i in range(self.core_count):
            col = i % cols
            row = i // cols
            x = start_x + col * (CORE_SIZE + 50)
            y = start_y + row * (CORE_SIZE + 80)
            self.cores.append(Core(i, x, y))
        
        # Reset base time when changing core count
        self.base_time = 0
    
    def update_simulation(self):
        """Update simulation state"""
        if self.paused:
            return
        
        # Process each core
        bus_used = False
        for core in self.cores:
            if core.active:
                used_bus = core.execute_step(self.memory, self.bus_available and not bus_used)
                if used_bus:
                    bus_used = True
                core.update_pulse()
        
        self.bus_available = not bus_used
        
        # Update performance stats
        if len(self.cores) > 0 and self.cores[0].instructions_completed > 0 and self.base_time == 0:
            self.base_time = time.time() - self.cores[0].start_time
        
        for core in self.cores:
            core.update_stats(self.base_time)
        
        # Record history for graphs
        if len(self.cores) > 1 and time.time() % 0.5 < 0.1:  # Sample every ~0.5s
            stats = {
                "time": time.time(),
                "speedups": [core.speedup for core in self.cores],
                "utilizations": [core.utilization for core in self.cores]
            }
            self.history.append(stats)
    
    def draw(self, screen):
        """Draw the simulation"""
        screen.fill(BG_COLOR)
        
        if self.show_help:
            self.draw_help_screen(screen)
        else:
            self.draw_controls(screen)
            self.draw_bus(screen)
            self.draw_memory(screen)
            
            for core in self.cores:
                self.draw_core(screen, core)
            
            if self.show_stats and len(self.cores) > 1:
                self.draw_performance_graphs(screen)
            
            if self.paused:
                self.draw_pause_overlay(screen)
    
    def draw_controls(self, screen):
        """Draw control panel"""
        # Control panel background
        pygame.draw.rect(screen, (240, 245, 255), (20, 20, WIDTH-40, 80), border_radius=15)
        pygame.draw.rect(screen, (180, 190, 220), (20, 20, WIDTH-40, 80), 2, border_radius=15)
        
        # Title
        title = TITLE_FONT.render("Multicore Processor Simulator", True, (40, 60, 120))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))
        
        # Core count selector
        core_text = INFO_FONT.render(f"Cores: {self.core_count}", True, (80, 100, 160))
        screen.blit(core_text, (50, 70))
        pygame.draw.rect(screen, (200, 220, 255), (120, 65, 30, 25), border_radius=5)
        pygame.draw.rect(screen, (100, 140, 220), (120, 65, 30, 25), 1, border_radius=5)
        plus = INFO_FONT.render("+", True, (40, 80, 160))
        screen.blit(plus, (130, 65))
        
        pygame.draw.rect(screen, (200, 220, 255), (160, 65, 30, 25), border_radius=5)
        pygame.draw.rect(screen, (100, 140, 220), (160, 65, 30, 25), 1, border_radius=5)
        minus = INFO_FONT.render("-", True, (40, 80, 160))
        screen.blit(minus, (170, 65))
        
        # Controls
        controls = INFO_FONT.render(
            "SPACE: Pause/Resume  |  UP/DOWN: Speed  |  R: Reset  |  H: Help  |  S: Stats", 
            True, (80, 100, 160))
        screen.blit(controls, (WIDTH//2 - controls.get_width()//2, 70))
        
        # Speed indicator
        speed_bg = pygame.Rect(WIDTH - 150, 30, 100, 30)
        pygame.draw.rect(screen, (200, 220, 255), speed_bg, border_radius=5)
        pygame.draw.rect(screen, (100, 140, 220), speed_bg, 2, border_radius=5)
        speed_text = INFO_FONT.render(f"Speed: {self.simulation_speed:.1f}x", True, (40, 80, 160))
        screen.blit(speed_text, (WIDTH - 145, 35))
    
    def draw_core(self, screen, core):
        """Draw a processor core with all its components"""
        # Core body with pulsing animation
        pulse_offset = math.sin(core.pulse) * 3
        pygame.draw.rect(screen, core.color, 
                        (core.x - pulse_offset, core.y - pulse_offset, 
                         CORE_SIZE + pulse_offset*2, CORE_SIZE + pulse_offset*2), 
                        border_radius=10)
        pygame.draw.rect(screen, BLACK, 
                        (core.x - pulse_offset, core.y - pulse_offset, 
                         CORE_SIZE + pulse_offset*2, CORE_SIZE + pulse_offset*2), 
                        2, border_radius=10)
        
        # Core ID
        id_text = TITLE_FONT.render(f"{core.id}", True, BLACK)
        screen.blit(id_text, (core.x + CORE_SIZE//2 - id_text.get_width()//2, core.y + 10))
        
        # Status
        status_text = FONT.render(core.status, True, BLACK)
        screen.blit(status_text, (core.x + CORE_SIZE//2 - status_text.get_width()//2, core.y + CORE_SIZE + 10))
        
        # Performance info if showing stats
        if self.show_stats:
            perf_text = INFO_FONT.render(f"Speedup: {core.speedup:.2f}x", True, BLACK)
            screen.blit(perf_text, (core.x, core.y + CORE_SIZE + 35))
            
            util_text = INFO_FONT.render(f"Util: {core.utilization:.1f}", True, BLACK)
            screen.blit(util_text, (core.x, core.y + CORE_SIZE + 55))
        
        # Cache visualization
        cache_title = INFO_FONT.render("Cache:", True, BLACK)
        screen.blit(cache_title, (core.x, core.y + CORE_SIZE + (85 if self.show_stats else 35)))
        
        for i, (addr, val) in enumerate(list(core.cache.items())[:4]):
            cache_rect = pygame.Rect(core.x + i*25, core.y + CORE_SIZE + (110 if self.show_stats else 60), 20, 20)
            pygame.draw.rect(screen, CACHE_COLOR, cache_rect, border_radius=3)
            pygame.draw.rect(screen, BLACK, cache_rect, 1, border_radius=3)
            addr_text = INFO_FONT.render(str(addr), True, BLACK)
            screen.blit(addr_text, (core.x + i*25 + 10 - addr_text.get_width()//2, 
                                  core.y + CORE_SIZE + (110 if self.show_stats else 60) + 2))
    
    def draw_memory(self, screen):
        """Draw the shared memory module"""
        # Memory title
        mem_title = TITLE_FONT.render("SHARED MEMORY", True, (30, 50, 100))
        screen.blit(mem_title, (WIDTH//2 - mem_title.get_width()//2, HEIGHT - 200))
        
        # Memory blocks
        for i in range(MEMORY_BLOCKS):
            # Check if any core recently accessed this block
            recently_accessed = any(core.last_accessed_address == i for core in self.cores)
            color = HIGHLIGHT_COLOR if recently_accessed else MEMORY_COLOR
            
            block_rect = pygame.Rect(WIDTH//2 - (MEMORY_BLOCKS*BLOCK_SIZE)//2 + i*BLOCK_SIZE, 
                                    HEIGHT - 150, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(screen, color, block_rect, border_radius=8)
            pygame.draw.rect(screen, BLACK, block_rect, 2, border_radius=8)
            
            # Address label
            addr_text = INFO_FONT.render(f"{i}", True, BLACK)
            screen.blit(addr_text, (block_rect.centerx - addr_text.get_width()//2, HEIGHT - 170))
            
            # Value
            val_text = FONT.render(str(self.memory[i]), True, BLACK)
            screen.blit(val_text, (block_rect.centerx - val_text.get_width()//2, 
                                 block_rect.centery - val_text.get_height()//2))
    
    def draw_bus(self, screen):
        """Draw the system bus"""
        # Bus line
        pygame.draw.rect(screen, BUS_COLOR, (50, HEIGHT - 100, WIDTH-100, 20), border_radius=10)
        pygame.draw.rect(screen, BLACK, (50, HEIGHT - 100, WIDTH-100, 20), 2, border_radius=10)
        
        # Bus activity indicator
        if not self.bus_available:
            pygame.draw.circle(screen, (255, 100, 100), (WIDTH//2, HEIGHT - 90), 8)
    
    def draw_performance_graphs(self, screen):
        """Draw performance comparison graphs"""
        if len(self.history) < 2:
            return
        
        # Graph area background
        graph_bg = pygame.Rect(50, HEIGHT - 350, WIDTH-100, 200)
        pygame.draw.rect(screen, (240, 245, 255), graph_bg, border_radius=10)
        pygame.draw.rect(screen, (180, 190, 220), graph_bg, 2, border_radius=10)
        
        # Title
        title = FONT.render("Performance Comparison", True, (40, 60, 120))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT - 340))
        
        # X-axis (time)
        start_time = self.history[0]["time"]
        end_time = self.history[-1]["time"]
        time_range = end_time - start_time if end_time > start_time else 1
        
        # Y-axis values (speedup)
        max_speedup = max(max(stats["speedups"]) for stats in self.history) or 1
        y_scale = 150 / max(1, max_speedup)
        
        # Draw grid lines
        for i in range(1, math.ceil(max_speedup) + 1):
            y_pos = HEIGHT - 150 - i * y_scale
            pygame.draw.line(screen, (220, 220, 220), (60, y_pos), (WIDTH-60, y_pos), 1)
            speedup_text = INFO_FONT.render(f"{i}x", True, (100, 100, 120))
            screen.blit(speedup_text, (40, y_pos - 10))
        
        # Draw speedup lines for each core
        for core_idx in range(len(self.cores)):
            color = self.cores[core_idx].color
            points = []
            for i, stats in enumerate(self.history):
                if core_idx < len(stats["speedups"]):
                    x = 60 + (WIDTH-120) * (stats["time"] - start_time) / time_range
                    y = HEIGHT - 150 - stats["speedups"][core_idx] * y_scale
                    points.append((x, y))
            
            if len(points) > 1:
                pygame.draw.lines(screen, color, False, points, 2)
        
        # Legend
        legend_y = HEIGHT - 380
        for core_idx, core in enumerate(self.cores[:4]):  # Only show first 4 to avoid clutter
            pygame.draw.rect(screen, core.color, (70 + core_idx * 120, legend_y, 20, 20))
            core_text = INFO_FONT.render(f"Core {core_idx}", True, BLACK)
            screen.blit(core_text, (95 + core_idx * 120, legend_y))
    
    def draw_help_screen(self, screen):
        """Draw the help screen"""
        screen.fill(HELP_BG)
        
        # Title
        title = TITLE_FONT.render("Multicore Processor Simulator", True, (255, 255, 200))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))
        
        # Instructions
        instructions = [
            "This simulation demonstrates how multiple processor cores work together",
            "and share resources like memory and system buses.",
            "",
            "Key Concepts:",
            "- Each core executes its own program independently",
            "- Cores share access to main memory through a bus",
            "- Caches reduce memory access times",
            "- More cores can increase throughput but add complexity",
            "",
            "Controls:",
            "SPACE: Pause/Resume simulation",
            "UP/DOWN: Increase/Decrease speed",
            "+/-: Add/Remove cores",
            "R: Reset simulation",
            "H: Toggle help",
            "S: Toggle performance stats",
            "",
            "Press any key to start..."
        ]
        
        for i, line in enumerate(instructions):
            text = HELP_FONT.render(line, True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, 100 + i * 25))
    
    def draw_pause_overlay(self, screen):
        """Draw pause indicator"""
        pause_bg = pygame.Surface((300, 60), pygame.SRCALPHA)
        pygame.draw.rect(pause_bg, (255, 200, 200, 180), pause_bg.get_rect(), border_radius=20)
        pygame.draw.rect(pause_bg, (200, 100, 100, 200), pause_bg.get_rect(), 3, border_radius=20)
        screen.blit(pause_bg, (WIDTH//2 - 150, HEIGHT//2 - 30))
        
        pause_text = TITLE_FONT.render("PAUSED", True, (200, 0, 0))
        screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 15))

# Main game loop
def main():
    clock = pygame.time.Clock()
    sim = Simulation()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if sim.show_help:
                    # Start simulation when any key is pressed during initial help
                    sim.show_help = False
                    sim.paused = False
                elif event.key == pygame.K_SPACE:
                    sim.paused = not sim.paused
                elif event.key == pygame.K_UP:
                    sim.simulation_speed = min(3.0, sim.simulation_speed + 0.5)
                elif event.key == pygame.K_DOWN:
                    sim.simulation_speed = max(0.5, sim.simulation_speed - 0.5)
                elif event.key == pygame.K_r:
                    sim.initialize_simulation()
                elif event.key == pygame.K_h:
                    sim.show_help = not sim.show_help
                elif event.key == pygame.K_s:
                    sim.show_stats = not sim.show_stats
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    if sim.core_count < 6:
                        sim.core_count += 1
                        sim.initialize_simulation()
                elif event.key == pygame.K_MINUS:
                    if sim.core_count > 1:
                        sim.core_count -= 1
                        sim.initialize_simulation()
        
        # Check for core count button clicks
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        
        if not sim.show_help and mouse_clicked:
            # Check + button
            if 120 <= mouse_pos[0] <= 150 and 65 <= mouse_pos[1] <= 90:
                if sim.core_count < 6:
                    sim.core_count += 1
                    sim.initialize_simulation()
            # Check - button
            elif 160 <= mouse_pos[0] <= 190 and 65 <= mouse_pos[1] <= 90:
                if sim.core_count > 1:
                    sim.core_count -= 1
                    sim.initialize_simulation()
        
        sim.update_simulation()
        sim.draw(screen)
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()

if __name__ == "__main__":
    main()