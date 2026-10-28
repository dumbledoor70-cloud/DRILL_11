# Drill #11 — AutoRun 상태

Pico2D로 만든 캐릭터 상태 실습입니다. `A` 키로 AutoRun을 시작하면 5초 동안 키 입력 없이 달리고, 달리는 동안 속도와 크기가 커집니다. 화면 좌우 끝에서는 방향을 바꿉니다. AutoRun 중 방향키를 누르면 자동 달리기를 취소하고 해당 방향의 일반 Run 상태로 전환합니다.

## 실행

프로젝트 폴더에서 다음 명령을 실행하세요.

```powershell
python main.py
```

`pico2d` Python 패키지가 필요합니다. 이미지 경로는 `main.py`의 위치를 기준으로 처리합니다.

## 조작

- `A`: Idle에서 AutoRun 시작
- `←` / `→`: 일반 Run; AutoRun 중 누르면 자동 달리기 취소
- 방향키 해제: Run에서 Idle로 복귀
- `Esc`: 종료

## 테스트

```powershell
python -m unittest discover -s tests -v
```

`PRD2.md`에서 상세 개발 명세를 확인할 수 있으며, `Drill_11_StateDiagram.png`에 상태 다이어그램이 있습니다.
