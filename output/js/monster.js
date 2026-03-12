// monster.js - 몬스터 객체 정의 및 관련 로직
import {
    RENDER_TILE_SIZE, ORIGINAL_TILE_SIZE, MONSTER_CHASE_RANGE, MONSTER_TYPES
} from './config.js';
import { drawSprite } from './assets.js';
import { getDistance, clamp, toTileCoord } from './utils.js';

export class Monster {
    constructor(x, y, type) {
        this.x = x;
        this.y = y;
        this.width = RENDER_TILE_SIZE;
        this.height = RENDER_TILE_SIZE;
        this.type = type;

        const monsterConfig = MONSTER_TYPES[type];
        this.name = monsterConfig.name;
        this.maxHp = monsterConfig.hp;
        this.currentHp = this.maxHp;
        this.attack = monsterConfig.attack;
        this.speed = monsterConfig.speed; // 픽셀/프레임
        this.expReward = monsterConfig.expReward;
        this.sprite = monsterConfig.sprite;
        this.defense = 0; // 몬스터는 방어력 없음 (간단화)

        this.isDead = false;
        this.lastAttackTime = 0;
        this.attackCooldown = 1000; // 몬스터 공격 쿨다운 (ms)
    }

    /**
     * 몬스터의 상태를 업데이트합니다 (AI, 이동, 공격).
     * @param {Player} player - 플레이어 객체
     * @param {Map} map - 맵 객체
     * @param {number} currentTime - 현재 게임 시간 (ms)
     */
    update(player, map, currentTime) {
        if (this.isDead) return;

        const distanceToPlayer = getDistance(
            this.x + this.width / 2, this.y + this.height / 2,
            player.x + player.width / 2, player.y + player.height / 2
        );

        // 플레이어가 추격 범위 내에 있으면 추격
        if (distanceToPlayer < MONSTER_CHASE_RANGE) {
            const angle = Math.atan2(
                (player.y + player.height / 2) - (this.y + this.height / 2),
                (player.x + player.width / 2) - (this.x + this.width / 2)
            );

            const moveX = Math.cos(angle) * this.speed;
            const moveY = Math.sin(angle) * this.speed;

            const newX = this.x + moveX;
            const newY = this.y + moveY;

            // 이동할 타일의 중심 좌표 계산
            const targetTileX = toTileCoord(newX + this.width / 2);
            const targetTileY = toTileCoord(newY + this.height / 2);

            // 맵 충돌 체크
            if (!map.isCollidable(targetTileX, targetTileY)) {
                this.x = newX;
                this.y = newY;
            }

            // 플레이어와 근접했을 때 공격
            if (distanceToPlayer < RENDER_TILE_SIZE * 0.8 && currentTime - this.lastAttackTime > this.attackCooldown) {
                const damage = Math.max(0, this.attack - player.defense);
                player.takeDamage(damage);
                this.lastAttackTime = currentTime;
                console.log(`${this.name} attacks Player for ${damage} damage!`);
            }
        }
    }

    /**
     * 데미지를 입습니다.
     * @param {number} amount - 입을 데미지 양
     */
    takeDamage(amount) {
        this.currentHp -= amount;
        if (this.currentHp <= 0) {
            this.currentHp = 0;
            this.isDead = true;
            console.log(`${this.name} is defeated!`);
        }
    }

    /**
     * 몬스터를 캔버스에 렌더링합니다.
     * @param {CanvasRenderingContext2D} ctx - 캔버스 2D 렌더링 컨텍스트
     * @param {HTMLImageElement} spritesheet - 스프라이트시트 이미지
     */
    render(ctx, spritesheet) {
        if (this.isDead) return;
        drawSprite(ctx, spritesheet, this.sprite, this.x, this.y, RENDER_TILE_SIZE / ORIGINAL_TILE_SIZE);

        // 몬스터 HP 바 (간단하게 구현)
        const barWidth = RENDER_TILE_SIZE;
        const barHeight = 3;
        const barX = this.x;
        const barY = this.y - barHeight - 2; // 몬스터 위에 표시

        ctx.fillStyle = 'red';
        ctx.fillRect(barX, barY, barWidth, barHeight);

        ctx.fillStyle = 'lime';
        const currentBarWidth = (this.currentHp / this.maxHp) * barWidth;
        ctx.fillRect(barX, barY, currentBarWidth, barHeight);
    }
}
