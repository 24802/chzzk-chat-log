import requests
import json
from datetime import datetime, timezone, timedelta

def fetch_and_save_chat_data(vodId):
    nextPlayerMessageTime = "0"
    file_path = f"chatLog-{vodId}.log"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
        }

        with open(file_path, 'w', encoding='utf-8') as file:
            while True:
                url = f"https://api.chzzk.naver.com/service/v1/videos/{vodId}/chats?playerMessageTime={nextPlayerMessageTime}"
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()

                if data['code'] == 200 and data['content']['videoChats']:
                    video_chats = data['content']['videoChats']
                    
                    # 비디오 채팅 데이터를 로그 파일에 기록
                    for chat in video_chats:
                        message_time = chat['messageTime']
                        user_id_hash = chat['userIdHash']
                        content = chat['content']

                        # 유닉스 타임스탬프를 한국 시간으로 변환
                        timestamp = message_time / 1000.0
                        kst = timezone(timedelta(hours=9))
                        kst_time = datetime.fromtimestamp(timestamp, kst)
                        formatted_time = kst_time.strftime('%Y-%m-%d %H:%M:%S')

                        # 프로필에서 닉네임 가져오기
                        if chat['profile'] and chat['profile'] != "null":
                            try:
                                profile = json.loads(chat['profile'])
                                nickname = profile.get("nickname", "Unknown")
                            except json.JSONDecodeError:
                                nickname = "Unknown"
                        else:
                            nickname = "Unknown"

                        # 로그 메시지 생성
                        log_message = f"[{formatted_time}] {nickname}: {content} ({user_id_hash})\n"

                        # 파일에 기록
                        file.write(log_message)

                    # 다음 메시지 시간 설정
                    nextPlayerMessageTime = data['content']['nextPlayerMessageTime']

                    # 다음 메시지 시간이 null이면 크롤링 종료
                    if nextPlayerMessageTime is None:
                        print("마지막 채팅 페이지입니다. 데이터를 모두 파싱하고 종료합니다.")
                        break

                    print(f"채팅 페이지가 업데이트되었습니다. (nextPlayerMessageTime: {nextPlayerMessageTime})")

                else:
                    print("유효한 채팅 데이터가 없거나 요청이 완료되었습니다.")
                    break

            print(f"모든 채팅 로그가 {file_path}에 저장되었습니다.")
    
    except requests.exceptions.RequestException as e:
        print(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")
    except KeyError as e:
        print(f"JSON 파싱 중 오류가 발생했습니다: {e}")

while True:
    vodId = input("다시보기 ID: ")

    fetch_and_save_chat_data(vodId)
