# 🚀 Stock Analyzer - Quick Reference

## 즉시 시작하기

```bash
# 기본(대화형) 모드
python analyze_stock.py

# 영어 인터페이스 + 나스닥 벤치마크
python analyze_stock.py --lang en --benchmark QQQ
```

## 대화형 모드 명령어

### 티커 분석
```
📈 티커 입력: AAPL
```

### 도움말 보기
```
📈 티커 입력: /help
```

### 종료
```
📈 티커 입력: /quit
# 또는 그냥 엔터
```

## 빠른 분석 (명령줄 모드)

```bash
# 단일 종목
python analyze_stock.py analyze AAPL

# 여러 종목
python analyze_stock.py analyze AAPL TSLA GOOGL

# 분석 후 저장 + 벤치마크 지정
python analyze_stock.py analyze AAPL --benchmark QQQ --export json

# 백테스트 120일 + CSV 저장
python analyze_stock.py analyze TSLA --backtest 120 --export csv

# 도움말
python analyze_stock.py --help
```

## 주요 기능

- ✨ **대화형 UX** – `You > … / Assistant > …` 스트리밍 출력, `/help` 즉시 안내
- 📊 **지표 요약** – MACD/RSI/채널/변동성 등 핵심 지표 카드
- 🧮 **스코어·확률·리스크** – 정규화된 스코어카드, Probability Radar, Risk Overview
- 🔁 **상대 성과·백테스트** – 벤치마크 대비 알파, 간단 buy&hold 백테스트
- 💾 **다양한 저장** – JSON, CSV, MySQL, PostgreSQL 내보내기

## 팁

1. **가장 빠른 시작**: 그냥 `python stock-analyzer` 실행
2. **도움이 필요할 때**: `/help` 입력
3. **빠른 종료**: 엔터만 누르기
4. **벤치마크 지정**: `--benchmark QQQ`
5. **백테스트 추가**: `--backtest 120`
6. **배치 분석**: `python analyze_stock.py analyze AAPL TSLA GOOGL`

---

📖 전체 가이드: [CLI_GUIDE.md](./CLI_GUIDE.md)

---

## Docker 실행 요약

```bash
docker build -t stock-analyzer .
docker run --rm -p 8000:8000 -p 3000:3000 stock-analyzer
```

- 컨테이너가 3000/8000 포트를 우선적으로 사용하며, 충돌 시 다음 포트를 자동 선택합니다.
- `DATABASE_URL`/`SQLITE_PATH` 환경변수로 저장소를 변경할 수 있고, 브라우저에서 프론트엔드 포트(기본 `http://localhost:3000`)로 접속하면 웹 대시보드를 사용할 수 있습니다.
