import random

number_of_cell = int(input("Enter number of cell: "))
list_of_cell = []
for i in range(number_of_cell):
    list_of_cell.append(input("Enter cell type: "))
    
print(list_of_cell)
cells_data = {}
    
for idx, cell_type in enumerate(list_of_cell, start=1):
    cell_key = f"cell_{idx}_{cell_type}"
    
    voltage = 3.2 if cell_type == "lfp" else 3.6
    min_voltage = 2.8 if cell_type == "lfp" else 3.2
    max_voltage = 3.6 if cell_type == "lfp" else 4.0
    current = 0.0
    temp = round(random.uniform(25, 40), 1)
    capacity = round(voltage * current, 2)
    
    cells_data[cell_key] = {
        "voltage": voltage,
        "current": current,
        "temp": temp,
        "capacity": capacity,
        "min_voltage": min_voltage,
        "max_voltage": max_voltage
    }
    
for key, values in cells_data.items():
    print(f"{key}: {values}")

def process_task():
    list_task = []
    task_dict = {}
    
    task_number = int(input("Enter how many tasks are there? "))
    
    for i in range(task_number):
        print(f"\n--- Task {i+1} ---")
        task = input("Input task (1) CC_CV, (2) IDLE, (3) CC_CD: ").upper()
        list_task.append(task)
        
        task_key = f"task_{i+1}"
        task_data = {}
        
        if task == "CC_CV" or task == "CCCV":
            print("Enter CC_CV parameters:")
            cc_input = input("Enter CC value (A) or CP value (W) - specify unit (e.g., '5A' or '10W'): ")
            cv_voltage = float(input("Enter CV voltage (V): "))
            current = float(input("Enter current (A): "))
            capacity = float(input("Enter capacity: "))
            time_seconds = int(input("Enter time in seconds: "))
            
            task_data = {
                "task_type": "CC_CV",
                "cc_cp": cc_input,
                "cv_voltage": cv_voltage,
                "current": current,
                "capacity": capacity,
                "time_seconds": time_seconds
            }
            
        elif task == "IDLE":
            print("Enter IDLE parameters:")
            time_seconds = int(input("Enter time in seconds: "))
            
            task_data = {
                "task_type": "IDLE",
                "time_seconds": time_seconds
            }
            
        elif task == "CC_CD":
            print("Enter CC_CD parameters:")
            cc_input = input("Enter CC value (A) or CP value (W) - specify unit (e.g., '5A' or '10W'): ")
            voltage = float(input("Enter voltage (V): "))
            capacity = float(input("Enter capacity: "))
            time_seconds = int(input("Enter time in seconds: "))
            
            task_data = {
                "task_type": "CC_CD",
                "cc_cp": cc_input,
                "voltage": voltage,
                "capacity": capacity,
                "time_seconds": time_seconds
            }
        else:
            print("Invalid task type entered!")
            task_data = {
                "task_type": "INVALID",
                "error": "Unknown task type"
            }
        
        task_dict[task_key] = task_data
    
    print(f"\nList of tasks: {list_task}")
    print("\n--- Task Dictionary ---")
    for key, values in task_dict.items():
        print(f"{key}: {values}")
    
    return list_task, task_dict

if __name__ == "__main__":
    task_list, tasks_dictionary = process_task()