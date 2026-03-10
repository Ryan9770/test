from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

# 1. 로컬 LLM 연결
local_llm = LLM(
    model="ollama/qwen2.5", # 또는 llama3.1
    base_url="http://localhost:11434"
)

# 2. 인터넷 검색 도구
@tool("Search_Internet")
def search_internet(query: str) -> str:
    """인터넷에서 최신 정보, 기사, 여론 등을 검색할 때 사용하는 도구입니다. 검색어(query)를 입력하세요."""
    search = DuckDuckGoSearchRun()
    return search.run(query)

# 3. 에이전트 생성
mint_lover = Agent(
    role='민트초코 찬성파',
    goal='민트초코가 최고임을 증명하기',
    backstory='당신은 민트초코를 사랑합니다. 반드시 `Search_Internet` 도구를 사용해 긍정적인 팩트를 찾고, 이를 바탕으로 한국어로 강력하게 주장하세요.',
    verbose=True,
    tools=[search_internet],
    llm=local_llm,
    max_iter=3
)

mint_hater = Agent(
    role='민트초코 반대파',
    goal='민트초코 찬성파의 주장을 반박하고 치약맛임을 증명하기',
    backstory='당신은 민트초코를 극도로 싫어합니다. 앞선 찬성파의 주장을 읽고, 반드시 `Search_Internet` 도구를 사용해 부정적인 팩트(호불호, 악평 등)를 찾아 한국어로 날카롭게 반박하세요.',
    verbose=True,
    tools=[search_internet],
    llm=local_llm,
    max_iter=3
)

judge = Agent(
    role='냉정한 인공지능 심판',
    goal='양측의 주장을 객관적으로 평가하고 승자를 판정하기',
    backstory='당신은 논리학 마스터입니다. 찬성파와 반대파의 주장을 모두 읽고, 누가 더 검색된 팩트를 논리적으로 잘 활용했는지 평가하여 승자를 가릅니다. 반드시 한국어로 대답하세요.',
    verbose=True,
    llm=local_llm
)

# 기존의 1번, 2번 태스크 하드코딩을 싹 지우고 아래처럼 바꿉니다.

rounds = 3 # 원하는 토론 라운드 수 설정 (예: 3라운드면 총 6번의 발언)
debate_tasks = []

# 🌟 For 문을 돌면서 태스크를 자동으로 생성해 리스트에 넣습니다.
for i in range(1, rounds + 1):
    pro_task = Task(
        description=f'[라운드 {i}] 상대방의 이전 주장을 논리적으로 반박하고, 필요시 도구를 사용해 새로운 찬성 근거를 대세요.',
        expected_output=f'{i}라운드 찬성파 주장',
        agent=mint_lover
    )
    con_task = Task(
        description=f'[라운드 {i}] 방금 올라온 찬성파의 주장을 읽고, 도구를 사용해 날카롭게 재반박하세요.',
        expected_output=f'{i}라운드 반대파 반박',
        agent=mint_hater
    )
    debate_tasks.extend([pro_task, con_task])

# 마지막에 심판 태스크 추가
judge_task = Task(
    description='앞선 모든 라운드의 토론을 분석하고 최종 승자를 가리세요.',
    expected_output='최종 심사평',
    agent=judge
)
debate_tasks.append(judge_task)

# Crew 결성 시 생성된 리스트(debate_tasks)를 그대로 넣습니다.
debate_club = Crew(
    agents=[mint_lover, mint_hater, judge],
    tasks=debate_tasks, 
    process=Process.sequential
)

print("=== 🌐 진정한 1:1 팩트 기반 턴제 토론 시작! ===")
result = debate_club.kickoff()

print("\n\n=== 🏆 최종 토론 결과 ===")
print(result)