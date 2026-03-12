import requests
from bs4 import BeautifulSoup
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

local_llm = LLM(
    model="ollama/qwen2.5", # 모델은 그대로 유지!
    base_url="http://localhost:11434"
)

# 🌟 1. 도구 설명서를 아주 직관적으로 수정 (괄호 안의 사용법 추가)
@tool("Search_Internet")
def search_internet(query: str) -> str:
    """인터넷 검색 도구입니다. 
    (사용법: Action Input에 검색어 키워드만 짧게 입력하세요. 예: '오픈소스 LLM 동향')"""
    search = DuckDuckGoSearchRun()
    return search.run(query)

@tool("Read_Webpage")
def read_webpage(url: str) -> str:
    """웹페이지 본문을 읽어오는 도구입니다. 
    (사용법: Action Input에 반드시 http로 시작하는 URL 주소만 정확히 입력하세요.)"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        return text[:2000] 
    except Exception as e:
        return f"페이지 읽기 실패: {e}"

# 🌟 2. 연구원 프롬프트에 '행동 순서'를 강제로 주입
researcher = Agent(
    role='시니어 AI 트렌드 연구원',
    goal='최신 AI 기술을 검색하고 본문을 읽어 요약하기',
    backstory='''당신은 다음 순서로만 일해야 합니다:
    1. 반드시 `Search_Internet` 도구로 먼저 검색하고 검색 시에는 '최근 1개월 내 출시', '2026년 신규' 같은 구체적인 시기 키워드를 포함하세요.
    2. 검색 결과에 나온 URL 중 하나를 골라 `Read_Webpage` 도구에 넣어 본문을 읽으세요.
    3. 본문을 읽은 뒤 한국어로 요약 보고서를 작성하세요.''',
    verbose=True,
    tools=[search_internet, read_webpage],
    llm=local_llm,
    max_iter=4 # 도구를 2번 써야 하므로 시도 횟수를 조금 늘려줍니다
)

# --- 아래 writer, editor, task, crew 부분은 기존 코드와 100% 동일하게 두시면 됩니다 ---
writer = Agent(
    role='테크 전문 블로그 카피라이터',
    goal='연구원이 찾아온 팩트를 바탕으로 일반인도 읽기 쉬운 흥미로운 블로그 초안 작성하기',
    backstory='당신은 구독자 100만 명을 보유한 스타 블로거입니다. 딱딱한 기술 용어를 쉽게 풀어쓰고, 도입부에서 독자의 시선을 확 사로잡는 글쓰기에 능합니다.',
    verbose=True,
    llm=local_llm
)

editor = Agent(
    role='수석 콘텐츠 편집장 (SEO 전문가)',
    goal='블로그 초안을 검수하고 검색 엔진에 잘 노출되도록 최적화하여 최종 발행본 만들기',
    backstory='당신은 꼼꼼한 편집장이자 마케터입니다. 글의 흐름을 다듬고, 마크다운(Markdown) 문법을 활용해 소제목과 굵은 글씨를 추가하며, 맨 아래에 적절한 해시태그를 5개 이상 달아줍니다.',
    verbose=True,
    llm=local_llm
)

topic = "2026년 최신 오픈소스 LLM 동향과 활용법"

task1 = Task(
    description=f'"{topic}"에 대한 최신 뉴스와 블로그 글을 검색하세요. 가장 중요하고 흥미로운 URL에 직접 들어가 내용을 읽은 뒤, 핵심 팩트와 인사이트를 상세히 요약한 보고서를 작성하세요.',
    expected_output='검색된 링크와 팩트가 포함된 상세한 리서치 보고서',
    agent=researcher
)

task2 = Task(
    description='연구원의 리서치 보고서를 바탕으로 블로그 포스팅 초안을 작성하세요. 독자에게 말을 건네는 듯한 친근한 말투(예: ~했습니다, ~인 거 아시나요?)를 사용하세요. 분량은 중간 길이로 작성하세요.',
    expected_output='친근한 말투의 블로그 포스팅 초안',
    agent=writer
)

task3 = Task(
    description='블로그 초안을 최종 검수하세요. 1) 시선을 끄는 매력적인 제목을 맨 위에 달고, 2) 읽기 좋게 소제목(##)과 글머리 기호(-)를 배치하며, 3) 글 마지막에 #해시태그 를 추가하세요.',
    expected_output='당장 블로그에 복사/붙여넣기 할 수 있는 완벽한 마크다운 형식의 최종 게시글',
    agent=editor
)

blog_crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[task1, task2, task3],
    process=Process.sequential
)

print(f"=== 🏭 '{topic}' 주제로 블로그 자동 작성 공장을 가동합니다! ===")
final_blog_post = blog_crew.kickoff()

print("\n\n" + "="*50)
print("✨ [최종 완성된 블로그 게시글] ✨")
print("="*50)
print(final_blog_post)