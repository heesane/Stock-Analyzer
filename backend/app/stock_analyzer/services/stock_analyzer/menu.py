"""Interactive menu selection with arrow keys"""
from __future__ import annotations

import sys
import tty
import termios
from typing import List, Optional


def get_key() -> str:
    """Get a single keypress from the user"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        # Handle arrow keys (escape sequences)
        if ch == '\x1b':  # ESC
            ch2 = sys.stdin.read(1)
            if ch2 == '[':
                ch3 = sys.stdin.read(1)
                return f'\x1b[{ch3}'
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def select_from_menu(
    prompt: str,
    options: List[str],
    descriptions: Optional[List[str]] = None,
    lang: str = "ko",
) -> str:
    """
    Interactive menu selection with arrow keys
    
    Args:
        prompt: The prompt message to display
        options: List of option values
        descriptions: Optional list of descriptions for each option
        lang: Language code (ko or en)
    
    Returns:
        The selected option value
    """
    selected_idx = 0
    
    if descriptions is None:
        descriptions = options
    
    # 조작 안내 메시지
    instructions = {
        "ko": "  \033[1;33m↑/↓\033[0m: 이동  |  \033[1;32mEnter\033[0m: 선택  |  \033[1;31mq\033[0m: 건너뛰기",
        "en": "  \033[1;33m↑/↓\033[0m: Move  |  \033[1;32mEnter\033[0m: Select  |  \033[1;31mq\033[0m: Skip"
    }
    
    instruction_text = instructions.get(lang, instructions["ko"])
    
    # 메뉴 시작 전에 alternate screen buffer 사용
    # 이렇게 하면 메뉴가 별도 화면에서 표시되고 종료 시 원래 화면으로 복귀
    
    try:
        # Alternate screen buffer 시작
        sys.stdout.write('\033[?1049h')
        sys.stdout.flush()
        
        while True:
            # 화면 지우고 커서를 상단으로
            sys.stdout.write('\033[2J\033[H')
            
            # Display banner
            print()
            print("  ╔══════════════════════════════════════════════════════════════════════╗")
            print(f"  ║  {prompt:<66}  ║")
            print("  ╚══════════════════════════════════════════════════════════════════════╝")
            print()
            
            # Display options
            for idx, (option, desc) in enumerate(zip(options, descriptions)):
                if idx == selected_idx:
                    # Highlighted option with background
                    print(f"  \033[1;37;46m  ❯ {desc:<62}  \033[0m")
                else:
                    # Normal option
                    print(f"    \033[2m  {desc:<62}  \033[0m")
            
            print()
            print("  " + "─" * 70)
            print(instruction_text)
            print()
            
            sys.stdout.flush()
            
            # Get user input
            key = get_key()
            
            if key == '\x1b[A':  # Up arrow
                selected_idx = (selected_idx - 1) % len(options)
            elif key == '\x1b[B':  # Down arrow
                selected_idx = (selected_idx + 1) % len(options)
            elif key == '\r' or key == '\n':  # Enter
                # Alternate screen buffer 종료 (원래 화면으로 복귀)
                sys.stdout.write('\033[?1049l')
                sys.stdout.flush()
                print()
                return options[selected_idx]
            elif key.lower() == 'q':  # Quit
                # Alternate screen buffer 종료 (원래 화면으로 복귀)
                sys.stdout.write('\033[?1049l')
                sys.stdout.flush()
                print()
                return 'skip'
    except KeyboardInterrupt:
        # Ctrl+C로 종료 시 alternate screen 복귀
        sys.stdout.write('\033[?1049l')
        sys.stdout.flush()
        print()
        return 'skip'


def select_export_format(lang: str = "ko") -> str:
    """Select export format interactively"""
    options = ['json', 'csv', 'mysql', 'postgres', 'skip']
    
    descriptions_map = {
        "ko": [
            '📄 JSON        - JSON 파일로 저장하기',
            '📊 CSV         - CSV 파일로 저장하기',
            '🗄️  MySQL      - MySQL 데이터베이스에 저장하기',
            '🐘 PostgreSQL  - PostgreSQL 데이터베이스에 저장하기',
            '⏭️  건너뛰기     - 저장하지 않고 계속하기',
        ],
        "en": [
            '📄 JSON        - Save as JSON file',
            '📊 CSV         - Save as CSV file',
            '🗄️  MySQL      - Save to MySQL database',
            '🐘 PostgreSQL  - Save to PostgreSQL database',
            '⏭️  Skip       - Continue without saving',
        ]
    }
    
    prompts = {
        "ko": "💾 분석 결과를 어떻게 저장하시겠어요?",
        "en": "💾 How would you like to save the analysis results?"
    }
    
    descriptions = descriptions_map.get(lang, descriptions_map["ko"])
    prompt = prompts.get(lang, prompts["ko"])
    
    return select_from_menu(prompt, options, descriptions, lang)
