#! /usr/bin/env python

from os import system
from urllib2 import urlopen
from socket import socket
from sys import argv
from time import asctime
from smtplib import SMTP


def tcp_test(server_info):
    cpos = server_info.find(':')
    try:
        sock = socket()
        sock.connect((server_info[:cpos], int(server_info[cpos + 1:])))
        sock.close
        return True
    except:
        return False


def http_test(server_info):
    try:
        data = urlopen(server_info).read()
        if data:
            return True
    except:
        return False


def server_test(test_type, server_info):
    if test_type.lower() == 'tcp':
        return tcp_test(server_info)
    elif test_type.lower() == 'http':
        return http_test(server_info)

smtp = SMTP('mail.vorwaerts-werbung.de')


def notifyUser(smtp, smtp_user, smtp_password, from_email, to_email, msg):
    smtp.login(smtp_user, smtp_password)
    smtp.sendmail(from_email, to_email, msg.as_string())
    smtp.quit()


class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.current_keys, self.past_keys = [
            set(d.keys()) for d in (current_dict, past_dict)
        ]
        self.intersect = self.current_keys.intersection(self.past_keys)

    def added(self):
        return self.current_keys - self.intersect

    def removed(self):
        return self.past_keys - self.intersect

    def changed(self):
        return set(o for o in self.intersect
                   if self.past_dict[o] != self.current_dict[o])

    def unchanged(self):
        return set(o for o in self.intersect
                   if self.past_dict[o] == self.current_dict[o])
