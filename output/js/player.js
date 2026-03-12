// player.js - 플레이어 객체 정의 및 관련 로직
import {
    RENDER_TILE_SIZE, SPRITE_PLAYER, PLAYER_BASE_HP, PLAYER_BASE_ATTACK, PLAYER_BASE_DEFENSE,
    PLAYER_MOVE_SPEED, LEVEL_STATS, EXP_TO_NEXT_LEVEL, ATTACK_RANGE, ORIGINAL_TILE_SIZE
} from './config.js';
import { drawSprite } from './assets.js';
import { clamp, getDistance, toTileCoord } from './utils.js';

export class Player {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.width = RENDER_TILE_SIZE;
        this.height = RENDER_TILE_SIZE;
        this.sprite = SPRITE_PLAYER;

        this.level = 1;
        this.exp = 0;
        this.expToNextLevel = EXP_TO_NEXT_LEVEL[this.level];

        this.maxHp = PLAYER_BASE_HP;
        this.currentHp = this.maxHp;
        this.attackPower = PLAYER_BASE_ATTACK;
        this.defense = PLAYER_BASE_DEFENSE;

        this.lastAttackTime = 0;
    }

    /**
     * 플레이어의 현재 스탯을 레벨에 맞춰 업데이트합니다.
     */
    updateStatsForLevel() {
        const stats = LEVEL_STATS.find(s => s.level === this.level);
        if (stats) {
            this.maxHp = stats.hp;
            this.attackPower = stats.attack;
            this.defense = stats.defense;
            // 현재 HP가 최대 HP보다 높으면 최대 HP로 조정
            this.currentHp = clamp(this.currentHp, 0, this.maxHp);
        }
        this.expToNextLevel = EXP_TO_NEXT_LEVEL[this.level];
    }

    /**
     * 플레이어를 이동시킵니다.
     * @param {number} dx - x축 이동량
     * @param {number} dy - y축 이동량
     * @param {Map} map - 맵 객체
     */
    move(dx, dy, map) {
        const newX = this.x + dx;
        const newY = this.y + dy;

        // 이동할 타일의 중심 좌표 계산
        const targetTileX = toTileCoord(newX + this.width / 2);
        const targetTileY = toTileCoord(newY + this.height / 2);

        // 맵 경계 및 충돌 가능한 타일 체크
        if (!map.isCollidable(targetTileX, targetTileY)) {
            this.x = newX;
            this.y = newY;
        }

        // 맵 경계에 플레이어가 완전히 벗어나지 않도록 클램프
        this.x = clamp(this.x, 0, map.width * map.tileSize - this.width);
        this.y = clamp(this.y, 0, map.height * map.tileSize - this.height);
    }

    /**
     * 몬스터에게 공격을 시도합니다.
     * @param {Array<Monster>} monsters - 현재 활성화된 몬스터 배열
     * @param {number} currentTime - 현재 게임 시간 (ms)
     * @returns {boolean} 공격 성공 여부
     */
    attack(monsters, currentTime) {
        if (currentTime - this.lastAttackTime < 500) { // 0.5초 쿨다운
            return false;
        }

        let attacked = false;
        for (const monster of monsters) {
            if (monster.currentHp <= 0) continue;

            const distance = getDistance(
                this.x + this.width / 2, this.y + this.height / 2,
                monster.x + monster.width / 2, monster.y + monster.height / 2
            );

            if (distance < ATTACK_RANGE) {
                const damage = Math.max(0, this.attackPower - monster.defense);
                monster.takeDamage(damage);
                attacked = true;
                console.log(`Player attacks ${monster.name} for ${damage} damage!`);
            }
        }

        if (attacked) {
            this.lastAttackTime = currentTime;
        }
        return attacked;
    }

    /**
     * 데미지를 입습니다.
     * @param {number} amount - 입을 데미지 양
     */
    takeDamage(amount) {
        this.currentHp -= amount;
        if (this.currentHp < 0) {
            this.currentHp = 0;
        }
        console.log(`Player takes ${amount} damage. HP: ${this.currentHp}/${this.maxHp}`);
    }

    /**
     * 경험치를 획득하고 레벨업을 확인합니다.
     * @param {number} amount - 획득할 경험치 양
     */
    gainExp(amount) {
        this.exp += amount;
        console.log(`Player gained ${amount} EXP. Current EXP: ${this.exp}/${this.expToNextLevel}`);
        if (this.exp >= this.expToNextLevel && this.level < LEVEL_STATS.length) {
            this.levelUp();
        }
    }

    /**
     * 레벨업을 처리하고 스탯을 증가시킵니다.
     */
    levelUp() {
        this.level++;
        this.exp -= this.expToNextLevel; // 남은 경험치 처리
        this.updateStatsForLevel(); // 새 레벨에 맞춰 스탯 업데이트
        this.currentHp = this.maxHp; // 레벨업 시 HP 완전 회복
        console.log(`Player Leveled Up to Level ${this.level}! HP: ${this.maxHp}, Attack: ${this.attackPower}`);
    }

    /**
     * 플레이어를 캔버스에 렌더링합니다.
     * @param {CanvasRenderingContext2D} ctx - 캔버스 2D 렌더링 컨텍스트
     * @param {HTMLImageElement} spritesheet - 스프라이트시트 이미지
     */
    render(ctx, spritesheet) {
        drawSprite(ctx, spritesheet, this.sprite, this.x, this.y, RENDER_TILE_SIZE / ORIGINAL_TILE_SIZE);
    }
}
