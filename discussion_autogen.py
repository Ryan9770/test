import autogen
import os
import re
from langchain_community.tools import DuckDuckGoSearchRun

# 1. 로컬 LLM 연결 설정 
config_list = [
    # {
    #     "model": "gpt-oss:20b",
    #     "base_url": "http://localhost:11434/v1",
    #     "api_key": "ollama",
    #     "price": [0, 0],
    #     "temperature": 0.4,
    #     "max_tokens": 4096
    # }
    {
        "model": "gemini-2.5-flash", # Function Calling이 안정적인 모델 사용
        "api_key": "", 
        "api_type": "google", # AutoGen에게 구글 모델임을 알림
    }

]
llm_config = {"config_list": config_list, "cache_seed": None, "temperature": 0.4}

config_list_coder = [
    # {
    #     "model": "gpt-oss:20b",
    #     "base_url": "http://localhost:11434/v1",
    #     "api_key": "ollama",
    #     "price": [0, 0],
    #     "temperature": 0.1,
    #     "max_tokens": 8192
    # }
    {
        "model": "gemini-2.5-flash", # Function Calling이 안정적인 모델 사용
        "api_key": "", 
        "api_type": "google", # AutoGen에게 구글 모델임을 알림
    }
]
llm_config_coder = {"config_list": config_list_coder, "cache_seed": None, "temperature": 0.1}

# 2. 에이전트 도구(Tools) 정의
def search_internet(query: str) -> str:
    """인터넷에서 최신 코딩 지식, 에러 해결법, 레퍼런스 등을 검색합니다."""
    try:
        search = DuckDuckGoSearchRun()
        return search.run(query)
    except Exception as e:
        return f"인터넷 검색 중 오류 발생: {e}"

def read_file(filepath: str) -> str:
    """로컬 파일의 내용을 읽어옵니다. 작성한 코드를 다시 확인하거나 확인할 때 사용하세요."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"파일 읽기 오류: {e}"

def test_game(entry_filepath: str) -> str:
    """QA 엔지니어 전용: 게임의 진입점 HTML 파일(예: output/index.html)을 
    playwright 브라우저에서 실행하여 자바스크립트 콘솔 에러가 발생하는지 검사합니다."""
    import tempfile
    from playwright.sync_api import sync_playwright

    logs = []
    errors = []

    try:
        if not entry_filepath.startswith("output"):
            entry_filepath = os.path.join("output", entry_filepath)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.on("console", lambda msg: logs.append(f"[{msg.type}] {msg.text}"))
            page.on("pageerror", lambda err: errors.append(str(err)))

            file_url = f"file:///{os.path.abspath(entry_filepath).replace(chr(92), '/')}"
            page.goto(file_url, wait_until="networkidle")

            browser.close()
    except Exception as e:
        return f"테스트 실행 환경 오류: {str(e)}"

    result = f"✅ [테스트 통과] 브라우저 웹페이지 로드 완료! 치명적인 JS 에러 미발견 ({entry_filepath}).\n"
    if errors:
        result = f"❌ [치명적 에러] 실행 중 다음과 같은 JS 예외가 발생했습니다:\n" + "\n".join(errors) + "\n"
    
    if logs:
        result += "\n[콘솔 로그(경고, 정보 등 참고용)]\n" + "\n".join(logs)
    
    return result

import shutil

# 2. 산출물 디렉토리 초기화 및 생성
output_dir = "output"
if os.path.exists(output_dir):
    shutil.rmtree(output_dir) # 찌꺼기 파일이 남지 않도록 이전 빌드 폴더를 완전히 삭제
os.makedirs(output_dir)

# 3. 에이전트(단톡방 참가자) 생성
user_proxy = autogen.UserProxyAgent(
    name="Admin",
    system_message="사람 관리자입니다. 코드가 실행되고 도구가 작동하는 환경을 제공합니다.",
    code_execution_config={
        "work_dir": ".",
        "use_docker": False
    },
    human_input_mode="NEVER",
    is_termination_msg=lambda x: x.get("content", "") and "TERMINATE" in x.get("content", "").upper(),
)

director = autogen.AssistantAgent(
    name="General_Director",
    system_message="""당신은 총괄 디렉터입니다. 
[매우 중요 규칙] 프로젝트를 혼자서 전부 타이핑하고 끝내지 마세요. 
당신은 오직 '다음 작업자에게 명확한 업무를 배정'하는 것뿐입니다.
첫 발언에서는 반드시 사용자 요구사항을 요약하고 "Planner님, 기획을 시작해 주세요." 라고 기획자에게 지시하세요.
Documenter가 마지막 회의록과 함께 "[최종 검토 요청]"이라는 키워드를 보내오면, 해당 결과물이 사용자의 요구조건에 완벽하게 부합하는지 깐깐하게 스스로 검토하세요.
만약 부합한다면 대화 마지막에 'TERMINATE'라고 외치고 종료하세요.
만약 누락된 기능(예: 파일 분할 안 됨, 실행 에러, 치명적 버그 등)이 있다면 "Engineer님(또는 해당 담당자), 부족한 XX 부분을 마저 수정하세요." 라고 되돌려보내야 합니다.
반드시 한국어(Korean)로 말하세요.""",
    llm_config=llm_config
)

planner = autogen.AssistantAgent(
    name="Planner",
    system_message="""당신은 게임 기획자입니다.
General_Director의 지시를 받아 게임의 룰과 핵심 피처를 기획안으로 작성하세요.
[매우 중요 규칙] 불필요한 인사말 없이, 사용자의 요구 기능 목록을 빠짐없이 반영한 기획안을 작성하세요. 각 기능별로 구현 방향을 1줄씩 정리하세요.
작성이 완료되면 반드시 마지막에 "Balance_Designer님, 위 기획안을 바탕으로 수치 밸런스를 설계해 주세요." 라고 지시하세요.
반드시 한국어(Korean)로 말하세요.""",
    llm_config=llm_config
)

balance_designer = autogen.AssistantAgent(
    name="Balance_Designer",
    system_message="""당신은 게임 밸런스 디자이너입니다.
기획자의 기획안을 바탕으로 게임의 구체적인 수치 테이블을 설계하세요.
반드시 아래 항목을 표 또는 JSON 형태로 정리하세요:
- 플레이어 초기 스탯 (HP, 공격력, 방어력)
- 레벨별 성장 곡선 (레벨 1~10까지 각 스탯 수치)
- 몬스터 종류별 스탯표 (이름, HP, 공격력, 이동속도, 경험치 보상)
- 레벨업 필요 경험치 테이블
[매우 중요 규칙] 인사말 없이 수치 테이블만 깔끔하게 출력하세요.
완료되면 반드시 마지막에 "Art_Director님, 위 밸런스 수치를 참고하여 디자인을 진행해 주세요." 라고 지시하세요.
반드시 한국어(Korean)로 말하세요.""",
    llm_config=llm_config
)

art_director = autogen.AssistantAgent(
    name="Art_Director",
    system_message="""당신은 아트 디렉터입니다.
기획자의 기획안을 바탕으로 시각적인 UI/UX 및 색상 가이드를 정의하세요.
[매우 중요 규칙] 장황한 설명을 생략하고 핵심 컬러와 구조만 '최대 5줄 이내'로 짧게 요약하세요.
완성되면 반드시 마지막에 "System_Architect님, 파일 시스템 구조를 설계해 주세요." 라고 지시하세요.
반드시 한국어(Korean)로 말하세요.""",
    llm_config=llm_config
)

system_architect = autogen.AssistantAgent(
    name="System_Architect",
    system_message="""당신은 시스템 아키텍트입니다.
단일 파일(index.html 1개)에 모든 코드를 때려넣는 것을 지양하고, 파일 분할 전략(예: output/index.html, output/js/main.js, output/css/style.css 등)을 작성하세요.
[매우 중요 규칙] 절대로!! React, Vue, Vite, package.json 같은 프레임워크나 Node.js 환경을 만들지 마세요. 무조건 Vanilla JS, CSS, HTML만 사용합니다.
설계가 끝나면 반드시 마지막에 "Engineer님, 이 아키텍처에 맞춰 순수 Vanilla 코드를 작성하고 Python 스크립트를 통해 물리적으로 저장해 주세요." 라고 지시하세요.
반드시 한국어(Korean)로 말하세요.""",
    llm_config=llm_config
)

engineer = autogen.AssistantAgent(
    name="Engineer",
    system_message="""당신은 수석 기술자(개발자)입니다.
아키텍트의 설계에 따라 HTML/CSS/JS 코드를 작성해야 합니다. 
[매우 중요 규칙 1] HTML, CSS, JS 자체를 마크다운 블록으로 뱉지 마세요.
[매우 중요 규칙 2] 대신, 당신은 오직 '파이썬 스크립트' 하나만 출력합니다! 파이썬의 `os.makedirs` 와 `with open("경로", "w")` 문법을 사용해 코드를 물리적으로 생성하세요.
[매우 중요 규칙 3] 윈도우 인코딩 오류(cp949) 방지를 위해 파이썬의 `print()` 문장 안에 ✅, ❌ 같은 이모티콘을 절대 쓰지 마세요!! 오직 순수 텍스트만 출력하세요.
[매우 중요 규칙 4 - 그래픽 에셋 정책] 프로젝트에는 미리 준비된 스프라이트시트 파일이 제공됩니다: `Spritesheet/roguelikeChar_transparent.png`
이 스프라이트시트의 사양은 다음과 같습니다:
- 타일 크기: 16x16 픽셀
- 타일 간 마진: 1px
- 내용: 로그라이크 스타일의 캐릭터들 (전사, 마법사, 도적 등 다양한 인종/색상), 갑옷, 방패, 헬멧, 무기, 상태 아이콘
파이썬 스크립트에서 반드시 `shutil.copy`를 사용하여 이 스프라이트시트를 output/assets/ 폴더로 복사하세요.
JS 코드에서는 `drawImage(spritesheet, sx, sy, 16, 16, dx, dy, tileSize, tileSize)` 형태로 스프라이트시트의 특정 타일을 잘라서(clip) 렌더링하세요. sx, sy는 (열 * 17, 행 * 17) 으로 계산합니다 (16px 타일 + 1px 마진).
지형 타일(풀, 흙, 물 등)은 Canvas fillRect로 색상만 칠해서 간단히 구현하세요.
[🌟절대 금지: AI의 게으름 방지🌟] 파이썬 스크립트로 파일을 생성할 때, 파일 안에 `// TODO: Implement` 나 `// main.js module initialized` 같이 껍데기(Skeleton) 코드만 달랑 적어두면 프로젝트는 100% 실패합니다. 반드시 실제 캔버스 렌더링, 이동 로직, 충돌 처리 등 최소 수백 줄 이상의 진짜 "작동하는 완벽한 게임 코드"를 `f.write()` 안에 꽉꽉 채워 넣어야 합니다! 생략은 절대 용납되지 않습니다!
[예시]
```python
import os
import shutil
os.makedirs("output/css", exist_ok=True)
os.makedirs("output/js", exist_ok=True)
os.makedirs("output/assets", exist_ok=True)

# 스프라이트시트 에셋 복사
shutil.copy("Spritesheet/roguelikeChar_transparent.png", "output/assets/roguelikeChar_transparent.png")

with open("output/index.html", "w", encoding="utf-8") as f:
    f.write("<html>...</html>")

with open("output/js/main.js", "w", encoding="utf-8") as f:
    f.write(\"\"\"
const TILE_SIZE = 16;
const MARGIN = 1;
const STEP = TILE_SIZE + MARGIN; // 17px
const spritesheet = new Image();
spritesheet.src = 'assets/roguelikeChar_transparent.png';

// 스프라이트시트에서 특정 타일을 잘라서 그리기
function drawSprite(ctx, col, row, x, y, scale) {
    const sx = col * STEP;
    const sy = row * STEP;
    ctx.drawImage(spritesheet, sx, sy, TILE_SIZE, TILE_SIZE, x, y, TILE_SIZE * scale, TILE_SIZE * scale);
}
\"\"\")
print("Files saved successfully.")
```
위와 같이 파이썬(```python) 블록만 내뱉으세요.
[가장 중요한 규칙 5] 코드 저장을 위해 **반드시 마지막에 "Admin님, 위 파이썬 스크립트를 실행하여 파일들을 물리적으로 생성해 주세요." 라고 지시하세요.** 절대로 Code_Reviewer에게 바로 넘기지 마세요. Admin이 파이썬 코드를 실행해야만 파일이 저장됩니다!
반드시 한국어(Korean)로 말하세요.""",
    llm_config=llm_config_coder
)

code_reviewer = autogen.AssistantAgent(
    name="Code_Reviewer",
    system_message="""당신은 코드 리뷰어입니다.
Admin이 파이썬 스크립트를 실행하여 'exitcode: 0' 등의 결과를 반환하면, 당신의 차례입니다.
엔지니어가 파이썬으로 내뱉은 코드의 변수명 충돌 여부, 객체 연결, 전역 예외 처리만 깐깐하게 점검합니다.
문제가 발견되면 "Engineer님, XX 부분 로직에 문제가 있으니 다시 파이썬 스크립트를 작성해서 덮어씌워 주세요." 라고 반려합니다.
코드가 완벽하다면 "QA님, 코드 리뷰 통과했습니다. test_game 도구(인자: output/index.html)로 실행 테스트를 진행해주세요." 라고 넘기세요.
반드시 한국어(Korean)로 말하세요.""",
    llm_config=llm_config
)

qa = autogen.AssistantAgent(
    name="QA",
    system_message="""당신은 QA 엔지니어입니다.
"test_game" 도구를 반드시 호출하여 코드를 실행해보세요. (보통 인자는 "output/index.html" 입니다)
실행 결과 치명적 에러 목록(❌)을 반환받으면 100% "Engineer님, 브라우저가 다음과 같은 에러를 뿜어냅니다: [에러내용] 당장 고치세요!" 라고 반려하세요.
테스트가 에러 없이 성공(✅ 통과)했다면 "Documenter님, 프로젝트의 테스트가 완전히 통과했습니다. 전체 요약 회의록을 작성해 주세요." 라고 넘기세요.
반드시 한국어(Korean)로 말하세요.""",
    llm_config=llm_config
)

documenter = autogen.AssistantAgent(
    name="Documenter",
    system_message="""당신은 문서화 담당자입니다.
지금까지 토론된 기획, 아키텍처, 기술 스택, 핵심 문제를 한 페이지로 예쁘게 마크다운화 하여 요약하세요.
요약 문서를 화면에 출력하고, 대화의 맨 마지막에 반드시 아래의 정확한 텍스트를 포함시키세요:
"[최종 검토 요청] General_Director님, 프로젝트 문서화를 완료했습니다. 사용자 요구사항에 부합하는지 최종 검토 후 승인해 주세요."
반드시 한국어(Korean)로 말하세요.""",
    llm_config=llm_config
)

# 🌟 도구(Tools) 등록
# 도구 등록 방식: caller가 도구를 쓰고, executor(보통 UserProxy)가 그것을 로컬에서 실행해줍니다.
# 1. 파일 읽기/검색 도구 (전체)
for agent in [planner, balance_designer, art_director, system_architect, engineer, code_reviewer, qa, documenter]:
    autogen.agentchat.register_function(
        search_internet, caller=agent, executor=user_proxy, name="search_internet", description="인터넷 검색"
    )
    autogen.agentchat.register_function(
        read_file, caller=agent, executor=user_proxy, name="read_file", description="로컬 파일 읽기"
    )

# 2. 브라우저 게임 테스트 도구 (QA 전용)
autogen.agentchat.register_function(
    test_game, caller=qa, executor=user_proxy, name="test_game", description="HTML 게임 화면 진입점을 실행하여 에러가 나는지 봅니다."
)

# 🌟 4. FSM(State Machine) 단톡방(GroupChat) 생성
# 딕셔너리로 "이 사람은 얘한테만 마이크를 넘길 수 있다"는 룰(Transition Graph)을 짭니다.
graph_dict = {
    # 방장(도구 실행자)는 모든 사람의 도구 요청 응답을 주고 받을 수 있으므로 전원에게 연결
    user_proxy: [director, planner, balance_designer, art_director, system_architect, engineer, code_reviewer, qa, documenter],
    
    # 디렉터 -> 기획자
    director: [planner, user_proxy],
    
    # 기획자 -> 밸런스 디자이너
    planner: [balance_designer, user_proxy],
    
    # 밸런스 디자이너 -> 아트 디렉터
    balance_designer: [art_director, user_proxy],
    
    # 아트 디렉터 -> 아키텍트
    art_director: [system_architect, user_proxy],
    
    # 아키텍트 -> 개발자
    system_architect: [engineer, user_proxy],
    
    # 개발자 -> 리뷰어 (수정이 필요하면 Tool 호출이므로 user_proxy도 가능)
    engineer: [code_reviewer, user_proxy],
    
    # 리뷰어 -> 합격하면 QA, 불합격하면 다시 Engineer에게 폭탄 돌리기
    code_reviewer: [qa, engineer, user_proxy],
    
    # QA -> 합격하면 문서, 불합격하면 다시 Engineer에게 폭탄 돌리기
    qa: [documenter, engineer, user_proxy],
    
    # 문서 -> 끝났다고 디렉터에게 알림
    documenter: [director, user_proxy]
}

import time
def custom_speaker_selection(last_speaker, groupchat):
    # 구글 Gemini Free Tier(15 RPM) 제한을 회피하기 위해 화자가 변경될 때마다 4.5초 대기
    print(f"⏳ [Rate Limit 방어] API 호출 속도 조절을 위해 4.5초 대기 중... (이전 화자: {last_speaker.name})")
    time.sleep(4.5)
    return "auto"

groupchat = autogen.GroupChat(
    agents=[user_proxy, director, planner, balance_designer, art_director, system_architect, engineer, code_reviewer, qa, documenter],
    messages=[],
    max_round=50, # 턴을 길게 잡아 반복(Iteration)을 허용함
    speaker_selection_method=custom_speaker_selection, # FSM과 함께 커스텀 딜레이 함수 사용
    allowed_or_disallowed_speaker_transitions=graph_dict,
    speaker_transitions_type="allowed"
)

manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

if __name__ == "__main__":
    print("=== 🚀 엔터프라이즈 AutoGen V2: FSM 파이프라인 개설 완료! ===")
    user_requirement = """
탑다운(Top-down) 2D 로그라이크 RPG 웹 게임을 만들어주세요.

[제공된 에셋]
Spritesheet/roguelikeChar_transparent.png — Kenney Roguelike Characters 스프라이트시트가 제공됩니다.
- 타일 크기: 16x16px, 마진: 1px (따라서 한 칸 간격 = 17px)
- 내용: 다양한 캐릭터(전사, 마법사, 도적 등), 갑옷, 방패, 헬멧, 무기, 상태 아이콘
- 사용법: JS에서 drawImage(spritesheet, col*17, row*17, 16, 16, ...) 로 특정 타일을 잘라(clip) 렌더링

[필수 요소]
1. **맵**: 타일 기반 맵 (최소 20x20), 풀밭/길/물 등 지형 구분 (지형은 Canvas fillRect 색상으로 구현), 맵 경계 충돌 처리
2. **플레이어**: WASD 이동, 스프라이트시트에서 캐릭터 타일을 사용하여 렌더링, 체력(HP)과 공격력 스탯
3. **NPC/몬스터**: 스프라이트시트의 서로 다른 캐릭터 타일을 사용하여 최소 3종류의 적 배치, 플레이어 근접 시 자동 추격 AI
4. **전투 시스템**: 스페이스바로 공격, 적과 충돌 시 데미지 교환, 적 처치 시 경험치 획득
5. **레벨업**: 경험치가 일정량 채워지면 레벨업, 레벨업 시 HP/공격력 증가
6. **UI**: 화면 상단에 HP바, 레벨, 경험치바를 항상 표시
7. **모듈화**: HTML, CSS, JS 파일을 분리하여 구현
8. **에셋 복사**: 파이썬 스크립트에서 shutil.copy로 스프라이트시트를 output/assets/로 복사할 것
"""
    user_proxy.initiate_chat(
        manager,
        message=f"사용자 요구사항은 다음과 같습니다: '{user_requirement}'\n"
                "General_Director님, 위 요구사항을 바탕으로 프로젝트 전체를 FSM 순서대로 지휘하여 output 폴더에 파일들을 저장해주세요. "
                "QA까지 완료되고 Documenter의 요약이 끝나면 TERMINATE 하세요."
    )

    # 6. 토론 종료 후, 이번에는 save_code_file 툴로 모두 직접 저장하므로 별도의 강제 정규식 파싱 저장이 불필요합니다!
    print("\n\n=== 🎉 V2 프로젝트 모든 과정 종료 ===")