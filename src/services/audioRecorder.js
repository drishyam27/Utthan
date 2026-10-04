/**
 * Utthan Audio Recorder Utility
 * Captures microphone audio using MediaRecorder API for backend STT transcription.
 * Ensures microphone hardware is released immediately when recording finishes or cancels.
 */

export function isAudioRecordingSupported() {
  if (typeof window === 'undefined') return false;
  return !!(
    navigator.mediaDevices &&
    typeof navigator.mediaDevices.getUserMedia === 'function' &&
    window.MediaRecorder
  );
}

function getSupportedAudioMimeType() {
  if (typeof window === 'undefined' || !window.MediaRecorder) return '';
  const candidateTypes = [
    'audio/webm;codecs=opus',
    'audio/webm',
    'audio/ogg;codecs=opus',
    'audio/mp4',
    'audio/wav',
  ];

  for (const type of candidateTypes) {
    if (MediaRecorder.isTypeSupported(type)) {
      return type;
    }
  }
  return '';
}

export class AudioRecorder {
  constructor({ maxDurationMs = 25000, onMaxDurationReached } = {}) {
    this.maxDurationMs = maxDurationMs;
    this.onMaxDurationReached = onMaxDurationReached;
    this.mediaRecorder = null;
    this.audioStream = null;
    this.chunks = [];
    this.startTime = 0;
    this.maxDurationTimer = null;
    this.state = 'idle'; // 'idle' | 'recording' | 'stopped'
  }

  async start() {
    if (!isAudioRecordingSupported()) {
      throw new Error('UNSUPPORTED_BROWSER');
    }

    if (this.state === 'recording') {
      return;
    }

    try {
      this.audioStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });
    } catch (err) {
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        throw new Error('PERMISSION_DENIED');
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        throw new Error('DEVICE_NOT_FOUND');
      }
      throw new Error('MICROPHONE_FAILED');
    }

    const mimeType = getSupportedAudioMimeType();
    const options = mimeType ? { mimeType } : {};

    try {
      this.mediaRecorder = new MediaRecorder(this.audioStream, options);
    } catch {
      this.mediaRecorder = new MediaRecorder(this.audioStream);
    }

    this.chunks = [];
    this.startTime = Date.now();
    this.state = 'recording';

    this.mediaRecorder.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) {
        this.chunks.push(event.data);
      }
    };

    this.mediaRecorder.start(250); // Collect slices every 250ms

    if (this.maxDurationMs > 0) {
      this.maxDurationTimer = setTimeout(() => {
        if (this.state === 'recording') {
          if (this.onMaxDurationReached) {
            this.onMaxDurationReached();
          }
        }
      }, this.maxDurationMs);
    }
  }

  async stop() {
    if (this.maxDurationTimer) {
      clearTimeout(this.maxDurationTimer);
      this.maxDurationTimer = null;
    }

    if (!this.mediaRecorder || this.state !== 'recording') {
      this._cleanupStream();
      this.state = 'idle';
      return null;
    }

    return new Promise((resolve) => {
      this.mediaRecorder.onstop = () => {
        const mimeType = this.mediaRecorder?.mimeType || 'audio/webm';
        const blob = new Blob(this.chunks, { type: mimeType });
        const durationMs = Date.now() - this.startTime;

        this._cleanupStream();
        this.state = 'idle';
        this.chunks = [];

        resolve({
          blob,
          mimeType,
          durationMs,
        });
      };

      try {
        this.mediaRecorder.stop();
      } catch {
        this._cleanupStream();
        this.state = 'idle';
        resolve(null);
      }
    });
  }

  cancel() {
    if (this.maxDurationTimer) {
      clearTimeout(this.maxDurationTimer);
      this.maxDurationTimer = null;
    }
    if (this.mediaRecorder && this.state === 'recording') {
      try {
        this.mediaRecorder.stop();
      } catch {}
    }
    this._cleanupStream();
    this.chunks = [];
    this.state = 'idle';
  }

  _cleanupStream() {
    if (this.audioStream) {
      try {
        this.audioStream.getTracks().forEach((track) => track.stop());
      } catch {}
      this.audioStream = null;
    }
  }
}
