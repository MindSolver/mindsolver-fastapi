# -*- coding: utf-8 -*-
from openai import AsyncOpenAI
import os 
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from openai import AsyncOpenAI
import asyncio
import time
import tiktoken
import datetime
import openai

load_dotenv('env/.env')

# 프롬프트 만들기
def make_prompt(age,gender,job,memolet_list):
    let=''
    for i in range(len(memolet_list)):
        date=memolet_list[i].get('dateTime').split('T')[0]
        let+=f"{i+1}. {date[:10]} {date[11:16]} {memolet_list[i].get('memoLet')}\n"

    text=f"네가 작성할 일기의 조건은 아래와 같아.\n\
        # 조건 1 : 날짜, 제목, 키워드 5개가 포함된 일기를 작성할 것. 오늘 날짜는 {date} {weekday}요일임.\n\
        # 조건 2 : 반드시 아래 \'\'\'로 구분된 내용으로만 일기를 작성할 것. 과도한 추측은 하지 말것. 단, 1., 2., 3.과 같이 구분된 내용들을 합쳐 하나의 글로 된 일기를 쓸 것. 본문엔 숫자가 들어가선 안됨.\n\
        # 조건 3 : 1.,2.,3.과 같이 구분된 각 내용들은 오늘 하루 있었던 일들이야. 일기에 구체적인 시간은 절대 포함하지 마. 그리고 시간의 흐름만 반영해 일기를 과거형으로 써줘. 내용 간 개행 구분은 하지 않을 것. \n\
        # 조건 4 : 아래 \'\'\'로 구분된 내용의 글의 말투, 개조식 여부, 줄넘김, 문장부호, 말어미, 사용된 단어의 수준, ..., ㅠㅠ와 같은 이모티콘 혹은 인터넷 축약어의 사용여부 등을 분석한 후에 동일한 스타일로 일기를 쓸 것. 이때 분석 결과는 작성하지 않을 것.\n\
        # 조건 5 : 일기의 제목은 [제목]으로 구분해 작성하고, 일기의 키워드도 [키워드]로 구분해 작성할 것. 일기 내용은 [일기]로, 오늘 날짜는 [날짜]로 구분할 것.\n\
        \n\n\'\'\'\n{let}\'\'\'"

    return text

# 일기 만들기
def generate_journal(prompt): 
    start=time.time()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content":f"{prompt}"}],
        temperature=0.1
        )
    end=time.time()

    return response.choices[0].message.content, end-start
d = datetime.datetime.now()
date=f'{str(d.year%100):0>2}.{str(d.month):0>2}.{str(d.day):0>2}'
week=['월','화','수','목','금','토','일']
weekday=week[datetime.datetime.now().weekday()]
tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")


start=time.time()
client = AsyncOpenAI(api_key=os.getenv('OPEN_AI_KEY'))
async def main():
    # 유저 데이터
    user = {
        "UserDto" : {
            "GoogleID": "studyingnam",
            "username": "영진",
            "age" : 25 ,
            "gender" : "남자",
            "job" : "개발자 취업을 희망하는 학생"
        },
        # 자동으로 입력받도록 해야함
        "todayStampList": [
            {
                "GoogleID": "studyingnam",
                "dateTime" : "2024-02-09 T15:00:30", # 자동으로 입력받도록 해야함
                "stamp" : "피곤",
                "memoLet" : "오늘 아침 9시에 집에서 출발해서 방금 할머니댁에 도착했다. 내가 운전을 3시간하고, 아빠가 나머지를 했는데, 너무 힘들다."
            },
            {
                "GoogleID": "studyingnam",
                "dateTime" : "2024-02-09 T19:00:50", # 자동으로 입력받도록 해야함
                "stamp" : "배부름",
                "memoLet" : "할머니가 해주신 맛있는 음식을 먹었다. 너무 맛있는 음식을 많이 먹어서 살 찔 거 같음.."
            },
            {
                "GoogleID": "studyingnam",
                "dateTime" : "2024-02-09 T23:00:44", 
                "stamp" : "기쁨",
                "memoLet" : "먹고 나서는 조카와 함께 카페를 갔었는데, 대학입학을 앞둔 조카를 만나서 이것저것 얘기해주면서 나도 대학생활 시절로 돌아간 느낌이었다. 좋은 시간이었던 것 같다"
            },        
        ]
    }
    ## 사용자의 성별, 나이, 직업 등등 받는 부분
    user_data = user.get('UserDto')
    prompt = make_prompt(user_data.get('age'),user_data.get('gender'),user_data.get('job'),user.get('todayStampList'))

    stream = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": f"너는 {user.get('age')}세 {user.get('sex')} {user.get('job')}의 입장에서 주어진 조건에 따라 일기를 쓰는 assistant야."},
            {"role": "user", "content": f"너는 몇 개의 조건까지 완벽하게 일기에 적용할 수 있지?"},
            {"role": "assistant", "content": "저는 주어진 조건에 따라 최대한 완벽하게 일기를 쓰려고 노력하지만,\
            제한적인 지식과 경험으로 인해 모든 조건을 완벽하게 적용할 수는 없을 수도 있습니다.\
            그래도 최대한 정확하고 적절한 일기를 쓰는 것을 목표로 노력하고 있습니다."},
            {"role": "user", "content": "조건이 4개인 경우에는 완벽하게 일기에 적용하도록 해."},
            {"role": "assistant", "content": "네, 알겠습니다."},
            {"role": "user", "content":f"{prompt}"}
            ],
        temperature = 0.1,
        stream=True
        )
    async for chunk in stream:
        print(chunk.choices[0].delta.content or "", end = "")

asyncio.run(main())
