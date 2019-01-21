# Webのプロトコルの実装
python3でWebのプロトコルを実装する。勉強用
- http
- websocket

## HTTP
```
$ python (or python3) http.py
```
### 課題
- jsonのresponse
- そもそもめんどくさくてGETの処理しか作ってない
- HTTP/2にも対応する
- QUIQ

## WebSocket
```
$ python (or python3) websocket.py
```
```
ws = new WebSocket('ws://localhost:8000')
ws.send('Hello, World')
ws.onmessage = function () {}
```
### 課題
- 接続中のクライアント全員に送信することしかできていない

## to do
- 非同期処理
- webrtc
  - rtp
  - srtp
  - ice
  - sdp
  - stun/turn
- dtls
- quiq(http/3)
