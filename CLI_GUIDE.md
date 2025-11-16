# Stock CLI 사용 가이드

대화형 스트리밍 인터페이스로 주식 분석을 수행하는 도구입니다. `You > … / Assistant > …` 대화 흐름과 ANSI 색상을 통해 자연스럽게 분석을 이어갈 수 있습니다.

---

## 1. 시작하기

```bash
# 대화형 모드(기본)
python analyze_stock.py

# 영어 인터페이스 + 나스닥 벤치마크
python analyze_stock.py --lang en --benchmark QQQ
```

실행하면 대화형 프롬프트가 나타나고, 티커를 입력하면 분석이 스트리밍으로 출력됩니다. `/help`를 입력하면 언제든 사용법을 확인할 수 있고, 빈 입력(엔터)으로 종료할 수 있습니다.

---

## 2. 전역 옵션

모든 명령에서 공통으로 사용할 수 있습니다.

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--lang` | 인터페이스 언어 (ko/en), 기본 ko | `--lang en` |
| `--benchmark` | 상대 성과와 시장 모멘텀 비교에 사용할 벤치마크 | `--benchmark QQQ` |
| `--backtest` | buy&hold 백테스트 기간(일) | `--backtest 120` |

```bash
python analyze_stock.py analyze TSLA --lang en --benchmark QQQ --backtest 90
```

---

## 3. 명령어 요약

| 명령 | 설명 | 예시 |
|------|------|------|
| _(없음)_ | 대화형 모드 시작 | `python analyze_stock.py` |
| `analyze` | 지정한 종목을 즉시 분석 | `python analyze_stock.py analyze AAPL MSFT` |
| `interactive` / `i` | 명시적으로 대화형 모드 실행 | `python analyze_stock.py interactive --benchmark DIA` |
| `export` | 분석과 동시에 저장 | `python analyze_stock.py export NVDA --format json` |

### 내보내기 옵션

- `--export json|csv|mysql|postgres`
- `--json-path`, `--csv-path`
- `--mysql-*`, `--postgres-*` 접속 정보

인터랙티브 모드에서는 분석이 끝난 뒤 방향키 메뉴로 저장 형식을 선택할 수 있습니다.

---

## 4. 대화형 모드 명령어

| 입력 | 설명 |
|------|------|
| `AAPL`, `005930.KS` 등 | 해당 티커 분석 |
| `/help` | 사용법 / 단축키 안내 |
| `/quit`, `/exit` | 즉시 종료 |
| `엔터` | 종료 확인 메시지 |

### 워크플로우 예시

```bash
python analyze_stock.py --benchmark QQQ --backtest 60
You      > analyze MSFT
Assistant  > 데이터를 정리했습니다. 결과를 스트리밍할게요.
# 결과 카드 확인 후 export/다음 종목 여부 선택
```

---

## 5. 출력 섹션

분석이 끝나면 다음 카드가 순차적으로 스트리밍됩니다.

1. **시장 스냅샷** – 티커, 기준일, 종가, 핵심 신호.
2. **신호 보드 & 지표 브리핑** – MACD/RSI/SMA/거래량 요약.
3. **Scorecard** – 각 지표 value(0~1)와 weight, 가중 평균 총점(0~100) 및 등급.
4. **Probability Radar** – 상승/하락 확률과 신뢰도.
5. **Relative Performance** – 벤치마크 대비 60거래일 수익률, 알파(α), 우위/열위 라벨.
6. **Risk Overview** – 30/60일 변동성, 180일 MDD, ATR 기반 손절선, 위험 등급.
7. **Channels & S/R** – 단/중/장기 채널 요약, 지지·저항선.
8. **Backtest Snapshot** – `--backtest` 지정 시 buy&hold 수익률, 승률, 알파.

---

## 6. 분석 예시

```bash
# 기본 분석
python analyze_stock.py analyze AAPL

# 벤치마크/백테스트 지정
python analyze_stock.py analyze TSLA --benchmark QQQ --backtest 120

# 다중 종목 + JSON/CSV 저장
python analyze_stock.py analyze MSFT NVDA --export json --export csv
```

### 데이터베이스 저장

```bash
python analyze_stock.py export META --format mysql \
  --mysql-host localhost --mysql-database stocks \
  --mysql-user user --mysql-password pass
```

---

## 7. 도움말 및 팁

```bash
# 전체 도움말
python analyze_stock.py --help

# 서브커맨드 도움말
python analyze_stock.py analyze --help
python analyze_stock.py export --help
```

**팁**
1. 가장 빠른 시작: `python analyze_stock.py`
2. `/help`로 언제든 사용법 확인
3. 여러 종목을 빠르게 비교하려면 `analyze` 서브커맨드 사용
4. 벤치마크를 자주 바꾼다면 `alias`나 `shell function`으로 기본 옵션을 지정해 두세요
5. JSON/CSV/DB 내보내기는 분석 직후 또는 별도 `export` 명령으로 반복 실행 가능

---

## 8. Docker & 웹 대시보드

```bash
docker build -t stock-analyzer .
docker run --rm -p 8000:8000 -p 3000:3000 stock-analyzer
```

- 컨테이너가 FastAPI(백엔드)와 Next.js(프론트엔드)를 동시에 실행하고, 8000/3000 포트가 사용 중이면 자동으로 다음 포트를 선택합니다.
- 브라우저에서 프론트엔드 포트(예: `http://localhost:3000`)로 접속하면 웹 UI에서 티커 입력, 결과 확인, 히스토리 탐색이 가능합니다.
- `DATABASE_URL` 또는 `SQLITE_PATH` 환경 변수를 설정하면 저장소( SQLite / MySQL / PostgreSQL)를 원하는 대로 지정할 수 있습니다.

즐거운 분석 되세요! 🚀
