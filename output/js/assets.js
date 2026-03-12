// assets.js - 스프라이트시트 로딩 및 스프라이트 렌더링 헬퍼
import { ORIGINAL_TILE_SIZE, STEP, RENDER_TILE_SIZE } from './config.js';

/**
 * 스프라이트시트 이미지를 로드합니다.
 * @param {string} path - 이미지 파일 경로
 * @returns {Promise<HTMLImageElement>} 로드된 이미지 객체
 */
export function loadSpritesheet(path) {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.src = path;
        img.onload = () => resolve(img);
        img.onerror = (err) => reject(err);
    });
}

/**
 * 스프라이트시트에서 특정 타일을 잘라 캔버스에 그립니다.
 * @param {CanvasRenderingContext2D} ctx - 캔버스 2D 렌더링 컨텍스트
 * @param {HTMLImageElement} spritesheet - 로드된 스프라이트시트 이미지
 * @param {{col: number, row: number}} spriteConfig - 스프라이트시트 내 타일의 (열, 행) 좌표
 * @param {number} dx - 캔버스에 그릴 목적지 x 좌표
 * @param {number} dy - 캔버스에 그릴 목적지 y 좌표
 * @param {number} [scale=1] - 렌더링 스케일 (기본값 1)
 */
export function drawSprite(ctx, spritesheet, spriteConfig, dx, dy, scale = 1) {
    const sx = spriteConfig.col * STEP;
    const sy = spriteConfig.row * STEP;
    const drawSize = ORIGINAL_TILE_SIZE * scale;
    ctx.drawImage(spritesheet, sx, sy, ORIGINAL_TILE_SIZE, ORIGINAL_TILE_SIZE, dx, dy, drawSize, drawSize);
}
