import time
import speech_recognition as sr
import os
import openai
import pyttsx3
import logging
import requests
import json
import base64
def get_token():
    logging.info('开始获取token...')
    # 获取token
    baidu_server = "https://openapi.baidu.com/oauth/2.0/token?"
    grant_type = "client_credentials"
    client_id = " "
    client_secret = " "
    payload = ""
    # 拼url
    url = f"{baidu_server}grant_type={grant_type}&client_id={client_id}&client_secret={client_secret}"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    token = json.loads(response.text)["access_token"]
    return token


def audio_baidu(filename):
    # 保存为音频文件
    with open(f"test.wav", "wb") as f:
        # 将麦克风录到的声音保存为wav文件
        f.write(filename.get_wav_data(convert_rate=16000))
    logging.info('录音结束，识别中...')

    logging.info('开始识别语音文件...')
    with open(f"test.wav", "rb") as f:
        speech = base64.b64encode(f.read()).decode('utf-8')
    size = os.path.getsize(f"test.wav")
    token = get_token()
    headers = {'Content-Type': 'application/json'}
    url = "https://vop.baidu.com/server_api"
    data = {
        "format": "wav",
        "rate": "16000",
        "dev_pid": "1536",
        "speech": speech,
        "cuid": "TEDxPY",
        "len": size,
        "channel": 1,
        "token": token,
    }

    req = requests.post(url, json.dumps(data), headers)
    result = json.loads(req.text)

    if result["err_msg"] == "success.":
        print(result['result'])
        return result['result']
    else:
        print("内容获取失败，退出语音识别")
        return -1


# 用于转录音频、发送到ChatGPT并大声朗读的功能


def listen_and_respond(after_prompt=True):
    """
    转录音频，发送到ChatGPT，并以语音进行响应
    Args:
    after_prompt: bool, whether the response comes directly
    after the user says "Hey, Jarvis!" or not
    
    """
    # Default is don't start listening, until I tell you to
    start_listening = False
    with microphone as source:
        while after_prompt:
            if start_listening==True:
                break
            recognizer.adjust_for_ambient_noise(source)
            print("说小爱同学开始")
            audio = recognizer.listen(source, phrase_time_limit=3)
            try:
                # 英文转文本
                # transcription = recognizer.recognize_google(audio)

                # 中文转文本
                transcription = audio_baidu(audio)
                print(transcription)
                # 英文唤醒
                # print(transcription.lower())
                # 中文唤醒
                if "小爱同学" in transcription[0]:
                    start_listening = True
                    break
                else:
                    start_listening = False
            except sr.UnknownValueError:
                 start_listening = False
        # else:
        #     start_listening = True

        while start_listening:
            try:
                print("正在听你的问题。。。。。")
                audio = recognizer.record(source, duration=5)
                transcription = audio_baidu(audio)
                print(f"Input text: {transcription}")
                if "休息" in transcription[0]:
                    start_listening = False
                    break
                # Send the transcribed text to the ChatGPT3 API
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=transcription[0],
                    temperature=0.9,
                    max_tokens=512,
                    top_p=1,
                    presence_penalty=0.6
                )

                # Get the response text from the ChatGPT3 API
                response_text = response.choices[0].text

                # Print the response from the ChatGPT3 API
                print(f"Response text: {response_text}")

                #  Say the response
                engine.say(response_text)
                engine.runAndWait()

            except sr.UnknownValueError:
                print("Unable to transcribe audio")


# pyttsx3 engine paramaters
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('voice', 'english_north')

# My OpenAI API Key
openai.api_key = "YOUR "

recognizer = sr.Recognizer()
microphone = sr.Microphone()

# First question
first_question = True

# Initialize last_question_time to current time
last_question_time = time.time()

# Set threshold for time elapsed before requiring "Hey, Jarvis!" again
threshold = 60  # 1 minute

while True:
    if (first_question == True) | (time.time() - last_question_time > threshold):
        listen_and_respond(after_prompt=True)
        first_question = False
    else:
        listen_and_respond(after_prompt=False)
