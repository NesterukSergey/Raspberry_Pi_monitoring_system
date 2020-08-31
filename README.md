# Monitoring system
This project is a monitoring system implemented on Raspberry Pi.  

The system includes:
* Configuring multiple independent pipelines simultaneously 
* Scheduling pipelines
* Collecting data from generic sensors and cameras
* Logging
* Visualising collected data on local web server
* Automated continuation of work after restart if interrupted 

The system can be easily extended to work with various shields and sensors.   


*All CLI commands assume that you are using Linux (Raspbian).*


## System structure
1. `main.py` is the entry point of the program.
2. `start.sh` is used to run the monitoring system.
3. `delete.sh` is used to delete all the collected data. Be careful when using it!
4. `configs/` folder contains all the configurations:
    1. `main.json` includes all other configs. Here we have to specify:
        * `project_name`
        * `logs_dir` - the path to store the logs
        * `data_dir` - the path to store the collected data
        * `cameras_config` - the list of cameras
        * `sensors_config` - the list of sensors
        * `pipelines` - the list of active pipelines
        * `log_level` - the level of logs to save. Read more at `Configuring logging`
        * `board` - the hardware scheme
    2. `cameras.json` includes the list of all cameras. Here for every camera we have to specify: 
        * `id` - camera custom unique name. Should reflect the position of camera.
        * `type` - the type of the camera. Now only RBG digital cameras supported. Future possible options: 3D, multispectral, thermal.
        * `width` and `height` - the desired image size.
        * `focus_skip` - the number of images to skip. Required for some cameras to autofocus. 
    3. `sensors.json` includes the list of all sensors. Here for every sensor:
        *   the key of the dictionary is the unique sensor name.
        * `type` - the type of the sensor. Choose from implemented in `monitoring_system/drivers/sensors/sensor_factory.py`.
        The rest of the parameters depend on the selected sensor type. Usually, you want to specify the `pin`. Make sure to select right pin according to the chosen board.
    4. `boards/` folder contains the options of board schemes. Here we specify: 
        * board name
        * optional description
        * pins naming (bcm, wpi, loc)
        * supported functions for every pin and their correspondence in different naming schemes.
    5. `pipelines/` folder contains all the pipelines. Here you only describe them. To make them actually work, include them to the `configs/main.jsom`.
    Pipeline must include:
        * `name`
        * `run_interval` - the scheduling rule in **cron** notation. Read more in `Configuring pipelines`. 
        * `pipeline` - the list of tasks. Select tasks from `monitoring_system/scheduler/PipelineExecutor.py`. 
        Must include `task_type`. The rest of the parameters depend on the chosen task. 
5. `monitoring_system` folder includes all the utilities to launch the monitoring.
    1. `drivers` includes low-lever operations with hardware:
        1. `camera.py` contains `RGBCameraDriver` that makes and saves images with regular RGB digital cameras.
        2. `sensors/` folder includes:
            * `Board.py` - utilities for board and storage for sensors states.
            * `Sensor.py` - abstract sensor class. Inherit all the other sensors from it. 
            * `sensor_factory.py` - used to create sensors instances.
            * sensors implementations
    2. `logger/` folder contains the utilities to log all the system actions. The logger is included to the `self` of the most hardware-related objects.
    3. `scheduler/` folder includes:
        * `Scheduler.py` that inits all of the pipelines. 
        * `PipelineExecutor.py` that manages the tasks in hte pipelines. If you want to add new tasks, add them here.
    4. `utils/` folder contains common for other modules utils.
6. `streamlit_server/` folder contains files that visualise the collected data on the simple web interface. You only need to use Python for it, no JS required.
    1. `server.py` is the main interface page. See Streamlit documentation to modify it. 
    2. `start_server.sh` is used to launch the visualisation.
    3. If you want the interface to autorefresh the plots, you can also launch `start_autorefresh.sh`. But note that it is an experimental feature! Streamlit doesn't support it! 

Read more about launching at `Launching`.  


## Configuring
You can setup general configs in `configs/main.json`.

### Configuring pipelines
To create new pipeline, add `<pipeline_name>.json` file to `/configs/pipelines` folder.
To activate pipeline, add path to pipeline file to the list *pipelines* in `configs/main.json`.

To setup pipeline running interval, use *run_interval* attribute in `<pipeline_name>.json` 
according to [APScheduler cron documentation](https://apscheduler.readthedocs.io/en/latest/modules/triggers/cron.html).  
For example, to run pipeline every 30 minutes, set *run_interval.minute* to `*/30`.  

To add jobs to a pipeline, add objects with it's description to *pipeline* in `<pipeline_name>.json`.
It must have *task_type* attribute that corresponds to an implemented function in *_get_tasks_executors* method in `monitoring_system/scheduler/PipelineExecutor.py`.

If you want to add new sensor, implement it in `monitoring_system/drivers/sensors`. It must be inherited from Sensor. 

If you want to add new type of task, add it to `monitoring_system/scheduler/PipelineExecutor.py` *_get_tasks_executors* method. 
If your task has to collect new data, you can add `@sensor` decorator, and optionally `@average` decorator.
The parameters from a task in a pipeline are passed to a function as **kwargs, except the `task_type` that is omitted. 


### Configuring logging
To make logs, we use python package *logging*.
This package has different levels of logs. 
To setup the minimum level of logs that you want to log, set *log_level* attribute in `configs/main.json`.  

10 for 'DEBUG'  
20 for 'INFO'  
30 for 'WARNING'  
40 for 'ERROR'  
50 for 'CRITICAL'  

The logs stored in `logs/` folder. There you can find: logs for the main scheduler, and separate logs for each pipeline.
To avoid creating huge log files, all the log files handlers are changed every day. 


### Configuring cameras
For each camera:
1. Unplug USB a camera
2. `ls -ltrh /dev/video*`
3. Plug a USB camera
4. `ls -ltrh /dev/video*`
5. Note new device name. For instance, /dev/video0
6. `sudo udevadm info --query=all --name=/dev/video0` (don't forget to change device number)
7. check  second part of DEVLINKS string. It should look like `/dev/v4l/by-path/platform-3f980000.usb-usb-0:1.4:1.0-video-index0`
8. Write you device name to `/configs/cameras.json`


### Configuring sensors
1. Add your sensors to `configs/sensors.json`.  
    `"naming"` is the pin naming scheme. Can be:  
    * `"loc"` - physical location
    * `"bcm"` - BCM
    * `"wpi"` - wPi (GPIO)
    To see pins state and correspondence: `gpio readall`.  
    To check what pins are in use in your project see `board.txt`.  

2. Add driver to your sensor as a `monitoring_system/drivers/sensors/YouySensor.py` inherits from `Sensor.py`.
Don't forget to implement `Sensor` abstract methods.

3. Add your sensor to `monitoring_system/drivers/sensors/sensor_factory.py`. And don't forget all the imports.

4. Use your sensor in pipeline.

The most stable Raspberry Pi pins (physical locations) are: 11, 12, 13, 15, 16, 18 and 22. Try using them in your project if you don't use external boards.


## Launching
To start monitoring system on reboot, type in CLI:  
`crontab -e`  
and add to the end of file:  
`@reboot Projects/Monitoring/start.sh`  
`@reboot Projects/Monitoring/streamlit_server/start_server.sh`  
`@reboot Projects/Monitoring/streamlit_server/start_autorefresh.sh`  
And save the file:
`ctlr+o ctrl+x` in nano editor.

Make sure to change `Projects/Monitoring` to your project location.


## Data
The collected data is stored in `data/` folder. 
In `images/` subfolder you can find:  
1. `images.csv` file with information about the collected images from all the cameras.
2. folders for each cameras with images.

In `sensors/` subfolder you can find `sensors_measurements.csv` file with all the collected sensors measurements.
The columns in the file are sorted by name alphabetically including separate columns for datetime values.

Note that we record not the exact time of every measurement, but the time when its pipeline started to execute. So, every measurement in a single pipeline run has the same time, which simplifies further data processing. 
It will also match am image timestamp if sensing and imaging tasks are in the same pipeline. 



## Restart monitoring
To delete all the collected data and logs, run `Projects/Monitoring/delete.sh`  
Caution! Use it only if you understand what you are doing!


## Useful Utilities 
### Making Raspbian OS copy
1. `ls -ltrh /dev/sd*`  
2. Plug the SD card  
3. `ls -ltrh /dev/sd*`  
4. Note new device name. For instance, /dev/sdc  
5. `sudo dd if=/dev/sdc | gzip > image.gz`


To restore OS:
1. `sudo gzip -dc image.gz | sudo dd of=/dev/sdc`  


### To monitor pins use:
`watch -n 0.1 gpio readall`  


### Unique device serial number 
can be seen in file `serial_number.txt`.  


### Remote access
to Raspberry Pi recommended via VNC.


### Remote code edit and execution
is possible via Pycharm remote interpreter. 
To configure:
* `ctrl+alt+S`
* Project
* Python Interpreter
* Add -> ssh interpreter

To see Raspberry address in local network for ssh interpreter:
`ifconfig`

