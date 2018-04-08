"""
    shaper.py
    =========
    
    using tc to limit bandwith
"""
import subprocess
import sys
from config import NETWORK_INTERFACE


class Shaper:

    DEVICE = NETWORK_INTERFACE

    def __init__(self, ignore_nonroot=False):

        # this attribute describes the current limit, 0 means no limit
        self.download_limit = 0

        result = subprocess.run(['sudo', 'whoami'], stdout=subprocess.PIPE)
        username = result.stdout.decode('utf-8').strip()
        print(f'Running shaper as [{username}]')
        if username != 'root':
            print(f'ERROR: Trying to shape traffic as nonroot, logged in as: [{username}]')
            if not ignore_nonroot:
                print('Exiting...')
                sys.exit(1)

        # clean up previously set up rules
        print('Trying to delete ingress filter')
        self.reset_ingress()

    def limit_download(self, amount):
        """

        :param amount: Limits bandwith to {amount} kbit
        :return:
        """
        print(f'limiting to {amount}')
        self.reset_ingress()

        self.download_limit = amount
        subprocess.run(['sudo', 'tc', 'qdisc', 'add', 'dev', self.DEVICE, 'handle', 'ffff:', 'ingress'])
        subprocess.run(['sudo', 'tc', 'filter', 'add', 'dev', self.DEVICE, 'parent', 'ffff:', 'protocol', 'ip', 'prio', '50',
                        'u32', 'match', 'ip', 'src', '0.0.0.0/0', 'police', 'rate', f'{amount}kbit', 'burst', '10k',
                        'drop', 'flowid', ':1'])

    def reset_ingress(self):
        # todo suppress RTNETLINK answers: Invalid argument if qdisc ingress not here
        subprocess.Popen(['sudo', 'tc', 'qdisc', 'del', 'dev', self.DEVICE, 'ingress'])
        self.download_limit = 0

    def __del__(self):
        print('cleaning up traffic shaping rules...')
        # todo cleanup trafficshaping rules


if __name__ == '__main__':
    S = Shaper()
    input('press enter to start limiting')
    S.limit_download(1000)
    input('press enter to reset')
    S.reset_ingress()
