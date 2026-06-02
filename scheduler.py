from collections import deque
import re

gantt_chart = []
waiting_queue = deque()
def execute_process(process, time, quantum, processes, ready_queue, allocation, available, request, RR_flag):
    sequence = process['sequence']

    tokens = re.findall(r'(\w+\{[^}]*\})', sequence)  # Extract tokens like CPU{...} or IO{...}
    updated_tokens = []
    actual_execution = 0
    requestFlag = 0

    for token in tokens:
        if token.startswith('CPU{'):  # Handle CPU tokens
            CPUtokens = token[4:-1].split(', ')  # Extract individual parts inside CPU{}
            remaining_burst = -1
            for CPUtoken in CPUtokens:
                if CPUtoken.startswith('R['):  # Resource request
                    resourceType = int(CPUtoken[2:-1])
                    request[process['pid']][resourceType] += 1
                    print(f"Time {time}: Process {process['pid']} requesting resource {resourceType}.")

                    if available[resourceType] > 0:
                        available[resourceType] -= 1
                        allocation[process['pid']][resourceType] += 1
                        request[process['pid']][resourceType] -= 1
                        print(f"Resource {resourceType} allocated to Process {process['pid']} successfully.")
                    elif allocation[process['pid']][resourceType] == 1:
                        request[process['pid']][resourceType] -= 1
                    else:
                        print(f"Resource {resourceType} not available. Moving Process {process['pid']} to waiting queue.")
                        waiting_queue.append(process)  # Move to waiting queue
                        return time, actual_execution

                    if (len(tokens) == 1 and len(CPUtokens) > 1):  # Case 1
                        updated_tokens.append(f"CPU{{{', '.join(CPUtokens[1:])}}}")
                    elif (len(tokens) >= 1 and len(CPUtokens) == 1):  # Case 2
                        updated_tokens.extend(tokens[tokens.index(token) + 1:])
                    elif len(tokens) > 1 and len(CPUtokens) > 1:  # Case 3
                        updated_tokens.append(f"CPU{{{', '.join(CPUtokens[1:])}}}")
                        updated_tokens.extend(tokens[tokens.index(token) + 1:])
                    CPUtokens = CPUtokens[1:]

                    if (RR_flag == 0) and (CPUtokens[0].isdigit() or CPUtokens[0].startswith('R[')):
                        requestFlag = 1

                elif CPUtoken.startswith('F['):  # Resource release
                    resourceType = int(CPUtoken[2:-1])
                    allocation[process['pid']][resourceType] -= 1
                    available[resourceType] += 1
                    print(f"Time {time}: Process {process['pid']} releasing resource {resourceType}.")

                    if (len(tokens) == 1 and len(CPUtokens) > 1):  # Case 1
                        updated_tokens.append(f"CPU{{{', '.join(CPUtokens[1:])}}}")
                    elif len(tokens) >= 1 and len(CPUtokens) == 1:  # Case 2
                        updated_tokens.extend(tokens[tokens.index(token) + 1:])
                    elif len(tokens) > 1 and len(CPUtokens) > 1:  # Case 3
                        updated_tokens.append(f"CPU{{{', '.join(CPUtokens[1:])}}}")
                        updated_tokens.extend(tokens[tokens.index(token) + 1:])
                    CPUtokens = CPUtokens[1:]
                    check_waiting_queue(waiting_queue, ready_queue, allocation, available, request)


                else:  # CPU burst
                    burst_time = int(CPUtoken)
                    actual_execution = min(burst_time, quantum) if RR_flag else burst_time
                    # Simulate execution time and check for new arrivals
                    for i in range(actual_execution):
                        check_new_arrivals(time + i, processes, ready_queue)
                    time += actual_execution
                    remaining_burst = burst_time - actual_execution

                    # Handle remaining burst
                    if remaining_burst > 0:
                        updated_tokens.clear()
                        CPUtokens[CPUtokens.index(CPUtoken)] = str(remaining_burst)
                        if (len(tokens) == 1 and len(CPUtokens) > 1):  # Case 1
                            updated_tokens.append(f"CPU{{{', '.join(CPUtokens[:])}}}")
                        elif len(tokens) >= 1 and len(CPUtokens) == 1:  # Case 2
                            tokens[tokens.index(token)] = str(remaining_burst)
                            updated_tokens.append(f"CPU{{{', '.join(tokens[:])}}}")
                        elif len(tokens) > 1 and len(CPUtokens) > 1:  # Case 3
                            updated_tokens.append(f"CPU{{{', '.join(CPUtokens[1:])}}}")
                            tokens[tokens.index(token)] = str(remaining_burst)
                            updated_tokens.append(f"CPU{{{', '.join(tokens[:])}}}")
                    break

            # Correcting these cases
            if remaining_burst == 0 or remaining_burst == -1:
                updated_tokens.clear()
                if (len(tokens) == 1 and len(CPUtokens) > 1):  # Case 1
                    updated_tokens.append(f"CPU{{{', '.join(CPUtokens[1:])}}}")
                elif len(tokens) >= 1 and len(CPUtokens) == 1:  # Case 2
                    updated_tokens.extend(tokens[tokens.index(token) + 1:])
                elif len(tokens) > 1 and len(CPUtokens) > 1:  # Case 3
                    updated_tokens.append(f"CPU{{{', '.join(CPUtokens[1:])}}}")
                    updated_tokens.extend(tokens[tokens.index(token) + 1:])

            break  # Exit after processing one main token
        elif token.startswith('IO{'):  # Handle IO tokens
            io_time = int(token[3:-1])
            process['io_finish_time'] = time + io_time
            print(f"Time {time}: Process {process['pid']} enters I/O, finish time set to {process['io_finish_time']}.")
            updated_tokens.extend(tokens[tokens.index(token) + 1:])
            break  # Exit after processing one IO token

    # Update the process sequence
    process['sequence'] = ' '.join(updated_tokens).strip()

    #if process['sequence']:
        #print(f"Updated sequence for Process {process['pid']}: {process['sequence']}")

    if process['sequence'].startswith('CPU{F[') or requestFlag == 1:
        if requestFlag == 1 and process in waiting_queue:
            print(f"Process {process['pid']} is waiting for resources. Skipping execution.")
            return time, actual_execution  # Avoid recursive call if the process is in the waiting queue
        return execute_process(process, time, quantum, processes, ready_queue, allocation, available, request,RR_flag)

    return time, actual_execution

def check_waiting_queue(waiting_queue, ready_queue, allocation, available, request):
    """Check if resources are now available for processes in the waiting queue."""
    to_remove = []
    for process in list(waiting_queue):
        process_id = process['pid']
        can_allocate = True
        for resourceType, count in enumerate(request[process_id]):
            if count > 0 and available[resourceType] < count:
                can_allocate = False
                break

        if can_allocate:
            print(f"Resources now available for Process {process_id}. Moving to ready queue.")
            for resourceType, count in enumerate(request[process_id]):
                if count > 0:
                    allocation[process_id][resourceType] += count
                    available[resourceType] -= count
                    request[process_id][resourceType] = 0
            waiting_queue.remove(process)
            ready_queue.append(process)

def check_io_completion(time, io_queue, ready_queue):
    for process in list(io_queue):
        if 'io_finish_time' in process and time >= process['io_finish_time']:
            print(f"Time {time}: Process {process['pid']} completed I/O and re-entered the ready queue.")
            del process['io_finish_time'] # Remove the key after completion
            io_queue.remove(process)
            process['ready_queue_enter_time'] = time
            ready_queue.append(process)

def check_new_arrivals(time, processes, ready_queue):
    for process in list(processes):
        if process['arrivalTime'] <= time:
            process['ready_queue_enter_time'] = time
            ready_queue.append(process)
            processes.remove(process)
            print(f"Time {time}: Process {process['pid']} added to ready queue (arrival).")

def select_next_process(ready_queue):
    ready_queue.sort(key=lambda p: p['priority'])
    # Check for processes with the same priority
    highest_priority = ready_queue[0]['priority']
    same_priority_processes = []
    for p in ready_queue:
        if p['priority'] == highest_priority:
            same_priority_processes.append(p)

    if len(same_priority_processes) > 1:
        return 1, ready_queue.pop(0)
    else:
        return 0, ready_queue.pop(0)

def simulate(processes, quantum, allocation, available, request):
    time = 0
    ready_queue = []
    io_queue = deque()
    gantt_chart = []  # To track CPU activity
    wait_times = {process['pid']: 0 for process in processes}
    start_times = {process['pid']: None for process in processes}
    end_times = {process['pid']: None for process in processes}
    burst_times = {process['pid']: 0 for process in processes}
    last_execution_time = 0

    # Record total burst times
    for process in processes:
        valid_cpu_times = []
        if 'CPU{' in process['sequence']:
            cpu_content = process['sequence'][4:-1].split(', ')
            for part in cpu_content:
                if part.isdigit():
                    valid_cpu_times.append(int(part))
        burst_times[process['pid']] = sum(valid_cpu_times)

    while processes or ready_queue or io_queue or waiting_queue:
        check_new_arrivals(time, processes, ready_queue)
        deadlock_process = deadlock_detect(processes, allocation, available, request, ready_queue, time)

        if ready_queue:
            RR_flag, current_process = select_next_process(ready_queue)
            print(f"Time {time}: Executing Process {current_process['pid']} with priority {current_process['priority']}")

            if start_times[current_process['pid']] is None:
                start_times[current_process['pid']] = time

            # Update waiting time for the process
            wait_times[current_process['pid']] += time - current_process['ready_queue_enter_time']

            # Handle idle time before executing a process
            if time > last_execution_time:
                if len(gantt_chart) > 0 and gantt_chart[-1][0] == 'Idle':
                    gantt_chart[-1] = ('Idle', gantt_chart[-1][1], time)
                else:
                    gantt_chart.append(('Idle', last_execution_time, time))

            # Execute the current process
            previous_time = time
            time, executed_time = execute_process(current_process, time, quantum, processes, ready_queue, allocation, available, request, RR_flag)
            last_execution_time = time

            # Add execution to the Gantt chart
            if previous_time != time:  # Only add if start and end times are different
                gantt_chart.append((current_process['pid'], previous_time, time))

            if executed_time > 0:
                # Handle remaining sequence
                if current_process['sequence']:
                    if current_process['sequence'].startswith('IO'):
                        check_new_arrivals(time, processes, ready_queue)
                        time, executed_time = execute_process(current_process, time, quantum, processes, ready_queue,
                                                              allocation, available, request, RR_flag)
                        io_queue.append(current_process)
                        print(f"Time {time}: Process {current_process['pid']} has an I/O burst remaining and is waiting in I/O queue.")
                    else:
                        current_process['ready_queue_enter_time'] = time
                        ready_queue.append(current_process)
                else:
                    end_times[current_process['pid']] = time
                    print(f"Time {time}: Process {current_process['pid']} completed its execution and is finished.")
        else:
            # Handle idle time
            if len(gantt_chart) > 0 and gantt_chart[-1][0] == 'Idle':
                gantt_chart[-1] = ('Idle', gantt_chart[-1][1], time + 1)
            else:
                gantt_chart.append(('Idle', time, time + 1))
            last_execution_time = time
            check_new_arrivals(time, processes, ready_queue)
            time += 1

        # Check for IO completion
        check_io_completion(time, io_queue, ready_queue)

    print(f"Simulation complete. All processes executed by time {time}.")

    # Turnaround time calculation using Gantt chart
    turnaround_times = {}
    first_occurrence = {}
    last_occurrence = {}

    for entry in gantt_chart:
        pid, start, end = entry
        if pid != 'Idle':
            if pid not in first_occurrence:
                first_occurrence[pid] = start
            last_occurrence[pid] = end

    for pid in first_occurrence:
        turnaround_times[pid] = last_occurrence[pid] - first_occurrence[pid]

    # Average calculations
    avg_waiting_time = sum(wait_times.values()) / len(wait_times) if wait_times else 0
    avg_turnaround_time = sum(turnaround_times.values()) / len(turnaround_times) if turnaround_times else 0

    # Print Gantt chart
    print("\nGantt Chart:")
    for entry in gantt_chart:
        if entry[0] == 'Idle':
            print(f"CPU idle from time {entry[1]} to {entry[2]}")
        else:
            print(f"Process {entry[0]} executed from {entry[1]} to {entry[2]}")

    # Print results
    '''
    print("\nSummary:")
    print(f"{'PID':<5} {'Turnaround Time':<18}")
    for pid in sorted(turnaround_times.keys()):
        print(f"{pid:<5} {turnaround_times[pid]:<18}")
    '''

    print(f"\nAverage Waiting Time: {avg_waiting_time:.2f}")
    print(f"Average Turnaround Time: {avg_turnaround_time:.2f}")

def initialization(process_count, resource_count):
    allocation = [[0] * resource_count for _ in range(process_count)]
    request = [[0] * resource_count for _ in range(process_count)]
    available = [1] * resource_count  # Assuming each resource has 1 instance
    return allocation, available, request
def read_file(filename):
    processes = []
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            parts = line.split(" ")
            if len(parts) < 4:
                print("Error: invalid file format")
            pid = int(parts[0])
            arrivalTime = int(parts[1])
            priority = int(parts[2])
            sequence = " ".join(parts[3:])
            process = {'pid': pid, 'arrivalTime': arrivalTime, 'priority': priority, 'sequence': sequence}
            processes.append(process)
    return processes

def deadlock_detect(processes, allocation, available, request, ready_queue, time):
    # Number of processes and resources
    numberOfProcesses = len(allocation)
    numberOfRecourses = len(available)
    # List to store indices of deadlocked processes
    list_deadlocked = []
    # Work vector to keep track of available resources (copy of available)
    work = available[:]
    # List to store the safe sequence of processes
    list_safe = []
    finish = [False] * numberOfProcesses  # Finish array to indicate if a process can finish

    # Mark processes with zero allocation as finished
    for i in range(numberOfProcesses):
        if all(x == 0 for x in allocation[i]):
            finish[i] = True
    # Variable to indicate if a process was found in the current iteration
    found = True

    # Loop to find processes that can complete
    while found:
        found = False  # Assume no process can complete
        for i in range(numberOfProcesses):
            # Check if the process can complete
            if not finish[i] and all(request[i][j] <= work[j] for j in range(numberOfRecourses)):
                # Simulate it finishing by adding its allocation to work
                work = [work[j] + allocation[i][j] for j in range(numberOfRecourses)]
                finish[i] = True
                list_safe.append(i)
                found = True

    # Identify deadlocked processes
    for i in range(numberOfProcesses):
        if not finish[i]:
            list_deadlocked.append(i)
    # Output the result
    if list_deadlocked:
        print("Deadlock processes: ", list_deadlocked)
        print(f"Time: {time} Deadlock detected! Terminating process {list_deadlocked[0]} for recovery.")
        terminated_process = list_deadlocked[0]

        # Recover resources by adding the resources held by the terminated process to the available pool
        available = [available[j] + allocation[terminated_process][j] for j in range(len(available))]
        allocation[terminated_process] = [0] * len(available)
        request[terminated_process] = [0] * len(available)

        terminated_process_info = None
        for i, process in enumerate(waiting_queue):
            if process['pid'] == terminated_process:
                terminated_process_info = process
                waiting_queue.remove(process)  # Remove the process from the deque
                break
        print(f"Terminated process {terminated_process_info['pid']} removed from the waiting queue for recovery.")

        # Recover the original sequence from the file
        original_sequence = recover_sequence_from_file(terminated_process_info['pid'])
        if original_sequence:
            terminated_process_info['sequence'] = original_sequence
        # Re-enter the terminated process into the ready queue
        terminated_process_info['ready_queue_enter_time'] = time
        print(f"Terminated process {terminated_process_info['pid']} re-entered the ready queue.")

        check_waiting_queue(waiting_queue, ready_queue, allocation, available, request)
        ready_queue.append(terminated_process_info)

        return terminated_process_info

    return None
def recover_sequence_from_file(process_id):
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            parts = line.split(" ")
            pid = int(parts[0])
            if pid == process_id:
                # Extract and return the sequence from the matching line
                sequence = " ".join(re.findall(r'(\w+\{[^}]*\})', line))
                return sequence
    return None  # Return None if the process ID is not found

# Main Execution
filename = "input.txt"
processes = read_file(filename)
quantum = 5
resourses = 10
allocation=[]
available=[]
request=[]
allocation, available, request = initialization(len(processes), resourses)
simulate(processes, quantum, allocation, available, request)

