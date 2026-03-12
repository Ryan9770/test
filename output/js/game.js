// game.js - 게임의 핵심 로직 (게임 상태, 업데이트, 렌더링 오케스트레이션)
import { Player } from './player.js';
import { Map, TILE_TYPE } from './map.js';
import { Monster } from './monster.js';
import { UI } from './ui.js';
import {
    RENDER_TILE_SIZE, PLAYER_MOVE_SPEED, MONSTER_TYPES,
    MAP_WIDTH_TILES, MAP_HEIGHT_TILES, ORIGINAL_TILE_SIZE
} from './config.js';
import { getRandomInt, toPixelCoord, toTileCoord } from './utils.js';

export class Game {
    constructor(canvas, ctx, spritesheet) {
        this.canvas = canvas;
        this.ctx = ctx;
        this.spritesheet = spritesheet;
        this.ui = new UI();

        this.map = new Map();
        this.player = null; // init에서 생성
        this.monsters = []; // init에서 생성

        this.keysPressed = {}; // 현재 눌린 키 상태
        this.lastUpdateTime = 0;
        this.deltaTime = 0;

        this.gameOver = false;
    }

    /**
     * 게임을 초기화하고 플레이어, 몬스터를 생성합니다.
     */
    init() {
        // 플레이어 시작 위치 찾기 (길 타일 위)
        let playerStartX, playerStartY;
        let foundPlayerStart = false;
        while (!foundPlayerStart) {
            const randX = getRandomInt(0, MAP_WIDTH_TILES - 1);
            const randY = getRandomInt(0, MAP_HEIGHT_TILES - 1);
            if (this.map.getTile(randX, randY) === TILE_TYPE.PATH) {
                playerStartX = toPixelCoord(randX);
                playerStartY = toPixelCoord(randY);
                foundPlayerStart = true;
            }
        }
        this.player = new Player(playerStartX, playerStartY);
        this.player.updateStatsForLevel(); // 초기 스탯 설정

        // 몬스터 생성 (랜덤 위치, 길 타일 위)
        const monsterTypes = Object.keys(MONSTER_TYPES);
        const numMonsters = getRandomInt(5, 10); // 5~10마리 몬스터 생성
        for (let i = 0; i < numMonsters; i++) {
            let monsterX, monsterY;
            let foundMonsterPos = false;
            while (!foundMonsterPos) {
                const randX = getRandomInt(0, MAP_WIDTH_TILES - 1);
                const randY = getRandomInt(0, MAP_HEIGHT_TILES - 1);
                // 플레이어와 너무 가깝지 않고, 길 타일 위
                if (this.map.getTile(randX, randY) === TILE_TYPE.PATH &&
                    Math.abs(randX - toTileCoord(this.player.x)) > 5 &&
                    Math.abs(randY - toTileCoord(this.player.y)) > 5) {
                    monsterX = toPixelCoord(randX);
                    monsterY = toPixelCoord(randY);
                    foundMonsterPos = true;
                }
            }
            const randomMonsterType = monsterTypes[getRandomInt(0, monsterTypes.length - 1)];
            this.monsters.push(new Monster(monsterX, monsterY, randomMonsterType));
        }

        this.updateUI(); // 초기 UI 업데이트
    }

    /**
     * 게임 상태를 업데이트합니다.
     * @param {number} currentTime - 현재 게임 시간 (ms)
     */
    update(currentTime) {
        if (this.gameOver) return;

        this.deltaTime = currentTime - this.lastUpdateTime;
        this.lastUpdateTime = currentTime;

        // 플레이어 이동 처리
        let dx = 0;
        let dy = 0;
        if (this.keysPressed['w']) dy -= PLAYER_MOVE_SPEED;
        if (this.keysPressed['s']) dy += PLAYER_MOVE_SPEED;
        if (this.keysPressed['a']) dx -= PLAYER_MOVE_SPEED;
        if (this.keysPressed['d']) dx += PLAYER_MOVE_SPEED;

        if (dx !== 0 || dy !== 0) {
            this.player.move(dx, dy, this.map);
        }

        // 플레이어 공격 처리
        if (this.keysPressed[' ']) { // 스페이스바
            this.player.attack(this.monsters, currentTime);
        }

        // 몬스터 업데이트
        for (const monster of this.monsters) {
            monster.update(this.player, this.map, currentTime);
        }

        // 죽은 몬스터 처리 및 경험치 획득
        const aliveMonsters = [];
        for (const monster of this.monsters) {
            if (monster.isDead) {
                this.player.gainExp(monster.expReward);
            } else {
                aliveMonsters.push(monster);
            }
        }
        this.monsters = aliveMonsters;

        // UI 업데이트
        this.updateUI();

        // 게임 오버 조건 체크
        if (this.player.currentHp <= 0) {
            this.gameOver = true;
            console.log("Game Over! You were defeated.");
            alert("Game Over! You were defeated.");
        }
    }

    /**
     * 모든 게임 요소를 캔버스에 렌더링합니다.
     */
    render() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // 맵 렌더링
        this.map.render(this.ctx);

        // 플레이어 렌더링
        this.player.render(this.ctx, this.spritesheet);

        // 몬스터 렌더링
        for (const monster of this.monsters) {
            monster.render(this.ctx, this.spritesheet);
        }
    }

    /**
     * UI를 업데이트합니다.
     */
    updateUI() {
        this.ui.updateHP(this.player.currentHp, this.player.maxHp);
        this.ui.updateExp(this.player.exp, this.player.expToNextLevel);
        this.ui.updateLevel(this.player.level);
    }

    /**
     * 키 입력 상태를 처리합니다.
     * @param {string} key - 눌리거나 떼어진 키
     * @param {boolean} isDown - 키가 눌렸는지 (true) 떼어졌는지 (false)
     */
    handleInput(key, isDown) {
        this.keysPressed[key] = isDown;
    }
}
