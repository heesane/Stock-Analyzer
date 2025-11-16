# 데이터 파이프라인

```text
CLI 입력 (예: You > analyze AAPL --benchmark QQQ --backtest 90)
        │
        ▼
AppContext 생성 (언어, 벤치마크, 백테스트 옵션)
        │
        ▼
analysis.analyze_ticker()
        │
        ├─ fetch_price_history() → 1년치 시세·볼륨 로딩
        ├─ indicators.*() → MACD/RSI/채널/변동성 등 계산
        ├─ scoring.build_scorecard() → 정규화 → value → 가중 평균 → 등급
        ├─ risk/relative/backtest 계산
        └─ summary dict 완성
        │
        ▼
CLI Report Renderer
        ├─ 스트리밍 카드: Market Snapshot, Signal Board, Indicators
        ├─ Relative Performance, Risk Overview, Probability, Backtest Snapshot
        ├─ Channels & Support/Resistance, Export 안내
        └─ Interactive Export Flow (JSON/CSV/DB)
```

## 단계별 설명
1. **CLI/Context**  
   - CLI는 `--benchmark`, `--backtest`, `--lang` 옵션을 전역으로 파싱해 AppContext에 저장합니다.
2. **데이터 수집**  
   - `fetch_price_history`가 yfinance에서 1년치 데이터를 받아오고, 필요 시 벤치마크도 캐시에 저장합니다.
3. **지표 계산**  
   - `indicators.py`가 MACD, RSI, 채널, 거래량, 변동성 등 핵심 지표를 산출합니다.
4. **스코어링**  
   - `scoring.py`의 IndicatorDefinition이 각 지표를 정규화 → value(0~1)로 변환 → weight 적용 후 총점을 구하고 등급을 결정합니다.
5. **요약 데이터 구성**  
   - `analyze_ticker`는 리스크 요약, 상대 성과, 백테스트 결과, 확률 추정 등을 묶어 최종 `summary` dict를 생성합니다.
6. **보고/저장**  
   - `report.py`가 카드 형태로 스트리밍 출력하고, 사용자는 JSON/CSV/DB 저장을 선택할 수 있습니다.
   - FastAPI 백엔드가 동일한 summary를 `/analyze` 응답으로 제공하며, `/history` 엔드포인트에서 최근 분석 결과를 조회할 수 있습니다.
   - Docker로 실행한 경우 Next.js 대시보드가 API를 호출해 웹 UI에서 같은 파이프라인을 시각화합니다.
