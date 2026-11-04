"""Dòng lệnh: python3 -m hoa_don 10000x2 5000x1 --giam 10"""
import argparse
import sys

from .tinh import tong_tien


def doc_dong(chu):
    don_gia, _, so_luong = chu.partition("x")
    return int(don_gia), int(so_luong)


def main(argv=None):
    p = argparse.ArgumentParser(prog="hoa_don")
    p.add_argument("dong", nargs="+", help="<đơn giá>x<số lượng>")
    p.add_argument("--giam", type=int, default=0, help="phần trăm giảm giá")
    a = p.parse_args(argv)
    try:
        print(tong_tien([doc_dong(x) for x in a.dong], a.giam))
    except ValueError as loi:
        print("lỗi: %s" % loi, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
