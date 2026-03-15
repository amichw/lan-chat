# lan-chat

Chat privately with someone nearby — no internet, no accounts, no cloud.

## The idea

You and a friend want to exchange messages or files. No internet connection needed.
One phone creates a Wi-Fi hotspot. Both phones join it. You open a page in your browser
and start chatting. Messages go directly from device to device and never touch a server.

Two ways to connect:

- **QR scan** — zero setup, but requires camera access (needs HTTPS or the server option below)
- **Run the server** — one person runs a small Python script; the other just opens a URL

---

## Option A — QR scan

Both people open `chat.html` in a browser.

1. Person A taps **Invite** → a QR code appears on screen
2. Person B taps **Join** → points their camera at Person A's screen
3. Connected — start chatting

> **Camera on mobile:** Browsers block camera access on plain `http://` addresses.
> If you're opening `chat.html` directly from a file or over `http://`, the camera won't work.
> Use Option B (the server) instead — it's easier on phones anyway.

---

## Option B — Run the server (recommended for phones)

One person runs the signaling server. The other just opens a URL — no QR, no camera needed.

The server only handles the initial handshake. Once connected, it's out of the picture.

```bash
python3 server.py
# Prints something like: http://192.168.1.5:8080
```

Both open that URL in their browser — connection is automatic.

### Running the server from a phone

No laptop? No problem. You can run the server directly from a phone.

**Android — Termux**

Install [Termux from F-Droid](https://f-droid.org/packages/com.termux/) (not Google Play — that version is abandoned).

```bash
pkg update && pkg install python git
git clone https://github.com/amichw/lan-chat
cd lan-chat
python3 server.py
```

**iOS — iSH**

Install [iSH from the App Store](https://ish.app).

```bash
apk add python3 git
git clone https://github.com/amichw/lan-chat
cd lan-chat
python3 server.py
```

Both phones must be on the same hotspot. The server prints the URL to share.

---

## WSL2 / running across devices from the same PC

WSL2 uses a private IP not reachable from the LAN. Two options:

**localtunnel** (easiest, needs internet for setup):
```bash
# Terminal 1
python3 server.py

# Terminal 2
npx localtunnel --port 8080
# → your url is: https://xxxx.loca.lt
```
Open `https://xxxx.loca.lt/chat.html` on both devices.
The tunnel only carries the tiny signaling payloads; all chat traffic stays peer-to-peer.

**netsh portproxy** (no internet, Admin PowerShell):
```powershell
netsh interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=8080 connectaddress=$(wsl hostname -I)
```
Then use `http://<Windows-IP>:8080/chat.html`.

> When you're done, clean up with: `netsh interface portproxy reset`

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
