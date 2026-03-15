# lan-chat

Chat privately with someone nearby — no internet, no accounts, no cloud.

## The idea

You and a friend want to exchange messages or files. No internet connection needed.
One phone creates a Wi-Fi hotspot. Both phones join it. You open a page in your browser
and start chatting. Messages go directly from device to device and never touch a server.

Two ways to connect:

- **Run the server** — easier and more reliable; one person runs a small Python script, the other opens a URL
- **QR scan** — zero setup, no install, but requires camera access

---

## Option A — Run the server (recommended)

One person runs the signaling server. The other just opens a URL — no QR, no camera needed.

The server only handles the initial handshake. Once connected, it's out of the picture.

```bash
python3 server.py
# Prints something like: http://192.168.1.5:8080
```

Share that URL with the other person — text it, show the screen, or scan a QR of it.
Both open it in their browser and connection is automatic.

### Running from a phone (Android)

No laptop? No problem. Run the server directly from your phone.

Install [Termux from F-Droid](https://f-droid.org/packages/com.termux/) (not Google Play — that version is abandoned).

```bash
pkg update && pkg install python git
git clone https://github.com/amichw/lan-chat
cd lan-chat
python3 server.py
```

---

## Option B — QR scan (no server needed)

Both people open `chat.html` directly in a browser.

1. Person A taps **Invite** → a QR code appears on screen
2. Person B taps **Join** → points their camera at Person A's screen
3. Connected — start chatting

> **Camera note:** Browsers block camera access on plain `http://` addresses.
> If the camera doesn't work, use Option A instead — it's easier on phones anyway.

---

## Technical details

### How it works

WebRTC DataChannels carry all traffic directly between devices (DTLS-encrypted end-to-end).
The signaling server (`server.py`) only brokers the initial WebRTC handshake
(offer/answer exchange) and is no longer involved once the connection is established.

### Features

- **Text chat** — real-time messaging both ways
- **File transfer** — send any file; receiver gets a download link on completion
- **Persistent identity** — username and device ID stored in `localStorage`, survives reloads
- **No build step** — single Python file server, single HTML file client

### File transfer

Files are split into **32 KB chunks**, encoded as base64, and sent over the DataChannel.
Back-pressure handling prevents buffer overflow. The receiver reassembles chunks in order
and offers a blob download link when complete.

### Security

- All traffic is **DTLS-encrypted** by WebRTC (transport layer)
- The signaling server sees only WebRTC offer/answer blobs — no message content
- No server-side logging, no accounts, no cloud
- QR payloads are gzip-compressed and base64-encoded (not encrypted at rest)

### Browser support

Any modern browser with WebRTC and `getUserMedia`:

| Browser | Minimum version |
|---------|----------------|
| Chrome / Edge | 80+ |
| Firefox | 78+ |
| Safari / iOS Safari | 14+ |

### Dependencies (loaded from CDN)

| Library | Purpose |
|---------|---------|
| [qrcodejs](https://github.com/davidshimjs/qrcodejs) | Generate QR codes |
| [jsQR](https://github.com/cozmo/jsQR) | Decode QR from camera frames |
| [pako](https://github.com/nodeca/pako) | Compress WebRTC offers to fit in QR codes |

### Project structure

```
chat.html    # Frontend — HTML, CSS, JS in one file (~1600 lines)
server.py    # Signaling server + static file server (stdlib only, no deps)
README.md
```
