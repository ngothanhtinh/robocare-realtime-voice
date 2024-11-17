import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import azure.cognitiveservices.speech as speech_sdk
from playsound import playsound
import time

ANSWERS = [
    """
    <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
        <voice name="en-US-EchoTurboMultilingualNeural">
            <prosody rate="-5%" volume="loud">
                <prosody volume="x-loud">
                    <emphasis level="strong">Hello everyone!</emphasis>
                </prosody>
                I'm <emphasis level="moderate">RoboCareer.</emphasis>
                I'm here to provide <prosody pitch="high">insights</prosody> and <prosody pitch="low">advice</prosody> on how to thrive in an AI-powered future.
                Let's dive in together.
            </prosody>
        </voice>
    </speak>
    """,
    """
    <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
        <voice name="en-US-EchoTurboMultilingualNeural">
            <prosody rate="-5%" volume="loud">
                Well, as an AI, <break time="300ms"/> I don't exactly have <emphasis level="moderate">feelings</emphasis>, 
                but if I did, <break time="200ms"/> 
                I'd say <break time="100ms"/> <prosody volume="x-loud">I'm super excited</prosody> to be here!
            </prosody>
        </voice>
    </speak>
    """,
    """
    <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
        <voice name="en-US-EchoTurboMultilingualNeural">
            <prosody rate="-5%" volume="loud">
                Absolutely! I'm ready to dive in!,
            </prosody>
        </voice>
    </speak>
    """,
    """
    <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
        <voice name="en-US-EchoTurboMultilingualNeural">
            <prosody rate="+10%" volume="loud">
                <break time="200ms"/> 
                <emphasis level="moderate">Ummm…</emphasis> <break time="300ms"/> That's a <emphasis level="strong">great question!</emphasis> 
                <break time="300ms"/> 
                In 10 years, many AI-related jobs will center around the development and maintenance of advanced AI systems. 
                <break time="400ms"/>
                Some of the most in-demand roles will include: 
                <break time="300ms"/> 
                <prosody pitch="+10%">AI Ethicists,</prosody> 
                <prosody pitch="+5%">AI Engineers,</prosody> 
                <prosody pitch="+5%">AI Trainers,</prosody> 
                and <prosody pitch="+5%">AI Medical Specialists.</prosody> 
                <break time="500ms"/> 
                These are just a few examples, but <emphasis level="moderate">AI will touch every industry.</emphasis>
            </prosody>
        </voice>
    </speak>
    """,
    """
    <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
        <voice name="en-US-EchoTurboMultilingualNeural">
            <prosody rate="+10%" volume="loud">
                <emphasis level="strong">Oh.</emphasis> 
                <break time="200ms"/> 
                That's an <emphasis level="moderate">insightful question!</emphasis> 
                <break time="200ms"/> 
                AI will assist human recruiters by identifying the best candidates based on <prosody pitch="+10%">skills</prosody>, 
                <prosody pitch="+5%">experience</prosody>, and <prosody pitch="+5%">cultural fit.</prosody> 
                <break time="100ms"/> 
                However, <prosody rate="medium" pitch="+5%">human judgment</prosody> will still be important for final hiring decisions, 
                as <emphasis level="strong">emotional intelligence</emphasis> and <emphasis level="moderate">intuition</emphasis> 
                cannot be fully replicated by AI.
            </prosody>
        </voice>
    </speak>
    """,
    """
    <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
        <voice name="en-US-EchoTurboMultilingualNeural">
            <prosody rate="+10%" volume="loud">
                <emphasis level="strong">That's a valid concern!</emphasis> 
                <break time="200ms"/> 
                While it's true that AI will <emphasis level="moderate">automate certain jobs.</emphasis> 
                <break time="300ms"/> 
                Jobs that require <emphasis level="strong">emotional intelligence,</emphasis> 
                <emphasis level="moderate">critical thinking,</emphasis> and <emphasis level="moderate">decision-making</emphasis> will continue to thrive. 
                <break time="200ms"/> 
                Instead of <prosody pitch="-5%">replacing jobs,</prosody> AI will <prosody pitch="+5%">enhance</prosody> and reshape them. 
                <break time="100ms"/> 
                My advice: <prosody pitch="+5%">continuously learn new skills</prosody> and adapt to changes in the job market.
            </prosody>
        </voice>
    </speak>
    """,
    """
    <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
        <voice name="en-US-EchoTurboMultilingualNeural">
            <prosody rate="0%" volume="loud">
                <emphasis level="moderate">Thank you!</emphasis> 
                <break time="100ms"/> 
                It was a <prosody pitch="+10%" volume="x-loud"><emphasis level="strong">blast</emphasis></prosody> sharing insights about the future of AI jobs. 
                <break time="200ms"/>
                Remember, the <prosody rate="medium" pitch="+5%">future is bright</prosody> and full of AI-tastic opportunities.
                <break time="200ms"/> 
                Stay curious and <prosody rate="medium" pitch="+5%">keep learning.</prosody> Have a great day!
            </prosody>
        </voice>
    </speak>
    """,
]

def main():
    try:
        global speech_config

        # Get Configuration Settings
        load_dotenv()
        ai_key = os.getenv("SPEECH_KEY")
        ai_region = os.getenv("SPEECH_REGION")
        azure_oai_endpoint = os.getenv("AZURE_OAI_ENDPOINT")
        azure_oai_key = os.getenv("AZURE_OAI_KEY")
        azure_oai_deployment = os.getenv("AZURE_OAI_DEPLOYMENT")

        # Initialize the Azure OpenAI client...
        client = AzureOpenAI(
            azure_endpoint=azure_oai_endpoint,
            api_key=azure_oai_key,
            api_version="2024-02-15-preview",
        )

        # Configure speech service
        speech_config = speech_sdk.SpeechConfig(ai_key, ai_region)
        speech_config.speech_recognition_language = "en-US"

        # Create a system message
        system_message = """Formatting the answer in Speech Synthesis Markup Language (SSML) format with suitable attributes such as pronunciation, speaking rate, and volume.
        Example format:
            <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>
                <voice name='en-US-EchoTurboMultilingualNeural'> 
                    <prosody rate='-10%'>
                        {answer}
                    </prosody>
                </voice> 
            </speak>
        """.strip()

        # Initialize messages array
        

        for i, answer in enumerate(ANSWERS):
            print(answer)
            # messages_array = [{"role": "system", "content": system_message},
            #                   {"role": "user", "content": answer}
            #                   ]
            # response = client.chat.completions.create(
            #     model=azure_oai_deployment,
            #     temperature=0.0,
            #     max_tokens=300,
            #     messages=messages_array,
            # )

            # answer = response.choices[0].message.content

            saveToAudio(answer, i)
            time.sleep(1)

    except Exception as ex:
        print(ex)


def saveToAudio(answer, index):
    # Configure speech synthesis
    speech_config.speech_synthesis_voice_name = 'en-US-EchoTurboMultilingualNeural'
    speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config)
    speak = speech_synthesizer.speak_ssml_async(answer).get()

    #/// Save to audio file
    root_path =r"H:/robocare-realtime-voice/audios/"
    file_path = root_path + f"audio_answer_{index}.wav"
    stream = speech_sdk.AudioDataStream(speak)
    stream.save_to_wav_file(file_path)

    #///
    # speak = speech_synthesizer.speak_text_async(text_to_speak).get()
    # file_path = 'output.wav'
    # with open(file_path, 'wb') as audio_file:
    #     audio_file.write(speak.audio_data)


    if speak.reason != speech_sdk.ResultReason.SynthesizingAudioCompleted:
        print(speak.reason)


if __name__ == "__main__":
    main()
