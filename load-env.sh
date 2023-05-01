#!/bin/sh

eval "export $(echo $(cat .env | grep -vE "^#"))"