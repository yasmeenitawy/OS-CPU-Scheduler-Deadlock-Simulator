# CPU Scheduling Simulator with Deadlock Detection & Recovery

A comprehensive simulation of a CPU scheduling system that implements priority-based scheduling with round-robin, deadlock detection, and automatic recovery mechanisms.

## Project Overview

This project simulates an operating system's CPU scheduler that manages process execution, resource allocation, and deadlock handling. The system demonstrates real-world OS concepts including:

- **CPU Scheduling**: Priority-based scheduling with round-robin (RR) for processes with equal priority
- **Resource Management**: Handles multiple resource types with allocation and release operations
- **Deadlock Detection**: Implements a deadlock detection algorithm to identify circular wait conditions
- **Deadlock Recovery**: Automatically terminates deadlocked processes and reallocates their resources
- **I/O Simulation**: Manages I/O operations without blocking other processes
- **Performance Metrics**: Calculates average waiting time and turnaround time

## Features

 **Priority Scheduling Algorithm** - Processes execute based on priority levels  
 **Round-Robin Support** - Equal priority processes share CPU time with configurable quantum  
 **Resource Request/Release** - Processes can request and release system resources  
 **Deadlock Detection** - Uses Banker's Algorithm approach to detect deadlock states  
 **Automatic Recovery** - Terminates deadlocked processes and reallocates resources  
 **I/O Queue Management** - Handles simultaneous I/O operations  
 **Gantt Chart Generation** - Visual timeline of process execution  
 **Performance Metrics** - Reports waiting time and turnaround time statistics  

## Requirements

- Python 3.6 or higher

## Input Format Explanation

### Process Structure
- **PID**: Unique process identifier (integer)
- **Arrival Time**: When the process enters the system (integer)
- **Priority**: Scheduling priority (lower numbers = higher priority)
- **Sequence**: Pattern of CPU bursts, I/O operations, and resource operations

### Sequence Notation

| Notation | Meaning | Example |
|----------|---------|---------|
| `CPU{...}` | CPU burst with operations | `CPU{10}` - 10 time units |
| `IO{n}` | I/O operation lasting n units | `IO{30}` - 30 time units |
| `R[x]` | Request resource x | `R[1]` - request resource 1 |
| `F[x]` | Release (Free) resource x | `F[1]` - release resource 1 |

### Example: Process Breakdown

```
1 5 1 CPU{20} IO{30} CPU{20, R[2], 30, F[2], 10}
```

- **PID**: 1
- **Arrival Time**: 5 (enters system at time 5)
- **Priority**: 1 (higher priority than 0)
- **Sequence**:
  - CPU burst: 20 time units
  - I/O operation: 30 time units
  - CPU burst: 20 units → request resource 2 → execute 30 units → release resource 2 → execute 10 units

## Algorithm Details

### CPU Scheduling Algorithm

The scheduler implements **Priority Scheduling with Round-Robin**:

1. **Select Process**: Pick highest priority process from ready queue
2. **Check for Tie**: If multiple processes have same priority, apply Round-Robin
3. **Execute**: Run for up to one time quantum (default: 5 units)
4. **Context Switch**: If burst remains, re-queue; if burst completes, process next burst

### Deadlock Detection

The system uses a **Resource Allocation Graph equivalent** algorithm:

1. **Check Resources**: For each process in waiting queue, verify if requested resources are available
2. **Safe State Test**: Attempt to find a safe execution sequence using Banker's Algorithm
3. **Deadlock Identification**: If no safe sequence exists, mark processes as deadlocked
4. **Recovery Action**: Terminate deadlocked process and reallocate its resources

### Recovery Mechanism

Upon deadlock detection:

1. Identify the deadlocked process
2. Terminate the process and reclaim all allocated resources
3. Restore the process to its original sequence (from input file)
4. Re-insert into ready queue for rescheduling
5. Check waiting queue for processes that can now proceed

## Test Cases & Results

### Test Case 1: Resource Contention & Deadlock Detection

**Input:**
```
0 0 0 CPU{R[1], 20, R[2], 4, F[1], F[2]}
1 0 0 CPU{R[2], 6, R[3], 3, F[2], F[3]}
2 0 0 CPU{R[3], 6, R[1], 3, F[1], F[3]}
```

**Results:**
```
Simulation complete. All processes executed by time 62.
Average Waiting Time: 29.67
Average Turnaround Time: 41.67
Deadlock detected at time 32 - Process 0 terminated for recovery
```

**Gantt Chart Output:**
```
Process 0 executed from 0 to 5
Process 1 executed from 5 to 10
Process 2 executed from 10 to 15
Process 0 executed from 15 to 20
... (additional executions)
Process 0 executed from 58 to 62
```

### Test Case 2: I/O Operations & Priority Scheduling

**Input:**
```
0 0 0 CPU{20} IO{30} CPU{10}
1 10 2 CPU{10}
2 11 2 CPU{5}
3 15 1 CPU{5} IO{25} CPU{5}
```

**Results:**
```
Simulation complete. All processes executed by time 65.
Average Waiting Time: 13.50
Average Turnaround Time: 31.25
No deadlock detected
```

**Gantt Chart Output:**
```
Process 0 executed from 0 to 20
Process 3 executed from 20 to 25
Process 1 executed from 25 to 30
Process 2 executed from 30 to 35
Process 1 executed from 35 to 40
CPU idle from time 40 to 50
Process 0 executed from 50 to 60
Process 3 executed from 60 to 65
```

## Configuration

Edit the main execution section to adjust:

```python
filename = "input.txt"        # Input file path
quantum = 5                   # Round-robin time quantum
resources = 10                # Number of resources in system
```

## Output Explanation

### Real-Time Log
Shows each scheduling decision, resource allocation, and deadlock events as simulation progresses.

### Gantt Chart
Visual representation of:
- Which process executed during each time interval
- CPU idle periods
- Total simulation time

### Performance Metrics

- **Average Waiting Time**: Mean time processes spent waiting in ready queue
- **Average Turnaround Time**: Mean time from arrival to completion
- **Deadlock Events**: Details of any detected deadlocks and recovery actions

## Project Structure

```
.
├── scheduler.py          # Main simulation program
├── input.txt            # Sample input file
└── README.md            # This file
```

## Key Functions

| Function | Purpose |
|----------|---------|
| `simulate()` | Main simulation loop managing process execution |
| `execute_process()` | Executes individual process bursts |
| `deadlock_detect()` | Implements deadlock detection algorithm |
| `check_waiting_queue()` | Checks if blocked processes can proceed |
| `check_io_completion()` | Manages I/O queue transitions |
| `select_next_process()` | Selects next process based on priority |

## Error Handling

The simulator handles:
-  Invalid input file format
-  Resource unavailability
-  Circular wait conditions (deadlock)
-  I/O operation completions
-  Process arrival events during execution

## Assumptions

1. **Single CPU Core**: System has only one processor
2. **Resource Instances**: Each resource type has exactly 1 instance
3. **Negligible Context Switching**: Context switch time is ignored
4. **Simultaneous I/O**: Multiple processes can perform I/O concurrently
5. **No Process Preemption**: Processes are not forcibly removed except during deadlock recovery

## Performance Characteristics

- **Time Complexity**: O(n²) per scheduling decision in worst case deadlock detection
- **Space Complexity**: O(n × m) where n = processes, m = resources
- **Scalability**: Tested with up to 10+ processes and multiple resources
