"# airdrop_telegram" 

# Script săn 1 số game
- Ocean
- Memefi
- Yescoin(vàng)
==================
1. Cài đặt python/git
https://www.python.org/downloads/
https://www.git-scm.com/download/win

3. Cài đặt thư viện
pip install -r requirements.txt
(1 số máy bị lỗi có thể dùng lệnh python -m pip install -r requirements.txt)

4. Tạo account.xlsx theo template file account-template.xlsx

5.1
Đối với yescoin:
Trong account tạo sheet yescoin gồm 2 cột proxy và token.token có thể lấy bằng gpm return localStorage.getItem("YESCOIN_MINI_APP:UserStore")
Chạy game : python yescoin.py

Đối với timefarm:
Trong account tạo sheet timefarm gồm 2 cột proxy và query.Khi chạy nhập số phút nghỉ giữa các lần chạy.Tool sẽ chạy 1 luồng duy nhất và claim lại dựa vào số phút chạy để tránh spam game

Lưu ý có thể đổi python thành py/python3/py3... tùy vào máy. Thử lệnh nào máy nhận thì dùng


Cách update version game mới nhất
- Mở Git bash Chạy lệnh git pull
- Mở cmd chạy pip install -r requirements.txt
