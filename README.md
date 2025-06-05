<img width="1673" alt="airweave-lettermark" style="padding-bottom: 12px;" src="https://github.com/user-attachments/assets/e79a9af7-2e93-4888-9cf4-0f700f19fe05"/>

## Goal
- airweave는 기존 앱들의 데이터들을 한 곳에 모아 처리할 수 있도록 만드는 앱입니다.
- 기존 프로젝트의 실행 오류를 수정하고, GitHub 브랜치 생성과 같은 누락된 기능을 보완했으며, 새로운 앱으로 Discord를 추가하여 더 다양한 소스를 지원합니다.

## Requirements
### Backend
- Python 3.11 이상
- 의존성 관리는 [Poetry](https://python-poetry.org/)로 수행 (필요 패키지는  `pyproject.toml` 참고)

### Frontend
Node.js 20 이상
- React + TypeScript + Vite 기반 (필요 패키지는 `frontend/package.json` 참고)

## How to Install & Run
Docker가 설치되어 있다는 가정하에 다음 단계로 실행합니다.

### Docker image 다운로드 방법
   ```bash
   docker pull cbnucattus/final_2021040040:v1
   ```

### Docker container 생성하고 실행하는 방법
1. 컨테이너 생성
   ```bash
   docker run -dit -v /var/run/docker.sock:/var/run/docker.sock cbnucattus/final_2021040040:v1 # 호스트와 docker 공유
   docker ps | grep final_2021040040 # docker_container_ID 확인
   ```

2. 컨테이너에 접속
   ```bash
   docker exec -it <CONTAINER_ID> /bin/bash
   ```

3. repository 이동
   ```bash
   cd ~/airweave
   ```

4. 실행 스크립트 실행
   ```bash
   ./start.sh (해당 옵션 모두 n 선택)
   docker ps | grep airweave # airweave-* # container가 6개(backend, frontend, qdrant, embeddings, db, redis)생성된 것을 확인. 간혹 frontend container가 안 열릴 수 있습니다. 따로 열어주시면 됩니다.
   docker start <container_id> # 6개 컨테이너 중 일부가 시작되지 않다면 해당 컨테이너 id를 넣어서 실행
   ```

5. 실행 확인
   ```bash
   브라우저에서 `http://localhost:10240` 접속 시 프론트엔드 대시보드가 보입니다.
   만약 sources이 나오지 않는다면 backend에서 관련 데이터 처리 중이니 잠시만 기다리시면 됩니다.
   ```

6. 실행 종료(~/airweave)
   ```bash
   docker compose -f docker/docker-compose.yml down
   ```

## Usage
### Example_GitHub
1. Dashboard의 Github(또는 사용할 앱)을 선택합니다.
2. Github PAT, 데이터를 불러올 repository를 입력합니다
3. branch를 입력합니다. (없으면 생성됨)
4. create를 누르고 기다리면 github collection이 생성되는데 query를 이용해서 해당 repository 정보와 openai를 이용하여 질문을 처리할 수 있습니다.

## 디렉터리 구조
```
/
├── backend/                      # FastAPI 백엔드
│   ├── airweave/
│   │   ├── api/
│   │   │   └── v1/endpoints/     # REST API 모듈
│   │   ├── core/                 # 설정 및 공통 로직
│   │   ├── crud/                 # 데이터베이스 접근
│   │   ├── db/
│   │   ├── models/
│   │   ├── platform/
│   │   │   ├── auth/
│   │   │   ├── destinations/
│   │   │   ├── embedding_models/
│   │   │   ├── entities/
│   │   │   ├── sources/
│   │   │   ├── sync/
│   │   │   └── transformers/
│   │   └── schemas/
│   └── alembic/
│
├── frontend/                     # React + TypeScript 프론트엔드
│   ├── src/
│   │   ├── components/
│   │   ├── config/
│   │   ├── constants/
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── pages/
│   │   ├── styles/
│   │   └── types/
│   └── public/
│
├── docker/                       # docker 파일 관
│   ├── docker-compose.yml
│   ├── docker-compose.dev.yml
│   ├── docker-compose.test.yml
│   └── temporal-config/
│
├── fern/
│   ├── definition/
│   ├── docs/
│   └── scripts/
│
├── mcp/
│   └── src/
│
├── examples/
├── .github/                      # GitHub 워크플로우
│   ├── workflows/
│   └── scripts/
└── start.sh
```


## 📄 License
```
MIT License

Copyright (c) 2025 Airweave

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
