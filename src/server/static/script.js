let audioRecorder = null;

// Create audio context
const BUFFER_SIZE = 4800;
class Player {
    constructor() {
        this.playbackNode = null;
    }

    async init(sampleRate) {
        const audioContext = new AudioContext({ sampleRate });
        await audioContext.audioWorklet.addModule("/audio-playback-worklet.js");

        this.playbackNode = new AudioWorkletNode(audioContext, "audio-playback-worklet");
        this.playbackNode.connect(audioContext.destination);
    }

    play(buffer) {
        if (this.playbackNode) {
            this.playbackNode.port.postMessage(buffer);
        }
    }

    stop() {
        if (this.playbackNode) {
            this.playbackNode.port.postMessage(null);
        }
    }
}   

class Recorder {
    constructor(onDataAvailable) {
        this.onDataAvailable = onDataAvailable;
        this.audioContext = null;
        this.mediaStream = null;
        this.mediaStreamSource = null;
        this.workletNode = null;
    }

    async start(stream) {
        console.log('starting')
        try {
            if (this.audioContext) {
                await this.audioContext.close();
            }

            this.audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 24000 });
            console.log('1')

            await this.audioContext.audioWorklet.addModule("/audio-processor-worklet.js");
            console.log('2')

            this.mediaStream = stream;
            this.mediaStreamSource = this.audioContext.createMediaStreamSource(this.mediaStream);

            this.workletNode = new AudioWorkletNode(this.audioContext, "audio-processor-worklet");
            this.workletNode.port.onmessage = event => {
                this.onDataAvailable(event.data.buffer);
            };

            this.mediaStreamSource.connect(this.workletNode);
            this.workletNode.connect(this.audioContext.destination);
            console.log('done')
        } catch (error) {
            console.log('error', error)
            this.stop();
        }
    }

    async stop() {
        if (this.mediaStream) {
            this.mediaStream.getTracks().forEach(track => track.stop());
            this.mediaStream = null;
        }

        if (this.audioContext) {
            await this.audioContext.close();
            this.audioContext = null;
        }

        this.mediaStreamSource = null;
        this.workletNode = null;
    }
}


// Function to get microphone input and send it to WebSocket
async function startAudio() {
    try {

        // handle output -> speaker stuff
        ws = new WebSocket("ws://localhost:3000/ws");

        const audioPlayer = new Player();
        audioPlayer.init(24000);

        ws.onmessage = event => {

            const data = JSON.parse(event.data);
            if (data?.type !== 'response.audio.delta') return;

            const binary = atob(data.delta);
            const bytes = Uint8Array.from(binary, c => c.charCodeAt(0));
            const pcmData = new Int16Array(bytes.buffer);

            audioPlayer.play(pcmData);
        };

        let buffer = new Uint8Array();

        const appendToBuffer = (newData) => {
            const newBuffer = new Uint8Array(buffer.length + newData.length);
            newBuffer.set(buffer);
            newBuffer.set(newData, buffer.length);
            buffer = newBuffer;
        };

        const handleAudioData = (data) => {
            const uint8Array = new Uint8Array(data);
            appendToBuffer(uint8Array);

            if (buffer.length >= BUFFER_SIZE) {
                const toSend = new Uint8Array(buffer.slice(0, BUFFER_SIZE));
                buffer = new Uint8Array(buffer.slice(BUFFER_SIZE));

                const regularArray = String.fromCharCode(...toSend);
                const base64 = btoa(regularArray);

                ws.send(JSON.stringify({type: 'input_audio_buffer.append', audio: base64}));
            }
        };

        // handle microphone -> input websocket
        audioRecorder = new Recorder(handleAudioData);
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

        await audioRecorder.start(stream);
        

    } catch (error) {
        console.error('Error accessing the microphone', error);
        alert('Error accessing the microphone. Please check your settings and try again.');
    }
}

// Function to stop audio recording and close WebSocket
function stopAudio() {
    if (audioRecorder) {
        audioRecorder.stop();  // Stop the recorder
    }
}

// Button to toggle audio
const toggleButton = document.getElementById('toggleAudio');
const liveConversationIcon = document.getElementById('liveConversationIcon');
let isAudioOn = false;

toggleButton.addEventListener('click', async () => {
    if (!isAudioOn) {
        await startAudio();
        toggleButton.textContent = 'Stop Live Conversation';
        isAudioOn = true;
        liveConversationIcon.style.display = 'block';
    } else {
        stopAudio();
        toggleButton.textContent = 'Start Live Conversation';
        isAudioOn = false;
        liveConversationIcon.style.display = 'None';
    }
});

const playButton = document.getElementById('playButton');
const audioWaveIcon = document.getElementById('audioWaveIcon');
const answerPlayer = document.getElementById('answerPlayer');

playButton.addEventListener('click', function() {
    answerPlayer.play();
});

answerPlayer.addEventListener('play', function() {
    // Show audio wave icon when audio is playing
    audioWaveIcon.style.display = 'block';
});

answerPlayer.addEventListener('ended', function() {
    // Hide audio wave icon when audio finishes playing
    audioWaveIcon.style.display = 'none';
  });

answerPlayer.addEventListener('pause', function() {
    // Optionally, hide the icon if the audio is paused
    audioWaveIcon.style.display = 'none';
});