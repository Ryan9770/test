// utils.js - 공통으로 사용되는 유틸리티 함수
import { RENDER_TILE_SIZE } from './config.js';

/**
 * 값을 특정 범위 내로 제한합니다.
 * @param {number} value - 제한할 값
 * @param {number} min - 최소값
 * @param {number} max - 최대값
 * @returns {number} 제한된 값
 */
export function clamp(value, min, max) {
    return Math.max(min, Math.min(value, max));
}

/**
 * 지정된 범위 내의 무작위 정수를 생성합니다.
 * @param {number} min - 최소값 (포함)
 * @param {number} max - 최대값 (포함)
 * @returns {number} 무작위 정수
 */
export function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

/**
 * 두 점 사이의 유클리드 거리를 계산합니다.
 * @param {number} x1
 * @param {number} y1
 * @param {number} x2
 * @param {number} y2
 * @returns {number} 거리
 */
export function getDistance(x1, y1, x2, y2) {
    const dx = x2 - x1;
    const dy = y2 - y1;
    return Math.sqrt(dx * dx + dy * dy);
}

/**
 * 두 객체 간의 AABB(Axis-Aligned Bounding Box) 충돌을 감지합니다.
 * 각 객체는 x, y, width, height 속성을 가져야 합니다.
 * @param {object} obj1 - 첫 번째 객체
 * @param {object} obj2 - 두 번째 객체
 * @returns {boolean} 충돌 여부
 */
export function checkCollision(obj1, obj2) {
    return obj1.x < obj2.x + obj2.width &&
           obj1.x + obj1.width > obj2.x &&
           obj1.y < obj2.y + obj2.height &&
           obj1.y + obj1.height > obj2.y;
}

/**
 * 픽셀 좌표를 타일 좌표로 변환합니다.
 * @param {number} pixelCoord - 픽셀 좌표
 * @returns {number} 타일 좌표
 */
export function toTileCoord(pixelCoord) {
    return Math.floor(pixelCoord / RENDER_TILE_SIZE);
}

/**
 * 타일 좌표를 픽셀 좌표로 변환합니다.
 * @param {number} tileCoord - 타일 좌표
 * @returns {number} 픽셀 좌표
 */
export function toPixelCoord(tileCoord) {
    return tileCoord * RENDER_TILE_SIZE;
}
