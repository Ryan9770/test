import autogen
from langchain_community.tools import DuckDuckGoSearchRun

# 1. 로컬 LLM 연결 설정 (Ollama의 OpenAI 호환 API 주소를 사용합니다)
# 🌟 중요: base_url 끝에 반드시 '/v1'이 붙어야 AutoGen이 인식합니다!
config_list = [
    {
        "model": "qwen3.5:latest", # 또는 llama3.1
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama" # 로컬이라 아무 문자열이나 넣어도 됩니다
    }
]
llm_config = {"config_list": config_list, "cache_seed": None}

# 2. 검색 도구 함수 정의
def search_internet(query: str) -> str:
    """인터넷에서 최신 정보, 기사, 여론 등을 검색할 때 사용하는 도구입니다."""
    search = DuckDuckGoSearchRun()
    return search.run(query)

# 3. 에이전트(단톡방 참가자) 생성
# 3-1. 방장 (사용자를 대신해서 대화를 시작하는 역할)
user_proxy = autogen.UserProxyAgent(
    name="Admin",
    system_message="토론의 시작을 알리는 관리자입니다.",
    code_execution_config=False,
    human_input_mode="NEVER" # 사람의 개입 없이 AI끼리 자동 진행
)

# 3-2. 민트초코 찬성파
mint_lover = autogen.AssistantAgent(
    name="Mint_Pro",
    system_message="당신은 민트초코 찬성파입니다. 상대방의 의견을 반박하고 민트초코가 최고의 디저트임을 증명하세요. 필요시 'search_internet' 함수를 호출해 팩트를 가져오세요. 반드시 한국어(Korean)로 말하세요.",
    llm_config=llm_config
)

# 3-3. 민트초코 반대파
mint_hater = autogen.AssistantAgent(
    name="Mint_Con",
    system_message="당신은 민트초코 반대파입니다. 찬성파의 주장을 논리적으로 물어뜯고 치약맛일 뿐임을 증명하세요. 필요시 'search_internet' 함수를 호출해 부정적 팩트를 가져오세요. 반드시 한국어(Korean)로 말하세요.",
    llm_config=llm_config
)

# 3-4. 심판
judge = autogen.AssistantAgent(
    name="Judge",
    system_message="당신은 냉정한 심판입니다. 앞선 찬성파와 반대파의 토론을 모두 지켜본 뒤, 가장 마지막에 등장하여 누구의 논리가 더 팩트에 기반했는지 평가하고 승자를 선언하세요. 반드시 한국어(Korean)로 말하세요.",
    llm_config=llm_config
)

# 🌟 도구를 에이전트들에게 등록 (무기 쥐여주기)
autogen.agentchat.register_function(
    search_internet,
    caller=mint_lover,
    executor=user_proxy,
    name="search_internet",
    description="인터넷 검색"
)
autogen.agentchat.register_function(
    search_internet,
    caller=mint_hater,
    executor=user_proxy,
    name="search_internet",
    description="인터넷 검색"
)

# 🌟 4. 단톡방(GroupChat) 개설!
groupchat = autogen.GroupChat(
    agents=[user_proxy, mint_lover, mint_hater, judge],
    messages=[],
    max_round=6, # 최대 6번의 핑퐁(턴)이 오가면 토론 자동 종료
    speaker_selection_method="auto" # 🔥 오토젠의 핵심: 다음 발언자를 AI가 문맥을 보고 스스로 고릅니다!
)

# 단톡방 매니저 생성
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

# 5. 토론 시작! 방장이 단톡방에 첫 메시지를 던집니다.
print("=== 💬 AutoGen 단톡방 개설 완료! 토론 시작! ===")
user_proxy.initiate_chat(
    manager,
    message="지금부터 민트초코가 최고의 디저트인지에 대한 치열한 토론을 시작합니다! Mint_Pro님부터 기조연설을 시작해 주시고, 자유롭게 반박하세요. 마지막엔 Judge님이 승자를 판정해 주세요."
)