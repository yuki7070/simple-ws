# Webのプロトコルの実装
python3でWebのプロトコルを実装する。勉強用
- http
- websocket

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
- rtp
- webrtc
