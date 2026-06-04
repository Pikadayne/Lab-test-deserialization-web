# Deserialization lab — Typing Test (pickle)

Ứng dụng này về mặt chức năng là một "Typing Speed Test" đơn giản,
nhưng thực chất là một lab an ninh chứa lỗ hổng deserialization bằng `pickle`.
Frontend nhận prompt từ server và gửi lại một trường `state` (base64-encoded
pickle) khi submit; server giải mã và dùng `pickle.loads` trực tiếp trên dữ liệu
do client cung cấp.

Tệp chính: [app.py](app.py#L1-L120) — các hàm `serialize_state` và `load_state`
chứa logic serialize/deserialize không an toàn.

Mục tiêu repo
- Làm rõ hành vi của một lỗ hổng deserialization bằng `pickle` trong ứng dụng web.
- Cung cấp môi trường lab để phân tích, chứng minh nguyên lý và thử nghiệm an toàn.

Vấn đề bảo mật (kỹ thuật)
- `serialize_state(prompt)` tạo một dict Python rồi gọi `pickle.dumps` và
  base64-encode kết quả để gửi cho client.
- `load_state(serialized_state)` thực hiện `base64.b64decode(...)` rồi gọi
  `pickle.loads(...)` trên dữ liệu do client gửi trở lại.
- Vì `pickle` có khả năng khôi phục các đối tượng Python và có cơ chế gọi
  hàm khi tái tạo (ví dụ `__reduce__`/`GLOBAL` ops), việc gọi `pickle.loads`
  trên dữ liệu không tin cậy cho phép thực thi mã từ xa trên server.

Attack surface
- Endpoint chịu trách nhiệm: `POST /api/typing` (trường `state` trong JSON hoặc
  form). Xem [app.py](app.py#L40-L80) để thấy nơi `load_state` được gọi.
- Client (hoặc attacker) có thể thay thế giá trị `state` bằng bất kỳ base64
  của một payload pickle tùy ý; server sẽ decode và unpickle nó.
- Ứng dụng kiểm tra kiểu trả về (`isinstance(state, dict)`) để lấy `prompt`,
  nhưng nếu payload trả về một đối tượng khác (ví dụ string) server sẽ
  chuyển `prompt = str(state)` — nghĩa là attacker có thể ảnh hưởng prompt
  hiển thị hoặc, trong trường hợp tấn công, kích hoạt các hành vi độc hại.

Làm thế nào để dùng lab này an toàn (mô tả cao cấp)
- Tạo một payload pickle trên máy local (ví dụ dùng `pickle.dumps(...)`) và
  base64-encode nó, rồi gửi tới `POST /api/typing` dưới trường `state`.
- Nếu payload khi unpickle trả về một dict hợp lệ thì app sẽ đánh giá kết quả
  như bình thường; nếu payload chứa cơ chế thực thi mã thì khi server unpickle
  payload đó, mã sẽ chạy trên máy chủ. (Lưu ý: đây là mô tả kỹ thuật — không
  cung cấp ví dụ mã khai thác trực tiếp trong README này.)

Mục tiêu lab (gợi ý bài tập)
- Nhận biết luồng dữ liệu nào bị deserialize và xác định control points.
- Tạo payload an toàn (ví dụ trả về một dict thay đổi `prompt`) để quan sát
  hành vi server mà không gây hại.
- Thử nghiệm detection: dùng logging hoặc monitor process để xem có thao tác
  bất thường khi payload được unpickle.

Kiểm thử sẵn có
- Có bộ test cơ bản tại [tests/test_typing.py](tests/test_typing.py#L1-L120)
  mô tả cách server tạo và tiêu thụ `state`.

Mitigations (cách sửa để ngăn tấn công thực tế)
- Tuyệt đối không gọi `pickle.loads` trên dữ liệu đầu vào không tin cậy.
- Thay bằng JSON cho các cấu trúc dữ liệu đơn giản (`json.loads`/`json.dumps`).
- Nếu cần giữ trạng thái ký hiệu, dùng token có chữ ký (HMAC) hoặc thư viện
  như `itsdangerous` để sinh/kiểm tra token có chữ ký trước khi giải mã.
- Áp dụng whitelist/schema validation nếu dùng deserialization có cấu trúc
  (ví dụ thư viện serialization an toàn hoặc marshmallow với schema rõ ràng).

Chạy app local
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Mở trình duyệt: `http://127.0.0.1:5000`

Chạy test
```powershell
.\venv\Scripts\python.exe -m pytest -q
```

Ghi chú đạo đức và an toàn
- Repo này dành cho mục đích học tập / kiểm thử có phép trên môi trường cô lập.
- Không triển khai payload khai thác thực tế lên hệ thống production hay máy
  chủ bạn không được phép tấn công.

Nếu bạn muốn, tôi có thể:
- Viết phần hướng dẫn lab chi tiết hơn (các bước an toàn để tạo payload "safe"
  chỉ thay đổi prompt),
- Hoặc vá ứng dụng sang dùng token có chữ ký thay vì pickle (tôi sẽ thay đổi
  `serialize_state`/`load_state`).

## API nhanh

Lay prompt:

```http
GET /api/prompt
```

Submit ket qua typing:

```http
POST /api/typing
Content-Type: application/json

{
  "state": "<encoded-state>",
  "typed_text": "hello world",
  "duration_seconds": 30
}
```

## Chay local tren Windows

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Mo trinh duyet tai:

```text
http://127.0.0.1:5000
```

## Chay test

```powershell
.\venv\Scripts\python.exe -m pytest -q
```

