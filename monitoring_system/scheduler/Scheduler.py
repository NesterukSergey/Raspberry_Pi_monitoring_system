from apscheduler.schedulers.background import BlockingScheduler
import atexit
from pathlib import Path

from monitoring_system.utils import *
from monitoring_system.scheduler.PipelineExecutor import PipelineExecutor
from monitoring_system.logger.Logger import get_logger
from monitoring_system.drivers.sensors.Board import Board


class Scheduler:
    def __init__(self, main_config):
        self.main_config = main_config
        self.main_config['system_state'] = {}

        self.create_dirs()
        self.logger = get_logger(main_config['project_name'],
                                 file=main_config['logs_dir'],
                                 level=main_config['log_level'])
        self.board = None
        self.scheduler = BlockingScheduler(
            logger=self.logger,
            job_defaults={'misfire_grace_time': 45},
        )
        self.setup()
        
        atexit.register(self._exit)

    def create_dirs(self):
        try:
            Path(self.main_config['logs_dir']).mkdir(parents=True, exist_ok=True)
            Path(self.main_config['data_dir']).mkdir(parents=True, exist_ok=True)

            Path(self.main_config['data_dir']).joinpath('sensors/').mkdir(parents=True, exist_ok=True)

            cameras_config = read_json(self.main_config['cameras_config'])
            for web_camera in cameras_config['web_cams']:
                Path(self.main_config['data_dir'])\
                    .joinpath('images/' + str(web_camera['type'] + '_' + str(web_camera['id'])))\
                    .mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print('Error creating file structure!')

    def setup(self):
        try:
            board_scheme = read_json(self.main_config['board'])
            sensors = read_json(self.main_config['sensors_config'])
            board = Board(board_scheme, sensors, self.logger)
            self.board = board
        except Exception as e:
            self.logger.warning('No board specified in config or some error in Board init')
            self.logger.warning(str(e))
            raise UserWarning(str(e))

        for p in self.main_config['pipelines']:
            pipeline = read_json(p)
            pipeline_executor = PipelineExecutor(
                logger=get_logger(self.main_config['project_name'] + '.' + pipeline['name'],
                                  file=self.main_config['logs_dir'],
                                  level=self.main_config['log_level']),
                pipeline=pipeline['pipeline'],
                main_config=self.main_config,
                pipeline_name=pipeline['name'],
                board=self.board
            )

            self.scheduler.add_job(func=(lambda executor=pipeline_executor: executor.execute()),
                                   **pipeline['run_interval'])

    def start(self):
        try:
            self.logger.info(self.main_config['project_name'] + ' started')
            self.scheduler.start()
        except Exception as e:
            self.logger.error('Error starting scheduler!')
            self.logger.error(str(e))

    def _exit(self):
        self.board.exit()
        print('EXITING!!!')
        self.logger.info('System exited normally')
        self.scheduler.shutdown()
