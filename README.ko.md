# Stock Analyzer CLI (KO)

대화형 스트리밍 UI를 갖춘 주식 분석 CLI입니다. `You > … / Assistant > …` 형태의 프롬프트와 ANSI 컬러 카드를 통해 기술적/펀더멘털 지표, 리스크, 상대 성과, 백테스트 결과를 실시간으로 확인할 수 있습니다.

---

## 목차

1. [시작하기](#시작하기)
2. [주요 기능](#주요-기능)
3. [명령어 및 옵션](#명령어-및-옵션)
4. [분석 데이터 및 계산 근거](#분석-데이터-및-계산-근거)
5. [문제 해결](#문제-해결)
6. [참고 자료](#참고-자료)

---

## 시작하기

```bash
# 대화형 모드 (기본)
python analyze_stock.py

# 영어 인터페이스 + 나스닥 벤치마크 + 90일 백테스트
python analyze_stock.py --lang en --benchmark QQQ --backtest 90
```

대화형 모드에서는 `/help`로 도움말을 확인하고, `/quit` 또는 빈 입력(엔터)으로 종료할 수 있습니다.

### Docker 배포

```bash
docker build -t stock-analyzer .
docker run --rm -p 8000:8000 -p 3000:3000 stock-analyzer
```

- 컨테이너 안에서 FastAPI(기본 8000), Next.js 프론트엔드(기본 3000)가 동시에 실행되며, 포트가 사용 중이면 자동으로 다음 포트를 선택합니다.
- `DATABASE_URL` 환경변수로 MySQL/PostgreSQL 연결을 지정하거나, 기본 SQLite 파일은 `SQLITE_PATH`로 경로를 변경할 수 있습니다.
- 브라우저에서 `http://localhost:3000`(또는 로그에 표시된 프론트엔드 포트)을 열어 웹 UI를 이용할 수 있습니다.

---

## 주요 기능

| 구분 | 설명 |
|------|------|
| 대화형 UX | `You > … / Assistant > …` 대화와 스트리밍 카드 출력 |
| 다국어 지원 | `--lang ko|en` 으로 인터페이스 전환 |
| 지표 요약 | MACD, RSI, 이동평균 배열, 채널, 거래량 스파이크, 변동성 등 |
| 스코어카드 | 각 지표를 0~1 value로 정규화 후 가중 평균, 0~100 총점과 등급 도출 |
| Probability Radar | 상승/하락 확률과 신뢰도(높음/중간/낮음) |
| 리스크/상대 성과 | 변동성·MDD·ATR·손절선, 벤치마크 대비 알파(α) |
| 간단 백테스트 | 지정 기간 buy&hold 수익률, 승률, 벤치마크 대비 알파 |
| 내보내기 | JSON, CSV, MySQL, PostgreSQL (대화형 메뉴 포함) |

---

## 명령어 및 옵션

### 최상단 명령어

| 명령 | 설명 |
|------|------|
| _(없음)_ | 대화형 모드 시작 |
| `analyze` | 지정한 티커를 즉시 분석 |
| `interactive` / `i` | 명시적으로 대화형 모드 실행 |
| `export` | 분석과 동시에 저장 수행 |

### 대표 예시

```bash
# 단일 종목 분석
python analyze_stock.py analyze AAPL

# 다중 종목 + 백테스트 120일
python analyze_stock.py analyze AAPL MSFT TSLA --backtest 120

# JSON/CSV 동시 저장
python analyze_stock.py analyze NVDA --export json --export csv

# MySQL로 내보내기
python analyze_stock.py export TSLA --format mysql \
  --mysql-host localhost --mysql-database stocks \
  --mysql-user user --mysql-password pass
```

### 전역 옵션

| 옵션 | 설명 |
|------|------|
| `--lang {ko,en}` | 인터페이스 언어 (기본: ko) |
| `--benchmark SYMBOL` | 상대 성과·시장 모멘텀 비교 벤치마크 (기본: SPY) |
| `--backtest N` | buy&hold 백테스트 기간(일) |

### 내보내기 옵션

- `--export json|csv|mysql|postgres`
- `--json-path`, `--csv-path`
- `--mysql-host`, `--mysql-port`, `--mysql-user`, `--mysql-password`, `--mysql-database`, `--mysql-table`
- `--postgres-host`, `--postgres-port`, `--postgres-user`, `--postgres-password`, `--postgres-database`, `--postgres-table`, `--postgres-schema`

---

## 분석 데이터 및 계산 근거

### 가격·거래량 기반 지표

- `yfinance`에서 1년치 일별 캔들을 수집합니다.
- **MACD / Signal / Histogram**: 12/26/9 EMA 기반 추세 모멘텀.
- **RSI(14)**: 0~100 범위를 Min-Max → 1-RSI 정규화로 value화.
- **이동평균 배열**: 5/20/60 SMA 비교를 통해 추세 value 도출.
- **거래량 스파이크**: 5일 평균 vs 30일 평균 비율을 z-score → sigmoid.
- **변동성**: 30일 수익률 표준편차 연율화 후 1 - sigmoid(z).
- **52주 고점 대비 비율**: 1 - (현재가/52주 최고가).
- **채널 & 지지/저항**: 회귀선 기반 채널, N일 고저점 기반 S/R 값.
- **ATR & 손절선**: 14일 평균실체범위로 2×ATR 손절 구간 제안.

### 펀더멘털/심리 지표

- **밸류에이션**: PER, PBR 역수 형태로 value화.
- **EPS 성장률**: 최근 2개 Net Income의 성장률 → 시그모이드 변환.
- **머니플로우**: 최근 5일 `(Close-Open)*Volume` 합계를 절대값으로 나눠 [-1,1] → (x+1)/2.
- **뉴스 감성**: 7일 내 제목·요약에서 긍/부정 키워드 빈도 계산.
- **시장 모멘텀**: 20거래일 수익률을 벤치마크와 비교, diff/0.03을 시그모이드로 변환.

### 스코어카드 파이프라인

1. **정규화** – z-score, Min-Max 등으로 지표를 공통 스케일로 변환.
2. **Value 변환** – 시그모이드/보완(1-정규화)으로 0~1 bullishness 산출.
3. **가중 평균** – IndicatorDefinition에 정의된 weight로 value를 결합.
4. **등급** – 총점이 0.8 이상이면 강력 매수, 0.6 이상 매수, 0.4 이상 중립, 그 외 매도.
5. **확률 추정** – 스코어카드를 재활용해 상승/하락 확률과 신뢰도를 계산.

### 리스크 · 상대 성과 · 백테스트

- **리스크 요약**: 30/60일 변동성, 180일 MDD, ATR, 손절선, 위험 등급.
- **Relative Performance**: 벤치마크 대비 60거래일 수익률과 알파(α).
- **Backtest Snapshot**: 지정 기간 buy&hold 수익률, 승률, 벤치마크 대비 알파.

---

## 문제 해결

| 증상 | 해결 방법 |
|------|----------|
| `ModuleNotFoundError: yfinance` | `pip install -r requirements.txt` 로 의존성 설치 |
| 데이터 다운로드 실패 | 네트워크/티커 철자 확인, 재시도 |
| MySQL/Postgres 접속 오류 | 접속 정보(`--mysql-*`, `--postgres-*`)를 다시 확인 |

로그가 필요하면 `--export json` 등으로 결과를 저장해 검토하거나, `logging` 설정을 조정할 수 있습니다.

---

## 참고 자료

- [Quickstart](QUICKSTART.md)
- [CLI Guide](CLI_GUIDE.md)
- [Feature Overview](docs/FEATURES.md)
- [Data & Metrics](docs/DATA_AND_METRICS.md)
- [Pipeline](docs/PIPELINE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Web Deployment Plan](docs/WEB_DEPLOYMENT_PLAN.md)

---

## 모니터링 & CI

- **로그**: backend/frontend/start 스크립트가 포트 선택 및 상태를 stdout으로 기록합니다. 필요 시 `LOG_LEVEL` 등을 확장해 로그 수집 파이프라인과 연계하세요.
- **헬스 체크**: FastAPI의 `GET /health` 엔드포인트를 Docker/Kubernetes readiness/liveness probe에 연결합니다.
- **메트릭 확장**: `backend/app/stock_analyzer/middleware`에 Prometheus/OTEL 미들웨어를 추가해 지표를 수집할 수 있습니다.
- **CI/CD**: `.github/workflows/ci.yml`에는 GitHub Actions 예시 파이프라인(백엔드/프론트엔드 빌드 + Docker 빌드)이 포함돼 있습니다. 레지스트리 로그인/배포 단계는 필요에 맞게 확장하세요.
회사/개인 환경에 맞춰 별칭(`alias`)을 등록하거나, `AppContext`를 확장해 커스텀 지표/내보내기 로직을 추가할 수 있습니다. 즐거운 분석 되세요! 🚀
