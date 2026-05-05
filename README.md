# Typing Speed Test

Ung dung Flask nho de kiem tra toc do go. Backend phat mot `typing_state`
kem prompt, frontend gui lai state do khi submit, va server dung state nay de
tinh WPM, accuracy va trang thai hoan thanh.

Repo nay phu hop cho demo, kiem thu noi bo, hoac moi truong da duoc phep danh
gia.

## Tinh nang

- Frontend typing test bang HTML, CSS, JavaScript.
- API `/api/prompt` tra ve prompt va `typing_state`.
- API `/api/typing` nhan `typing_state`, `typed_text`, `duration_seconds`,
  sau do tra ve ket qua typing.
- Endpoint `/health` de kiem tra app dang chay.
- File `render.yaml` va `Procfile` de deploy tren Render.

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
  "typing_state": "<encoded-state>",
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

## Deploy tren Render

1. Day repo len GitHub.
2. Tao Web Service moi tren Render va ket noi repo.
3. Render co the doc `render.yaml`, hoac cau hinh thu cong:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
4. Sau khi deploy, dung URL Render lam target cho kiem thu.

Nen tat/xoa service sau khi test xong.
