# Bedrock Agent Streamlit Chat

Amazon Bedrock Agent와 연동된 실시간 스트리밍 채팅 애플리케이션입니다.

## 🚀 빠른 시작

### 1. 가상환경 생성 및 활성화

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. Agent 설정

`streaming_app.py` 파일의 18~20번째 라인에서 다음 값들을 수정하세요:

```python
AGENT_ID = "YOUR_AGENT_ID"          # 실제 Agent ID로 변경
AGENT_ALIAS_ID = "YOUR_AGENT_ALIAS_ID"  # 실제 Agent Alias ID로 변경
AWS_REGION = "us-west-2"             # 원하는 AWS 리전으로 변경
```

### 4. 애플리케이션 실행

```bash
streamlit run streaming_app.py
```