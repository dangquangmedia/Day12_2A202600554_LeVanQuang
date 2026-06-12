# Day 12 Execution Roadmap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hoàn thành Day 12 theo đúng trọng tâm bài giảng, tối đa hóa điểm rubric, và tạo đủ bằng chứng nộp bài gồm code, câu trả lời mission, và public deployment.

**Architecture:** Đi từ hiểu bài và trả lời mission trước, sau đó bám pipeline production thật: `config/env -> Docker -> cloud deploy -> security -> reliability -> final integration`. Ưu tiên những hạng mục vừa là kiến thức cốt lõi của buổi học vừa xuất hiện trực tiếp trong rubric và validator cuối bài.

**Tech Stack:** FastAPI, Docker, Docker Compose, Redis, Nginx, Railway hoặc Render, Python 3.11+, curl

---

## File Map

**Read first:**
- `CODE_LAB.md` — đề bài tổng quan, checkpoint, rubric
- `DAY12_DELIVERY_CHECKLIST.md` — yêu cầu nộp bài và bằng chứng cần chuẩn bị
- `LEARNING_PATH.md` — thứ tự học đúng tinh thần buổi học
- `batch02-day12-cloud-services-and-deployment 16.31.52.pdf` — trọng tâm bài giảng
- `06-lab-complete/check_production_ready.py` — validator cuối bài

**Part-by-part lab files:**
- `01-localhost-vs-production/develop/app.py`
- `01-localhost-vs-production/production/app.py`
- `01-localhost-vs-production/production/config.py`
- `02-docker/develop/Dockerfile`
- `02-docker/production/Dockerfile`
- `02-docker/production/docker-compose.yml`
- `03-cloud-deployment/railway/railway.toml`
- `03-cloud-deployment/render/render.yaml`
- `04-api-gateway/develop/app.py`
- `04-api-gateway/production/app.py`
- `04-api-gateway/production/auth.py`
- `04-api-gateway/production/rate_limiter.py`
- `04-api-gateway/production/cost_guard.py`
- `05-scaling-reliability/develop/app.py`
- `05-scaling-reliability/production/app.py`
- `05-scaling-reliability/production/docker-compose.yml`
- `05-scaling-reliability/production/nginx.conf`
- `05-scaling-reliability/production/test_stateless.py`
- `06-lab-complete/app/main.py`
- `06-lab-complete/app/config.py`
- `06-lab-complete/Dockerfile`
- `06-lab-complete/docker-compose.yml`
- `06-lab-complete/railway.toml`
- `06-lab-complete/render.yaml`
- `06-lab-complete/.env.example`
- `06-lab-complete/.dockerignore`
- `06-lab-complete/README.md`

**Submission files to create/update:**
- `MISSION_ANSWERS.md`
- `DEPLOYMENT.md`
- `screenshots/`

## Priority Strategy

1. **Khóa điểm nền tảng trước:** Part 1 + Part 2 để hiểu đúng `env vars`, `Dockerfile`, `health check`, `compose`.
2. **Đạt deliverable tối thiểu theo bài giảng:** Dockerized app + `/health` + `X-API-Key` + public URL.
3. **Ăn điểm rubric lớn:** security, reliability, scalability trong `06-lab-complete`.
4. **Chuẩn hóa bằng chứng nộp bài:** `MISSION_ANSWERS.md`, `DEPLOYMENT.md`, screenshots, test outputs.

## Score-Weighted Focus

- `Security` + `Reliability`: 40/100 điểm, phải làm kỹ nhất.
- `Functionality` + `Docker` + `Scalability`: 50/100 điểm, là xương sống của sản phẩm.
- `Deployment`: 10/100 điểm nhưng là điều kiện để chứng minh toàn bộ bài đã chạy thật.

### Task 1: Nắm đề, rubric, deliverable

**Files:**
- Read: `CODE_LAB.md`
- Read: `DAY12_DELIVERY_CHECKLIST.md`
- Read: `LEARNING_PATH.md`
- Read: `batch02-day12-cloud-services-and-deployment 16.31.52.pdf`
- Read: `06-lab-complete/check_production_ready.py`

- [ ] **Step 1: Ghi ra mục tiêu học và tiêu chí đạt điểm**

Tóm tắt ngắn vào ghi chú cá nhân:

```text
Core lecture focus:
- Dev -> production gap
- Docker multi-stage < 500 MB
- Env vars, no hardcoded secrets
- /health and /ready
- API key authentication
- Public cloud URL

Rubric-critical extras:
- Rate limit
- Cost guard
- Graceful shutdown
- Stateless + Redis
```

- [ ] **Step 2: Tạo checklist nộp bài ngay từ đầu**

Tạo checklist làm việc:

```text
[ ] MISSION_ANSWERS.md
[ ] DEPLOYMENT.md
[ ] screenshots/
[ ] 06-lab-complete passes validator
[ ] Public URL tested
```

- [ ] **Step 3: Xác định ngưỡng hoàn thành tối thiểu và mục tiêu tối đa**

```text
Minimum pass:
- Dockerfile multi-stage
- /health
- env vars
- API key auth
- deploy Railway/Render

High-score target:
- /ready
- rate limiting
- cost guard
- graceful shutdown
- Redis stateless
- load-balancing understanding
```

### Task 2: Hoàn thành Part 1 thật chắc để tránh lỗi về sau

**Files:**
- Read: `01-localhost-vs-production/develop/app.py`
- Read: `01-localhost-vs-production/production/app.py`
- Read: `01-localhost-vs-production/production/config.py`
- Update later: `MISSION_ANSWERS.md`

- [ ] **Step 1: Tìm ít nhất 5 anti-pattern trong bản develop**

Checklist nên tìm:

```text
- Hardcoded secret/API key
- Port hardcoded
- Debug mode hardcoded
- No /health
- No graceful shutdown
- Config không đọc từ env
- Logging đơn giản hoặc thiếu
```

- [ ] **Step 2: So sánh develop vs production theo đúng bảng chấm**

Điền bảng vào `MISSION_ANSWERS.md`:

```markdown
| Feature | Basic | Advanced | Why important? |
|---------|-------|----------|----------------|
| Config | Hardcoded | Env vars | Deploy linh hoạt, không sửa code |
| Secrets | In code | In env | Tránh lộ secrets |
| Port | Fixed 8000 | Reads PORT | Tương thích Railway/Render |
| Health | Missing | GET /health | Platform biết app còn sống |
| Shutdown | Abrupt | Graceful | Không mất request khi deploy/stop |
| Logging | print | JSON | Dễ grep và quan sát trên cloud |
```

- [ ] **Step 3: Tự trả lời 4 checkpoint bằng lời của mình**

```text
- Vì sao hardcoded secrets nguy hiểm?
- Env vars giúp gì khi deploy?
- /health dùng cho liveness như thế nào?
- Graceful shutdown bảo vệ request ra sao?
```

### Task 3: Hoàn thành Part 2 và chốt kiến thức Docker

**Files:**
- Read: `02-docker/develop/Dockerfile`
- Read: `02-docker/production/Dockerfile`
- Read: `02-docker/production/docker-compose.yml`
- Update later: `MISSION_ANSWERS.md`

- [ ] **Step 1: Trả lời 4 câu hỏi Dockerfile cơ bản**

Điền vào `MISSION_ANSWERS.md`:

```markdown
1. Base image: ...
2. Working directory: ...
3. COPY requirements.txt trước để ...
4. CMD vs ENTRYPOINT: ...
```

- [ ] **Step 2: Build bản develop để hiểu luồng container**

Run:

```bash
docker build -f 02-docker/develop/Dockerfile -t my-agent:develop .
docker run -p 8000:8000 my-agent:develop
curl http://localhost:8000/ask -X POST -H "Content-Type: application/json" -d "{\"question\":\"What is Docker?\"}"
docker images my-agent:develop
```

Expected:

```text
- Container chạy được
- Endpoint trả response
- Có số liệu image size để ghi vào mission answers
```

- [ ] **Step 3: So sánh single-stage với multi-stage**

Run:

```bash
docker build -t my-agent:advanced 02-docker/production
docker images
```

Expected:

```text
- Nêu được stage builder làm gì
- Nêu được stage runtime làm gì
- Chỉ ra vì sao image nhỏ hơn
```

- [ ] **Step 4: Hiểu docker-compose và service topology**

Run:

```bash
docker compose -f 02-docker/production/docker-compose.yml up
```

Check:

```text
- Có những service nào
- Cổng nào được expose
- Request đi qua Nginx hay gọi trực tiếp app
```

### Task 4: Chọn hướng deploy sớm để tránh tắc ở cuối bài

**Files:**
- Read: `03-cloud-deployment/README.md`
- Read: `03-cloud-deployment/railway/railway.toml`
- Read: `03-cloud-deployment/render/render.yaml`
- Optional: `03-cloud-deployment/production-cloud-run/cloudbuild.yaml`
- Optional: `03-cloud-deployment/production-cloud-run/service.yaml`

- [ ] **Step 1: Chọn platform chính**

Khuyến nghị:

```text
Ưu tiên Railway nếu mục tiêu là hoàn thành lab nhanh
Ưu tiên Render nếu muốn bám infra-as-code bằng YAML
Chỉ làm Cloud Run nếu còn thời gian và muốn học thêm CI/CD
```

- [ ] **Step 2: Chuẩn bị biến môi trường cần có**

Danh sách tối thiểu:

```text
PORT
AGENT_API_KEY
REDIS_URL
LOG_LEVEL
OPENAI_API_KEY (nếu dùng LLM thật; nếu không thì mock)
```

- [ ] **Step 3: Viết trước khung `DEPLOYMENT.md`**

Tạo nội dung khung:

```markdown
# Deployment Information

## Public URL
TBD

## Platform
Railway

## Environment Variables Set
- PORT
- REDIS_URL
- AGENT_API_KEY
- LOG_LEVEL
```

### Task 5: Hoàn thành Security trước vì chiếm 20 điểm

**Files:**
- Read: `04-api-gateway/develop/app.py`
- Read: `04-api-gateway/production/app.py`
- Read: `04-api-gateway/production/auth.py`
- Read: `04-api-gateway/production/rate_limiter.py`
- Read: `04-api-gateway/production/cost_guard.py`
- Modify later: `06-lab-complete/app/main.py`
- Modify later: `06-lab-complete/app/config.py`

- [ ] **Step 1: Chốt security flow cần có trong final app**

Flow mục tiêu:

```text
Request
-> API key authentication
-> Rate limiting
-> Input validation
-> Cost guard
-> Agent response
```

- [ ] **Step 2: Chốt tiêu chí test cho security**

Run:

```bash
curl http://localhost:8000/ask -X POST -H "Content-Type: application/json" -d "{\"question\":\"Hello\"}"
curl http://localhost:8000/ask -X POST -H "X-API-Key: secret-key-123" -H "Content-Type: application/json" -d "{\"question\":\"Hello\"}"
```

Expected:

```text
- Không có key -> 401
- Có key hợp lệ -> 200
```

- [ ] **Step 3: Ưu tiên API key trước, JWT sau**

```text
Lecture deliverable chỉ yêu cầu basic authentication bằng X-API-Key.
JWT là phần advanced để hiểu thêm, không nên để chặn tiến độ final deployment.
```

- [ ] **Step 4: Đặt mục tiêu rõ cho rate limit và cost guard**

```text
Rate limit: 10 req/min per user theo rubric final project
Cost guard: $10/month per user theo CODE_LAB.md
```

### Task 6: Hoàn thành Reliability và Scalability vì đây là phần khó nhưng ăn nhiều điểm

**Files:**
- Read: `05-scaling-reliability/develop/app.py`
- Read: `05-scaling-reliability/production/app.py`
- Read: `05-scaling-reliability/production/docker-compose.yml`
- Read: `05-scaling-reliability/production/nginx.conf`
- Read: `05-scaling-reliability/production/test_stateless.py`
- Modify later: `06-lab-complete/app/main.py`
- Modify later: `06-lab-complete/docker-compose.yml`

- [ ] **Step 1: Làm rõ khác nhau giữa `/health` và `/ready`**

```text
/health = process còn sống
/ready = app đã sẵn sàng nhận traffic và dependency còn ổn
```

- [ ] **Step 2: Test flow graceful shutdown ở bản develop**

Run:

```bash
cd 05-scaling-reliability/develop
python app.py
```

Song song:

```bash
curl -X POST "http://localhost:8000/ask?question=hello"
```

Expected:

```text
- Khi nhận SIGTERM, app không rơi request đang xử lý
- /ready phải chuyển sang fail trước khi process tắt hẳn
```

- [ ] **Step 3: Ưu tiên stateless design trước load balancing**

```text
Nếu chưa đưa state sang Redis thì scale 3 instances cũng chưa đúng về mặt kiến trúc.
Redis là điều kiện để load balancer hoạt động đúng với multi-turn conversation.
```

- [ ] **Step 4: Test compose scale**

Run:

```bash
cd 05-scaling-reliability/production
docker compose up --scale agent=3
python test_stateless.py
```

Expected:

```text
- Request được xử lý qua nhiều instance
- Session/history không mất khi đổi instance
```

### Task 7: Triển khai `06-lab-complete` theo thứ tự tối ưu điểm

**Files:**
- Modify: `06-lab-complete/app/config.py`
- Modify: `06-lab-complete/app/main.py`
- Create or modify if needed: `06-lab-complete/app/auth.py`
- Create or modify if needed: `06-lab-complete/app/rate_limiter.py`
- Create or modify if needed: `06-lab-complete/app/cost_guard.py`
- Modify: `06-lab-complete/Dockerfile`
- Modify: `06-lab-complete/docker-compose.yml`
- Modify: `06-lab-complete/.env.example`
- Modify: `06-lab-complete/.dockerignore`
- Modify: `06-lab-complete/README.md`
- Modify: `06-lab-complete/railway.toml` or `06-lab-complete/render.yaml`

- [ ] **Step 1: Cố định cấu hình theo 12-factor**

Checklist:

```text
- Không hardcode secrets
- Đọc PORT từ env
- Đọc REDIS_URL từ env
- Đọc AGENT_API_KEY từ env
- Đọc RATE_LIMIT_PER_MINUTE từ env
- Đọc MONTHLY_BUDGET_USD từ env
```

- [ ] **Step 2: Làm endpoint cốt lõi trước**

Thứ tự:

```text
1. POST /ask chạy được
2. GET /health trả 200
3. GET /ready trả 200/503 đúng logic
```

- [ ] **Step 3: Gắn auth rồi mới gắn rate limit và cost guard**

```text
Không nên viết rate limit theo IP trước nếu bài yêu cầu theo user.
Nên lấy user identity từ API key hoặc body user_id rồi mới bucket quota.
```

- [ ] **Step 4: Chuyển conversation state ra Redis**

Checklist:

```text
- Không giữ history trong biến global dict
- Redis key theo user hoặc session
- Có TTL nếu bài mẫu đang dùng session history
```

- [ ] **Step 5: Hoàn thiện Dockerfile theo đúng bài giảng**

Checklist:

```text
- Multi-stage build
- Slim base image
- Non-root user
- HEALTHCHECK
- Image target < 500 MB
```

- [ ] **Step 6: Hoàn thiện Compose stack**

Checklist:

```text
- agent
- redis
- nginx hoặc route layer nếu cần
- env wiring đúng
- scale được agent
```

- [ ] **Step 7: Thêm README đủ để người khác chạy lại**

README cần có:

```text
- Prerequisites
- cp .env.example .env
- docker compose up
- curl test /health
- curl test /ask với X-API-Key
- deploy Railway/Render
```

### Task 8: Chạy validator liên tục, không để dồn cuối

**Files:**
- Run: `06-lab-complete/check_production_ready.py`

- [ ] **Step 1: Chạy validator sau mỗi cụm tính năng**

Run:

```bash
cd 06-lab-complete
python check_production_ready.py
```

Expected:

```text
- Tăng dần số check pass
- Phát hiện sớm thiếu file hoặc thiếu keyword quan trọng
```

- [ ] **Step 2: Dùng validator để chốt định nghĩa done**

```text
Done kỹ thuật = validator pass + docker chạy local + test curl thành công
Done nộp bài = thêm mission answers + deployment doc + screenshots
```

### Task 9: Làm mission answers song song với kỹ thuật

**Files:**
- Create: `MISSION_ANSWERS.md`

- [ ] **Step 1: Điền Part 1 và Part 2 ngay sau khi đọc/chạy xong**

```text
Không để dồn cuối vì dễ quên anti-patterns, image size, service topology.
```

- [ ] **Step 2: Chèn test outputs thật cho Part 4 và Part 5**

Nội dung nên có:

```markdown
## Part 4: API Security
- 401 without key
- 200 with key
- 429 after repeated requests
- giải thích cost guard

## Part 5: Scaling & Reliability
- kết quả /health
- kết quả /ready
- kết quả graceful shutdown
- kết quả stateless test
```

### Task 10: Deploy sớm, nhưng finalize muộn

**Files:**
- Modify: `06-lab-complete/railway.toml` or `06-lab-complete/render.yaml`
- Create: `DEPLOYMENT.md`
- Create: `screenshots/`

- [ ] **Step 1: Deploy bản tối thiểu sớm để kiểm tra pipeline cloud**

Minimum cloud build:

```text
- Dockerfile build được
- /health hoạt động
- /ask hoạt động với X-API-Key
```

- [ ] **Step 2: Ghi lại URL và test public commands**

Run:

```bash
curl https://your-app-domain/health
curl -X POST https://your-app-domain/ask -H "X-API-Key: YOUR_KEY" -H "Content-Type: application/json" -d "{\"user_id\":\"test\",\"question\":\"Hello\"}"
```

Expected:

```text
- Public URL trả 200
- Có bằng chứng để điền DEPLOYMENT.md
```

- [ ] **Step 3: Chụp ảnh bằng chứng**

Screenshots tối thiểu:

```text
- Dashboard deployment
- Service running / logs
- curl/Postman test thành công
```

### Task 11: Kiểm tra cuối trước khi nộp

**Files:**
- Review: `MISSION_ANSWERS.md`
- Review: `DEPLOYMENT.md`
- Review: `06-lab-complete/README.md`
- Review: `06-lab-complete/.env.example`
- Review: `.gitignore`

- [ ] **Step 1: Chạy self-test của submission checklist**

Run:

```bash
curl https://your-app-domain/health
curl https://your-app-domain/ask
curl -H "X-API-Key: YOUR_KEY" https://your-app-domain/ask -X POST -d "{\"user_id\":\"test\",\"question\":\"Hello\"}"
```

Expected:

```text
- /health -> 200
- /ask không key -> 401
- /ask có key -> 200
```

- [ ] **Step 2: Kiểm tra lỗi nộp bài phổ biến**

Checklist:

```text
- Không commit .env thật
- Không hardcode key trong code
- Public URL còn sống
- README đủ lệnh chạy
- Screenshots có trong repo
- Commit history rõ ràng
```

## Recommended Execution Order

1. Đọc `CODE_LAB.md` + `DAY12_DELIVERY_CHECKLIST.md` + validator
2. Làm Part 1 và điền ngay `MISSION_ANSWERS.md`
3. Làm Part 2 và ghi image size, compose notes
4. Chọn Railway hoặc Render
5. Làm Part 4 security trước Part 5 nếu thời gian gấp
6. Làm Part 5 reliability/scalability
7. Tích hợp vào `06-lab-complete`
8. Chạy `check_production_ready.py`
9. Deploy public URL
10. Hoàn thiện `DEPLOYMENT.md` + screenshots + final self-test

## Time Allocation

- `30-40 phút`: Part 1 + Mission answers
- `45-60 phút`: Part 2 + local Docker verification
- `20-30 phút`: Part 3 chọn platform và deploy thử sớm
- `45-60 phút`: Part 4 security
- `45-60 phút`: Part 5 reliability + stateless
- `60-90 phút`: Final integration trong `06-lab-complete`
- `20-30 phút`: viết tài liệu nộp bài và self-test

## Self-Review

- Spec coverage: kế hoạch này đã phủ toàn bộ Part 1-6, rubric 100 điểm, validator cuối bài, và 2 file nộp bài `MISSION_ANSWERS.md` + `DEPLOYMENT.md`.
- Placeholder scan: không dùng `TODO` hoặc `TBD` trong các bước thực thi; riêng `DEPLOYMENT.md` có khung tạm vì public URL chỉ có sau khi deploy.
- Type consistency: dùng nhất quán các thuật ngữ `X-API-Key`, `/health`, `/ready`, `Redis`, `Railway/Render`, `MISSION_ANSWERS.md`, `DEPLOYMENT.md`.

## Outcome Target

Khi hoàn thành đúng roadmap này, bạn nên có:

```text
- 1 repo public sạch, không lộ secrets
- 1 app production-ready ở 06-lab-complete
- 1 public URL hoạt động thật
- 1 MISSION_ANSWERS.md trả lời đầy đủ các exercise
- 1 DEPLOYMENT.md đủ lệnh test và screenshots
- Validator cuối bài pass tối đa hoặc gần tối đa
```
