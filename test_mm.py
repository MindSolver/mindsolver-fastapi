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
        date=memolet_list[i].get('dateTime')
        let+=f"{i+1}. {date[:10]} {date[11:16]} {memolet_list[i].get('memoLet')}\n"
    text=f"너는 {age}세 {gender} {job}의 입장에서 주어진 조건에 따라 일기를 작성해주는 assistant야.\n아래 \'\'\'로 구분된 내용중 1.,2.,3.과 같이 구분된 내용들을 합쳐 하나의 글로 된 일기를 써줘.\n이때 일기에는 [제목], [내용], [키워드]가 포함되도록 해줘.\n키워드는 반드시 3개로 뽑아줘.\n1.,2.,3.과 같이 구분된 각 내용들은 오늘 하루 있었던 일들이야.\n일기에 구체적인 시간은 절대 포함하지 마.\n그리고 시간의 흐름만 반영해 일기를 과거형으로 써줘.\n일기 내용은 아래 \'\'\'로 구분된 내용을 기반으로, 과도한 추측은 하지 마.\n제목은 오늘 하루 있었던 일의 핵심을 요약해줘.\n\n\'\'\'\n{let}\'\'\'"
    return text

#키워드 만들기
def generate_keyword():
    start=time.time()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": f"너는 주어진 문장을 대표할 수 있는 적절한 키워드를 추출하는 assistant야."},
            {"role": "user", "content": f"{text}"}]
        )
    end=time.time()
    print(end-start,'sec')
    output=response.choices[0].message.content
    return output

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
    #print(end-start,'sec')
    """
    print(response.usage)
    output=response.choices[0].message.content
    print(output)
    """
    #print(response.choices[0].message.content)
    return response.choices[0].message.content, end-start
# user={'age':22,'sex':'여자','job':'대학생'}
# d = datetime.datetime.now() - datetime.timedelta(days=1) #어제 날짜로 일기 작성
# 날짜 구분
d = datetime.datetime.now()
date=f'{str(d.year%100):0>2}.{str(d.month):0>2}.{str(d.day):0>2}'
week=['월','화','수','목','금','토','일']
weekday=week[datetime.datetime.now().weekday()]
tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")
text=f"네가 작성할 일기의 조건은 아래와 같아.\n\
조건 1 : 날짜, 제목, 키워드 5개가 포함된 일기를 작성할 것. 오늘 날짜는 {date} {weekday}요일임.\n\
조건 2 : 반드시 아래 \'\'\'로 구분된 내용으로만 일기를 작성할 것.\n\
조건 3 : 아래 \'\'\'로 구분된 내용의 글의 말투, 개조식 여부, 줄넘김, 문장부호, 말어미, 사용된 단어의 수준, ..., ㅠㅠ와 같은 이모티콘 혹은 인터넷 축약어의 사용여부 등을 분석한 후에 동일한 스타일로 일기를 쓸 것. 이때 분석 결과는 작성하지 않을 것.\n\
조건 4 : 일기의 제목은 [제목]으로 구분해 작성하고, 일기의 키워드도 [키워드]로 구분해 작성할 것. 일기 내용은 [일기]로, 오늘 날짜는 [날짜]로 구분할 것.\n\
\'\'\'\n\
1. 오랜만에 치과를 다녀왔다. 스케일링을 받았는데 너무 아프다\n\
2. 하계 긴자료코에 가서 맛있는 점심을 먹었다.\n\
3. 개발이 너무 어렵다.....\n\
\'\'\'"


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
        "todayStampList": [
            {
                "GoogleID": "studyingnam",
                "dateTime" : "2024-01-30T13:11:24",
                "stamp" : "아픔",
                "memoLet" : "오랜만에 치과를 다녀왔다. 스케일링을 받았는데 너무 아프다"
            },
            {
                "GoogleID": "studyingnam",
                "dateTime" : "2024-01-30T14:11:24",
                "stamp" : "기쁨",
                "memoLet" : "하계 긴자료코에 가서 맛있는 점심을 먹었다."
            },
            {
                "GoogleID": "studyingnam",
                "dateTime" : "2024-01-30T15:11:24",
                "stamp" : "피곤",
                "memoLet" : "개발이 너무 어렵다....."
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
    
    end=time.time()
    print(end-start,'sec')

asyncio.run(main())