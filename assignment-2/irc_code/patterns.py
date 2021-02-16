#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021
#
# Distributed under terms of the MIT license.

"""
Description:

"""
import abc


class Publisher:
    def __init__(self):
        self.subscribers = {}

    def add_subscriber(self, k, s):
        self.subscribers[k] = s

    def rm_subscriber(self, k):
        try:
            self.subscribers.pop(k, None)
        except ValueError:
            # not present
            pass

    def notify(self, msg):
        for _, s in self.subscribers.items():
            if hasattr(s, "update"):
                s.update(msg)


class Subscriber:
    @abc.abstractmethod
    def update(self, msg):
        pass
