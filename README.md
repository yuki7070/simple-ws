# Webのプロトコルの実装
python3でWebのプロトコルを実装する。勉強用
- http
- websocket

## HTTP
```
$ python (or python3) http.py
```

## WebSocket
```
$ python (or python3) websocket.py
```
```
ws = new WebSocket('ws://localhost:8000')
ws.send('Hello, World')
ws.onmessage = function () {}
```

## to do
- 非同期処理
- rtp
- webrtc
