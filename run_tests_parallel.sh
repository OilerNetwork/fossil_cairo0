#!/bin/bash

run_test () {
   tox -- -x -v -s "tests/${$1}"
}

trap "kill $(jobs -p); echo tests manually interrupted" SIGINT SIGTERM

for file in ./tests/*.py
do
  tox -- -x -v -s "$file" &
done