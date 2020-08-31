import time
import argparse


def rewrite_file(file):
    lines = None
    with open(file, 'r') as f:
        lines = f.readlines()
    f.close()

    reruns = int(lines[-1][2:])
    reruns += 1
    lines[-1] = '# ' + str(reruns)

    with open(file, 'w') as f:
        f.writelines(lines)

    f.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Server autorefresh')
    parser.add_argument(
        '--sec',
        type=int,
        default=60,
        help='interval in seconds (default: 60)'
    )

    server_refresh = parser.parse_args()

    while True:
        rewrite_file('server.py')
        time.sleep(server_refresh.sec)
