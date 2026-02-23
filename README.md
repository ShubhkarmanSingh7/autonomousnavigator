#  AutonomousNavigator

**AutonomousNavigator** is a modular ROS2-based framework designed for autonomous robot navigation.  
It integrates **mapping**, **path planning**, and **exploration** modules to enable a robot to navigate autonomously in a simulated or real-world environment.

---

## Overview

This repository provides a foundational navigation stack for autonomous robots built using **ROS2**.  
It includes launch files, configuration parameters, and core Python scripts for mapping, SLAM, and navigation.  
The project is easily extendable and can be used for both **simulation (Gazebo)** and **real robot deployments**.

---

##  Features

-  Modular architecture with separate folders for launch, config, and source code  
-  Integration-ready with ROS2 Navigation2 stack  
-  Support for mapping and SLAM using configurable parameters  
-  Autonomous exploration script for robot pathfinding  
-  Easy configuration via YAML files  
-  Unit testing included for maintainability  

---

##  Project Structure

```
autonomousnavigator/
│
├─ config/                      # Parameter and configuration files
│   ├─ mapper_params_online_async.yaml
│   ├─ nav2_params.yaml
│   └─ sim_params.yaml
│
├─ launch/                      # Launch files for simulation and SLAM
│   ├─ gazebo.launch.py
│   ├─ slam.launch.py
│   └─ start_simulation.launch.py
│
├─ src/autonomousnavigator/     # Main package source code
│   ├─ __init__.py
│   └─ explorer.py              # Exploration logic for navigation
│
├─ test/                        # Test scripts for ROS2 linting and standards
│   ├─ test_copyright.py
│   ├─ test_flake8.py
│   └─ test_pep257.py
│
├─ world/                       # Gazebo world files
│   └─ small_house.world
│
├─ package.xml                  # ROS2 package metadata
├─ setup.cfg                    # Build configuration
├─ setup.py                     # Python setup script
└─ README.md                    # Project documentation
```

---

##  Installation

### 1️ Clone the repository

```bash
git clone https://github.com/ShubhkarmanSingh7/autonomousnavigator.git
cd autonomousnavigator
```

### 2️ Build the package

If you're using a ROS2 workspace:

```bash
colcon build
source install/setup.bash
```

If using Python dependencies separately:

```bash
pip install -r requirements.txt
```

---

##  Usage

###  Run the simulation

```bash
ros2 launch autonomousnavigator start_simulation.launch.py
```

###  Run SLAM for mapping

```bash
ros2 launch autonomousnavigator slam.launch.py
```

###  Run autonomous exploration

```bash
ros2 run autonomousnavigator explorer
```

You can modify the robot and sensor configurations through the YAML files in the `config/` directory.

---

##  Configuration

Typical configuration file (example: `nav2_params.yaml`):

```yaml
planner_server:
  ros__parameters:
    expected_planner_frequency: 10.0
    planner_plugins: ["GridBased"]
    GridBased:
      plugin: "nav2_navfn_planner/NavfnPlanner"
      tolerance: 0.5
```

All parameters for simulation, SLAM, and navigation can be tuned in the `config/` folder.

---

##  Testing

This project includes ROS2 standard tests for:
- Code style (flake8)
- Docstring conventions (PEP257)
- Copyright

Run all tests using:

```bash
colcon test
colcon test-result --verbose
```

---

##  Contributing

Contributions are welcome!  
Follow the steps below to contribute:

1. **Fork** the repository  
2. Create a **feature branch** (`git checkout -b feature-name`)  
3. **Commit** your changes (`git commit -m "Added new feature"`)  
4. **Push** to your branch (`git push origin feature-name`)  
5. Open a **Pull Request**

Please ensure your code is clean, documented, and passes tests.

---

##  License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for full details.

---

###  Future Plans

- Add ROS2 Navigation2 + RViz integration  
- Implement SLAM using RPLIDAR A1M8  
- Integrate camera-based perception for obstacle avoidance  
- Develop path optimization using reinforcement learning  

---

> Developed by [Shubhkarman Singh](https://github.com/ShubhkarmanSingh7)
