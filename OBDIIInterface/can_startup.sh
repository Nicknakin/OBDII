#!/bin/bash
sudo /sbin/ip link set can0 up type can bitrate 500000
sudo ifconfig can0 up