// ui.js - UI 요소 업데이트 및 렌더링 로직
import { COLOR_HP_BAR, COLOR_EXP_BAR, COLOR_TEXT } from './config.js';

export class UI {
    constructor() {
        this.hpBar = document.getElementById('hp-bar');
        this.expBar = document.getElementById('exp-bar');
        this.playerLevel = document.getElementById('player-level');
        this.hpText = document.getElementById('hp-text');
        this.expText = document.getElementById('exp-text');

        if (!this.hpBar || !this.expBar || !this.playerLevel || !this.hpText || !this.expText) {
            console.error("UI elements not found. Check index.html IDs.");
        }
    }

    /**
     * HP 바와 텍스트를 업데이트합니다.
     * @param {number} currentHp - 현재 HP
     * @param {number} maxHp - 최대 HP
     */
    updateHP(currentHp, maxHp) {
        if (this.hpBar) {
            const percentage = (currentHp / maxHp) * 100;
            this.hpBar.style.width = `${percentage}%`;
        }
        if (this.hpText) {
            this.hpText.textContent = `${Math.max(0, currentHp)}/${maxHp}`;
        }
    }

    /**
     * 경험치 바와 텍스트를 업데이트합니다.
     * @param {number} currentExp - 현재 경험치
     * @param {number} expToNextLevel - 다음 레벨업에 필요한 경험치
     */
    updateExp(currentExp, expToNextLevel) {
        if (this.expBar) {
            const percentage = (currentExp / expToNextLevel) * 100;
            this.expBar.style.width = `${percentage}%`;
        }
        if (this.expText) {
            this.expText.textContent = `${currentExp}/${expToNextLevel}`;
        }
    }

    /**
     * 플레이어 레벨을 업데이트합니다.
     * @param {number} level - 현재 레벨
     */
    updateLevel(level) {
        if (this.playerLevel) {
            this.playerLevel.textContent = level;
        }
    }
}
