// map.js - 맵 생성, 렌더링, 충돌 감지 로직
import {
    MAP_WIDTH_TILES, MAP_HEIGHT_TILES, RENDER_TILE_SIZE,
    COLOR_GRASS, COLOR_PATH, COLOR_WATER, COLOR_VOID
} from './config.js';
import { getRandomInt } from './utils.js';

// 타일 타입 정의
export const TILE_TYPE = {
    GRASS: 0,
    PATH: 1,
    WATER: 2,
    VOID: 3 // 맵 경계 밖
};

export class Map {
    constructor() {
        this.width = MAP_WIDTH_TILES;
        this.height = MAP_HEIGHT_TILES;
        this.tileSize = RENDER_TILE_SIZE;
        this.data = []; // 2D 배열로 맵 데이터 저장
        this.generateMap();
    }

    /**
     * 맵을 생성합니다. (풀밭, 길, 물)
     */
    generateMap() {
        // 모든 타일을 풀밭으로 초기화
        for (let y = 0; y < this.height; y++) {
            this.data[y] = [];
            for (let x = 0; x < this.width; x++) {
                this.data[y][x] = TILE_TYPE.GRASS;
            }
        }

        // 길 생성 (랜덤 워크)
        let pathX = getRandomInt(0, this.width - 1);
        let pathY = getRandomInt(0, this.height - 1);
        for (let i = 0; i < this.width * this.height * 0.5; i++) { // 맵 크기의 절반만큼 길 생성 시도
            this.data[pathY][pathX] = TILE_TYPE.PATH;

            const direction = getRandomInt(0, 3); // 0:상, 1:하, 2:좌, 3:우
            if (direction === 0) pathY--;
            else if (direction === 1) pathY++;
            else if (direction === 2) pathX--;
            else if (direction === 3) pathX++;

            pathX = clamp(pathX, 0, this.width - 1);
            pathY = clamp(pathY, 0, this.height - 1);
        }

        // 물 타일 생성 (작은 웅덩이)
        for (let i = 0; i < 5; i++) { // 5개의 웅덩이 생성 시도
            const waterStartX = getRandomInt(0, this.width - 3);
            const waterStartY = getRandomInt(0, this.height - 3);
            const waterWidth = getRandomInt(2, 4);
            const waterHeight = getRandomInt(2, 4);

            for (let y = waterStartY; y < waterStartY + waterHeight; y++) {
                for (let x = waterStartX; x < waterStartX + waterWidth; x++) {
                    if (x >= 0 && x < this.width && y >= 0 && y < this.height) {
                        this.data[y][x] = TILE_TYPE.WATER;
                    }
                }
            }
        }
    }

    /**
     * 특정 타일 좌표가 맵 경계 내에 있고 충돌 가능한지 확인합니다.
     * @param {number} tileX - 타일 x 좌표
     * @param {number} tileY - 타일 y 좌표
     * @returns {boolean} 충돌 가능 여부 (true = 충돌, false = 이동 가능)
     */
    isCollidable(tileX, tileY) {
        // 맵 경계 밖이면 충돌
        if (tileX < 0 || tileX >= this.width || tileY < 0 || tileY >= this.height) {
            return true;
        }
        // 물 타일이면 충돌
        return this.data[tileY][tileX] === TILE_TYPE.WATER;
    }

    /**
     * 맵을 캔버스에 렌더링합니다.
     * @param {CanvasRenderingContext2D} ctx - 캔버스 2D 렌더링 컨텍스트
     */
    render(ctx) {
        for (let y = 0; y < this.height; y++) {
            for (let x = 0; x < this.width; x++) {
                let color;
                switch (this.data[y][x]) {
                    case TILE_TYPE.GRASS:
                        color = COLOR_GRASS;
                        break;
                    case TILE_TYPE.PATH:
                        color = COLOR_PATH;
                        break;
                    case TILE_TYPE.WATER:
                        color = COLOR_WATER;
                        break;
                    default:
                        color = COLOR_VOID; // 알 수 없는 타일 타입
                }
                ctx.fillStyle = color;
                ctx.fillRect(x * this.tileSize, y * this.tileSize, this.tileSize, this.tileSize);
            }
        }
    }

    /**
     * 맵의 특정 타일 좌표를 반환합니다.
     * @param {number} tileX
     * @param {number} tileY
     * @returns {number} 타일 타입
     */
    getTile(tileX, tileY) {
        if (tileX < 0 || tileX >= this.width || tileY < 0 || tileY >= this.height) {
            return TILE_TYPE.VOID;
        }
        return this.data[tileY][tileX];
    }
}

function clamp(value, min, max) {
    return Math.max(min, Math.min(value, max));
}
