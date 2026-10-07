# ⚡ File Converter Engine

> A high-performance, asynchronous file conversion and processing utility supporting images, documents, audio, and video formats with pipeline streaming.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](#)
[![Docker Ready](https://img.shields.io/badge/docker-ready-blue.svg)](#docker-deployment)
[![Node.js / Python / Go](https://img.shields.io/badge/runtime-v20%2B-informational)](#prerequisites)

## ✨ Features

- **Multi-Format Pipeline:** Seamless conversion across Image, Document, Audio, and Video formats.
- **Stream Processing:** Low-memory footprint using chunked stream pipes for large file conversions.
- **Validation & Sanity Checks:** Automated MIME-type identification, file signature (magic byte) verification, and corrupt file detection prior to conversion.

---



## 🏗 Architecture & Conversion Pipeline

The engine separates file handling into distinct pipeline stages: validation, AST/stream parsing, core conversion, and packaging.

1. **Ingestion & Validation:** Inspects raw file streams and verifies magic bytes (header signatures) to prevent malicious extension spoofing.
2. **Parser Dispatch:** Routes validated payloads to dedicated workers based on source and target MIME types.
3. **Execution Engine:** Spawns native child processes or streams data through optimized bindings with real-time process monitoring.
4. **Cleanup & Delivery:** Flushes temporary storage, validates output integrity, and delivers the target file stream.

---

## 🔄 Supported Formats

| Category | Input Formats | Output Formats | Under the Hood |
| :--- | :--- | :--- | :--- |
| **Images** | `PNG`, `JPEG`, `WEBP`, `TIFF`, `SVG`, `HEIC` | `PNG`, `JPEG`, `WEBP`, `AVIF`, `PDF` | ImageMagick / Sharp |
| **Documents** | `PDF`, `DOCX`, `EPUB`, `MD`, `HTML`, `TXT` | `PDF`, `DOCX`, `EPUB`, `MD`, `HTML` | Pandoc / LibreOffice |
| **Audio** | `MP3`, `WAV`, `AAC`, `FLAC`, `OGG`, `M4A` | `MP3`, `WAV`, `AAC`, `FLAC`, `OGG` | FFmpeg |
| **Video** | `MP4`, `MKV`, `AVI`, `MOV`, `WEBM` | `MP4`, `WEBM`, `GIF` | FFmpeg |

---

## 🛠 Prerequisites & System Dependencies


* **FFmpeg** (v5.0+): Media transcoding (`ffmpeg -version`)
* **Pandoc** (v3.0+): Document conversion (`pandoc -version`)
* **ImageMagick** / **Libvips**: Image processing (`magick -version` or `vips -version`)
* **Node.js** (v18+) or **Python** (v3.10+): Application runtime

---

