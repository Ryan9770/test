// main.js - 게임의 진입점, 초기화, 메인 루프, 이벤트 리스너 관리
import { loadSpritesheet } from './assets.js';
import { Game } from './game.js';
import { CANVAS_WIDTH, CANVAS_HEIGHT } from './config.js';

const SPRITESHEET_PATH = 'assets/roguelikeChar_transparent.png';

let canvas;
let ctx;
let game;
let spritesheet;

/**
 * 게임을 초기화하고 시작합니다.
 */
async function initGame() {
    canvas = document.getElementById('gameCanvas');
    ctx = canvas.getContext('2d');

    canvas.width = CANVAS_WIDTH;
    canvas.height = CANVAS_HEIGHT;

    // 스프라이트시트 로드
    try {
        spritesheet = await loadSpritesheet(SPRITESHEET_PATH);
        console.log('Spritesheet loaded successfully.');
    } catch (error) {
        console.error('Failed to load spritesheet:', error);
        alert('스프라이트시트 로드에 실패했습니다. 게임을 시작할 수 없습니다.');
        return;
    }

    game = new Game(canvas, ctx, spritesheet);
    game.init(); // 게임 요소 초기화 (플레이어, 몬스터 등)

    // 이벤트 리스너 등록
    window.addEventListener('keydown', (e) => {
        game.handleInput(e.key.toLowerCase(), true);
        if ([' ', 'w', 'a', 's', 'd'].includes(e.key.toLowerCase())) {
            e.preventDefault(); // 게임 관련 키의 기본 동작 방지
        }
    });
    window.addEventListener('keyup', (e) => {
        game.handleInput(e.key.toLowerCase(), false);
    });

    // 게임 루프 시작
    requestAnimationFrame(gameLoop);
}

/**
 * 메인 게임 루프입니다.
 * @param {DOMHighResTimeStamp} currentTime - 현재 시간 (ms)
 */
function gameLoop(currentTime) {
    if (!game.gameOver) {
        game.update(currentTime);
        game.render();
        requestAnimationFrame(gameLoop);
    }
}

// DOMContentLoaded 이벤트 발생 시 게임 초기화
document.addEventListener('DOMContentLoaded', initGame);
