# FFmpeg Installation Guide for Voice Input Feature

## Issue
The voice input feature requires **ffmpeg** to convert audio files from WebM format (used by browsers) to WAV format (required by speech recognition).

## Error Message
```
Audio conversion requires ffmpeg. Please install ffmpeg or use a different audio format.
```

---

## Solution 1: Install FFmpeg (Recommended)

### For Windows:

#### Option A: Using Chocolatey (Easiest)
1. Open PowerShell as Administrator
2. If you don't have Chocolatey, install it first:
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   ```
3. Install FFmpeg:
   ```powershell
   choco install ffmpeg
   ```
4. Restart your terminal

#### Option B: Manual Installation
1. Download FFmpeg from: https://www.gyan.dev/ffmpeg/builds/
   - Download the "ffmpeg-release-essentials.zip" file
2. Extract the ZIP file to `C:\ffmpeg`
3. Add FFmpeg to PATH:
   - Open System Properties → Environment Variables
   - Edit "Path" variable
   - Add: `C:\ffmpeg\bin`
   - Click OK
4. Restart your terminal
5. Verify installation:
   ```powershell
   ffmpeg -version
   ```

---

## Solution 2: Use Alternative Audio Format (Temporary Workaround)

If you cannot install ffmpeg immediately, the browser will attempt to record in WAV format directly.

### To test if your browser supports WAV recording:
Open browser console (F12) and run:
```javascript
console.log(MediaRecorder.isTypeSupported('audio/wav'));
```

- If `true`: Browser can record WAV directly (no ffmpeg needed)
- If `false`: Browser only supports WebM (ffmpeg required)

---

## Solution 3: Quick Test Without Installation

### Test Voice Feature Without Installing FFmpeg:

Some browsers (like Safari) support WAV recording natively. Try using:
- Safari (Mac/iOS)
- Microsoft Edge (some versions)

---

## Verification

After installing ffmpeg, restart your Flask server:

1. Stop the current server (Ctrl+C)
2. Start it again:
   ```powershell
   python run.py
   ```
3. Test the voice input feature
4. Check server logs for:
   ```
   ✅ Converted audio to WAV: ...
   ```

---

## Technical Details

### Why FFmpeg is Needed:
- Browsers record audio in WebM/Opus format (compressed)
- Google Speech Recognition API requires WAV/FLAC format (uncompressed)
- FFmpeg converts WebM → WAV seamlessly

### Audio Conversion Parameters:
```
Format: PCM WAV
Sample Rate: 16kHz
Channels: Mono (1)
Bit Depth: 16-bit
```

---

## Alternative: Use Google Cloud Speech API

If ffmpeg installation is problematic, consider using Google Cloud Speech API which can handle WebM directly:

1. Set up Google Cloud credentials
2. Update `voice_processor.py`:
   ```python
   voice_processor = VoiceProcessor(use_google_cloud=True)
   ```

---

## Troubleshooting

### Issue: "ffmpeg not found"
- Ensure FFmpeg is in PATH
- Restart terminal/IDE after installation
- Try running: `where ffmpeg` (Windows) or `which ffmpeg` (Mac/Linux)

### Issue: "Permission Denied"
- Run PowerShell as Administrator
- Check antivirus isn't blocking FFmpeg

### Issue: Still not working after install
- Restart Flask server completely
- Clear Python cache: Delete `__pycache__` folders
- Reinstall pydub: `pip install --upgrade pydub`

---

## Contact Support

If issues persist:
1. Check server logs for detailed error messages
2. Verify ffmpeg installation: `ffmpeg -version`
3. Test audio file manually:
   ```powershell
   ffmpeg -i test.webm -acodec pcm_s16le -ar 16000 -ac 1 output.wav
   ```

---

**Status**: Feature fully functional once ffmpeg is installed
**Priority**: High (required for voice input)
**Estimated Fix Time**: 5-10 minutes
