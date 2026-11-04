#!/bin/sh
# Script `check` của lõi: đổi tệp này là rủi ro cao (xem cong/rui_ro.py).
set -eu
python3 -m unittest discover -s cong/tests -t .
(cd nghiem-thu/app-mau && sh ./kiem-tra.sh)
python3 nghiem-thu/kiem_cuc_bo.py
