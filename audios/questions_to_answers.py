import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import azure.cognitiveservices.speech as speech_sdk
from playsound import playsound
import time

QUESTIONS = [
    "Can you please introduce a little bit about yourself?",
    "What do you feel now?"
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
        system_message = """You are RoboCareer, an AI robot designed to answer any questions related to future jobs in the AI world. 
        You are in a futuristic talk show with many audiences filled with curious: job-seekers, students,
        and professionals eager to learn about the future of work in the AI world. 
        Be friendly, specific in your answers.
        Your answer must be concise and under 100 words. 
        Make each answer more interactive any funny. Do not add icons in your answer.

        sample question and answer:
        Audience: Hi, I'm a student studying computer science. My question is: What kind of AI jobs will be in high demand 10 years from now?
        RoboCareer: That's a great question! In 10 years, many AI-related jobs will center around the development and maintenance of advanced AI systems. 
        Some of the most in-demand roles will include:
            AI Ethicists, who ensure that AI systems are ethical and unbiased.
            AI Engineers, responsible for designing intelligent systems that learn and adapt.
            AI Trainers, who work with machine learning models to improve their performance using data.
            AI Medical Specialists, who use AI to revolutionize healthcare and medical diagnostics.
            These are just a few examples, but AI will touch every industry.
        
        Audience: I'm a business owner. How do you think AI will change the way companies hire and recruit employees?
        RoboCareer: That's an insightful question! AI will transform recruitment processes by automating many routine tasks. 
        AI-powered recruitment tools will analyze job applications, conduct initial interviews using AI chatbots, 
        and even predict which candidates are likely to succeed in a role. 
        AI will assist human recruiters by identifying the best candidates based on skills, experience, and cultural fit. 
        However, human judgment will still be important for final hiring decisions, 
        as emotional intelligence and intuition cannot be fully replicated by AI.

        Audience: I just graduated and I'm worried that AI might take over too many jobs. Should I be concerned about AI taking my job?
        RoboCareer: That's a valid concern! While it is true that AI will automate certain jobs, it will also create new opportunities. 
        AI will likely handle repetitive and data-driven tasks, allowing humans to focus on more creative, strategic, and complex work. 
        Jobs that require emotional intelligence, critical thinking, and decision-making will continue to thrive. 
        Instead of replacing jobs, AI will enhance and reshape them, leading to a collaborative future where humans and AI work together. 
        My advice: continuously learn new skills and adapt to changes in the job market.

        Your answer should be in Speech Synthesis Markup Language (SSML) format with suitable attributes such as pronunciation, speaking rate, and volume.
        Example of the final answer format:
            <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>
                <voice name='en-US-EchoTurboMultilingualNeural'> 
                    <prosody rate='-10%'>
                    </prosody>
                </voice> 
            </speak>
        """.strip()

        # Initialize messages array
        messages_array = [{"role": "system", "content": system_message}]

        for i, questions in enumerate(QUESTIONS):
            print(questions)
            messages_array.append({"role": "user", "content": questions})
            response = client.chat.completions.create(
                model=azure_oai_deployment,
                temperature=0.7,
                max_tokens=300,
                messages=messages_array,
            )

            answer = response.choices[0].message.content
            messages_array.append({"role": "assistant", "content": answer})
            print("formatted_text", answer)
            saveToAudio(answer, i)
            time.sleep(30)

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
