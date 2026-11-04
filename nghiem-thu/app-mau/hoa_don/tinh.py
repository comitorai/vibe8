"""Tính tiền bằng số nguyên (đồng), không dùng số thực."""


def tong_tien(dong, giam_pt=0):
    """dong: các cặp (đơn giá, số lượng). giam_pt: 0 đến 100. Làm tròn xuống tới đồng."""
    if not 0 <= giam_pt <= 100:
        raise ValueError("giảm giá phải từ 0 đến 100")
    tong = 0
    for don_gia, so_luong in dong:
        if don_gia < 0 or so_luong < 0:
            raise ValueError("đơn giá và số lượng không được âm")
        tong += don_gia * so_luong
    return tong * (100 - giam_pt) // 100
