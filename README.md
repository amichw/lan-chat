# P2P Chat + File Transfer

A single-file, serverless, peer-to-peer chat and file transfer app that works entirely over a shared Wi-Fi network — no internet required.

## How It Works

WebRTC DataChannels carry all traffic directly between devices (DTLS-encrypted).
A lightweight signaling server (`server.py`) exchanges the WebRTC offer/answer so
no QR code scanning is required — just open the URL on each device.

1. Run `python3 server.py` — it prints a LAN URL
2. Open that URL on both devices
3. Connection is established automatically via the signaling server
4. Both sides can now chat and send files; the server is no longer involved

> **QR fallback**: The app also supports a manual two-step QR handshake if you
> prefer to run without the server (open `chat.html` directly in a browser).

## Features

- **Text chat** — real-time messaging both ways
- **File transfer** — send any file; receiver gets a download link on completion
- **Persistent identity** — username and device ID stored in `localStorage`, survives reloads
- **Auto-connect via signaling server** — `server.py` brokers the WebRTC handshake; no QR scanning needed
- **QR fallback** — works without the server by scanning QR codes between devices
- **No build step** — single Python file server, single HTML file client

## Usage

### Option A — Signaling server (recommended)
```bash
python3 server.py
# → Open on both devices: http://192.168.x.x:8080/chat.html
```
Open the printed URL on each device — connection is automatic.

### Option B — Open directly (QR handshake)
```
file:///path/to/chat.html
```
> Camera access (`getUserMedia`) requires `localhost` or HTTPS in most browsers.

### WSL2 / cross-device on the same PC
WSL2 uses a private IP not reachable from the LAN. Two options:

**localtunnel** (easiest):
```bash
# Terminal 1
python3 server.py

# Terminal 2
npx localtunnel --port 8080
# → your url is: https://xxxx.loca.lt
```
Open `https://xxxx.loca.lt/chat.html` on both devices.
The tunnel only carries the tiny signaling payloads; WebRTC traffic stays peer-to-peer.

**netsh portproxy** (no internet required — Admin PowerShell):
```powershell
netsh interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=8080 connectaddress=$(wsl hostname -I)
```
Then use `http://<Windows-IP>:8080/chat.html`.

## Dependencies (loaded from CDN)

| Library | Version | Purpose |
|---------|---------|---------|
| [qrcodejs](https://github.com/davidshimjs/qrcodejs) | 1.0.0 | Generate QR codes |
| [jsQR](https://github.com/cozmo/jsQR) | 1.4.0 | Decode QR from camera frames |
| [pako](https://github.com/nodeca/pako) | 2.1.0 | Compress WebRTC offers to fit in QR codes |

All CDN resources are fetched from `cdnjs.cloudflare.com` / `cdn.jsdelivr.net`.

## Browser Support

Any modern browser with WebRTC and `getUserMedia` support:
- Chrome / Edge 80+
- Firefox 78+
- Safari 14+ (iOS 14+)

## File Transfer Details

- Files are split into **32 KB chunks**, encoded as base64, sent over the DataChannel
- Back-pressure handling prevents DataChannel buffer overflow
- Receiver reassembles chunks in order and offers a blob download link

## Security

- All traffic is **DTLS-encrypted** by WebRTC (transport layer)
- No server-side logging, no accounts, no cloud
- QR payloads are gzip-compressed and base64-encoded (not encrypted at rest)

## Project Structure

```
chat.html    # Frontend — HTML, CSS, JS in one file
server.py    # Signaling server + static file server (stdlib only, no deps)
README.md
```
