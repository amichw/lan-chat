# P2P Chat + File Transfer

A single-file, serverless, peer-to-peer chat and file transfer app that works entirely over a shared Wi-Fi network — no internet required.

## How It Works

Connection is bootstrapped via a two-step QR code handshake:

1. **Host** opens `chat.html` → taps **Create Session** → a QR code appears
2. **Joiner** opens `chat.html` → taps **Join Session** → scans the host QR → an answer QR appears
3. **Host** taps **Scan Answer QR** → scans the joiner's QR → connection established
4. Both sides can now chat and send files

WebRTC DataChannels carry all traffic directly between devices (DTLS-encrypted). No data ever leaves the local network.

## Features

- **Text chat** — real-time messaging both ways
- **File transfer** — send any file; receiver gets a download link on completion
- **Persistent identity** — username and device ID stored in `localStorage`, survives reloads
- **No server, no build step** — open `chat.html` directly in a browser

## Usage

### Option A — Open directly
```
file:///path/to/chat.html
```
> Note: camera access (`getUserMedia`) requires either `localhost` or HTTPS in most browsers.

### Option B — Serve over local network (recommended for phones)
```bash
# Python 3
python3 -m http.server 8080

# Then open on each phone:
# http://<your-computer-ip>:8080/chat.html
```

Or use any static file server (Node's `serve`, `caddy`, nginx, etc.).

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
chat.html    # Everything — HTML, CSS, JS in one file
README.md
```
