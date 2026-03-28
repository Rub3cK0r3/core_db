#!/usr/bin/env bash 

sudo systemctl daemon-reload
sudo systemctl enable ttrssupdate.service 
sudo systemctl start ttrssupdate.service

# Author : rub3ck0r3
