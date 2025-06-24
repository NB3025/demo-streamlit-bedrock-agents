
import streamlit as st
import boto3
import json
import uuid
from typing import Iterator

# Streamlit 페이지 설정
st.set_page_config(
    page_title="Bedrock Agent Chat",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Bedrock Agent Chat")

# Agent 설정 (코드에서 직접 설정)
AGENT_ID = "IU5CLVN58I"
AGENT_ALIAS_ID = "W7BZSIDVO5"
AWS_REGION = "us-west-2"  # 원하는 리전으로 변경

# Bedrock Agent 클라이언트 초기화
@st.cache_resource
def get_bedrock_client():
    return boto3.client('bedrock-agent-runtime', region_name=AWS_REGION)

# 스트리밍 응답 처리 함수 (수정됨)
def invoke_bedrock_agent_streaming(client, agent_id, agent_alias_id, session_id, input_text):
    try:
        response = client.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=session_id,
            inputText=input_text,
            streamingConfigurations={
                'streamFinalResponse': True
                }
        )
        
        # EventStream 처리
        event_stream = response['completion']
        
        full_response = ""
        for event in event_stream:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    chunk_text = chunk['bytes'].decode('utf-8')
                    full_response += chunk_text
                    yield chunk_text
            elif 'trace' in event:
                # trace 정보는 건너뛰기
                continue
                
        return full_response
        
    except Exception as e:
        error_msg = f"❌ 오류가 발생했습니다: {str(e)}"
        yield error_msg
        return error_msg

# 메시지 히스토리 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 세션 ID 생성 (한 번만)
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# 대화 초기화 버튼
col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    if st.button("🔄 대화 초기화"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

with col2:
    st.write(f"**Region:** {AWS_REGION}")

# 기존 메시지 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
if prompt := st.chat_input("메시지를 입력하세요..."):
    # Agent 설정 확인
    if AGENT_ID == "YOUR_AGENT_ID" or AGENT_ALIAS_ID == "YOUR_AGENT_ALIAS_ID":
        st.error("⚠️ 코드에서 AGENT_ID와 AGENT_ALIAS_ID를 실제 값으로 설정해주세요.")
        st.stop()
    
    # 사용자 메시지 추가 및 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Assistant 응답 생성
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Spinner 표시
        with st.spinner("🤖 AI 에이전트가 응답을 생성하고 있습니다..."):
            try:
                # Bedrock 클라이언트 가져오기
                bedrock_client = get_bedrock_client()
                
                # 스트리밍 응답 처리
                response_generator = invoke_bedrock_agent_streaming(
                    bedrock_client,
                    AGENT_ID,
                    AGENT_ALIAS_ID,
                    st.session_state.session_id,
                    prompt
                )
                
                # 첫 번째 청크가 올 때까지 spinner 유지
                first_chunk = True
                
                # 실시간 스트리밍 표시
                for chunk in response_generator:
                    if first_chunk:
                        # 첫 번째 청크가 오면 spinner 종료를 위해 빈 컨테이너 생성
                        first_chunk = False
                    
                    full_response += chunk
                    # 커서 효과와 함께 실시간 업데이트
                    message_placeholder.markdown(full_response + "▌")
                
                # 최종 응답 표시 (커서 제거)
                message_placeholder.markdown(full_response)
                
            except Exception as e:
                error_message = f"❌ 연결 오류: {str(e)}\n\n다음을 확인해주세요:\n- AWS 자격 증명\n- Agent ID와 Alias ID\n- 네트워크 연결"
                message_placeholder.markdown(error_message)
                full_response = error_message
    
    # Assistant 메시지 히스토리에 추가
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# 하단 정보
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.caption(f"**Session ID:** `{st.session_state.session_id[:8]}...`")

with col2:
    st.caption(f"**Messages:** {len(st.session_state.messages)}")

with col3:
    st.caption(f"**Agent:** `{AGENT_ALIAS_ID}`")
