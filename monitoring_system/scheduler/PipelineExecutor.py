import time
from datetime import datetime
from pathlib import Path

from monitoring_system.utils import *
from monitoring_system.drivers import *


def _sensor(func):
    def _wrapper(self, *args, **kwargs):
        try:
            measurements = func(self, *args, **kwargs)
            for measurement in measurements:
                self.sensors_accumulator[measurement] = [measurements[measurement]]

        except Exception as e:
            self.log.warning('sensor ' + kwargs['sensor_name'] + ' disabled')
            self.log.error(e)
            raise e

    return _wrapper


def _average(func):
    def _wrapper(self, *args, **kwargs):
        DEFAULT_REPEATS = 10
        DEFAULT_REPEATINTERVAL = 0.1
        repeats = kwargs['repeats'] if kwargs.get('repeats') else DEFAULT_REPEATS
        repeat_interval = kwargs['repeat_interval'] if kwargs.get('repeat_interval') else DEFAULT_REPEATINTERVAL
        assert repeats > 0
        assert repeat_interval > 0

        tmp = {}
        for i in range(repeats):
            res = func(self, *args, **kwargs)

            if i == 0:
                for k in res:
                    tmp[k] = [res[k]]
            else:
                for k in res:
                    tmp[k].append(res[k])

            time.sleep(repeat_interval)

        result = {}
        for k in tmp:
            result[k] = average(tmp[k])

        return result

    return _wrapper


class PipelineExecutor:
    def __init__(self, logger, pipeline, main_config, pipeline_name, board):
        self.log = logger
        self.pipeline = pipeline
        self.main_config = main_config
        self.pipeline_name = pipeline_name
        self.board = board
        self.tasks_executors = self._get_tasks_executors()
        self.sensors_accumulator = None
        self.measurements_file = Path(self.main_config['data_dir']).joinpath(
            'sensors/' + pipeline_name + '_measurements.csv')
        self.cam_config = read_json(self.main_config['cameras_config'])
        self.datetime_prefix, self.datetime_dict = get_time()
        self.current_imaging_state = 'unset'

    def execute(self):
        pipeline_start = datetime.now()
        self.datetime_prefix, self.datetime_dict = get_time()
        self.sensors_accumulator = self.datetime_dict.copy()

        for task in self.pipeline:
            try:
                params = task.copy()
                del params['task_type']
                self.tasks_executors[task['task_type']](**params)
            except Exception as e:
                self.log.error('Error at task ' + task['task_type'])
                self.log.error(str(e))
                raise e

        self._save_measurements()
        pipeline_execution_time = (datetime.now() - pipeline_start).seconds
        self.log.info('Pipeline executed in ' + str(pipeline_execution_time) + ' seconds')

    def _get_tasks_executors(self):
        return {
            'hello_world': lambda: self.log.debug('Hello world!'),  # Dummy task
            'sleep': self._sleep,
            'switch_state': self._switch_state,
            'get_web_images': self._get_web_images,
            'get_dummy': self._get_dummy,
            'actuator': self._actuating,
            'sensor': self._sensing,
        }

    def _save_measurements(self):
        if not list(self.sensors_accumulator.keys()) == list(self.datetime_dict):
            write_csv(self.sensors_accumulator, self.measurements_file)

    def _sleep(self, interval_seconds):
        self.log.debug('Start sleeping for ' + str(interval_seconds) + 's')
        time.sleep(interval_seconds)
        self.log.debug('Finish sleeping for ' + str(interval_seconds) + 's')

    def _switch_state(self, states_list_path, state_name, is_current_imaging_state):

        if is_current_imaging_state:
            self.current_imaging_state = state_name

        states = read_json(states_list_path)

        for actuator in states[state_name]:

            a = states[state_name][actuator]

            if a['mode'] == 'recovery':

                if actuator in self.main_config['system_state']:
                    cmd = self.main_config['system_state'][actuator]
                else:
                    if a['type'] == 'bool':
                        cmd = 'off'

            else:

                if a['type'] == 'bool':
                    cmd = 'on' if bool(a['value']) else 'off'

                if a['mode'] == 'permanent':
                    self.main_config['system_state'][actuator] = cmd

            self._actuating(
                sensor_name=actuator,
                cmd=cmd,
                params={}
            )

            self.log.info('Switching state to: {}'.format(state_name))

    def _get_web_images(self):
        for c in self.cam_config['web_cams']:
            cam = WebCameraDriver(
                camera_info=c,
                folder=self.main_config['data_dir'],
                log=self.log,
                datetime_prefix=self.datetime_prefix,
                datetime_dict=self.datetime_dict,
                system_state=self.current_imaging_state
            )

            cam.capture()

    def _get_slr_images(self):
        # ToDo: add SLR cameras support
        # Add parameters to SLR cameras constructor
        pass

    def _actuating(self, *args, **kwargs):
        cmd = 'self.board.active_sensors["' + kwargs['sensor_name'] + '"].' + kwargs['cmd'] + '(**' + str(kwargs['params']) + ')'
        exec(cmd)

    @_sensor
    @_average
    def _sensing(self, *args, **kwargs):
        ldict = {
            'board': self.board
        }  # Scope to use exec with local variables
        cmd = 'd = board.active_sensors["' + kwargs['sensor_name'] + '"].' + kwargs['cmd'] + '(**' + str(kwargs['params']) + ')'
        exec(cmd, globals(), ldict)
        d = ldict['d']

        if d is None:
            # We don't raise an error here for smooth running
            error_message = 'No data collected with sensor ' + kwargs['sensor_name']
            self.log.error(error_message)
            return None
        else:
            result = {}
            for k in list(d.keys()):
                result[kwargs['sensor_name'] + '_' + k] = d[k]
            return result

    @_sensor
    @_average
    def _get_dummy(self, *args, **kwargs):
        self.log.debug('Dummy value collected')
        import random
        return random.random() * kwargs['mean'] * 2
