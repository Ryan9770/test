// config.js - 게임 전반에 걸쳐 사용되는 상수 및 설정 값
export const ORIGINAL_TILE_SIZE = 16; // 스프라이트시트의 원본 타일 크기
export const SPRITESHEET_MARGIN = 1; // 스프라이트시트 타일 간 마진
export const STEP = ORIGINAL_TILE_SIZE + SPRITESHEET_MARGIN; // 스프라이트시트에서 한 칸 이동 단위 (17px)

export const RENDER_SCALE = 2; // 캔버스에 렌더링될 때 타일 크기 배율
export const RENDER_TILE_SIZE = ORIGINAL_TILE_SIZE * RENDER_SCALE; // 실제 캔버스에 그려지는 타일 크기

export const MAP_WIDTH_TILES = 25; // 맵 가로 타일 수 (최소 20x20)
export const MAP_HEIGHT_TILES = 25; // 맵 세로 타일 수

export const CANVAS_WIDTH = MAP_WIDTH_TILES * RENDER_TILE_SIZE;
export const CANVAS_HEIGHT = MAP_HEIGHT_TILES * RENDER_TILE_SIZE;

// 지형 색상 (Art_Director 지침 반영)
export const COLOR_GRASS = '#6B8E23'; // 올리브
export const COLOR_PATH = '#A0522D';  // 시에나
export const COLOR_WATER = '#4682B4'; // 스틸블루
export const COLOR_VOID = '#000000'; // 맵 경계 밖

// UI 색상 (Art_Director 지침 반영)
export const COLOR_HP_BAR = '#DC143C'; // 크림슨
export const COLOR_EXP_BAR = '#FFD700'; // 골드
export const COLOR_TEXT = '#FFFFFF'; // 흰색

// 스프라이트시트 좌표 (col, row)
export const SPRITE_PLAYER = { col: 0, row: 0 }; // 전사
export const SPRITE_SLIME = { col: 1, row: 10 }; // 녹색 슬라임
export const SPRITE_GOBLIN = { col: 1, row: 1 }; // 고블린
export const SPRITE_ORC = { col: 0, row: 1 }; // 오크

// 플레이어 초기 스탯 (Balance_Designer 지침 반영)
export const PLAYER_BASE_HP = 100;
export const PLAYER_BASE_ATTACK = 10;
export const PLAYER_BASE_DEFENSE = 5;
export const PLAYER_MOVE_SPEED = 4; // 픽셀 단위 이동 속도

// 레벨별 성장 곡선 (Balance_Designer 지침 반영)
export const LEVEL_STATS = [
    { level: 1, hp: 100, attack: 10, defense: 5 },
    { level: 2, hp: 115, attack: 12, defense: 6 },
    { level: 3, hp: 130, attack: 14, defense: 7 },
    { level: 4, hp: 145, attack: 16, defense: 8 },
    { level: 5, hp: 160, attack: 18, defense: 9 },
    { level: 6, hp: 175, attack: 20, defense: 10 },
    { level: 7, hp: 190, attack: 22, defense: 11 },
    { level: 8, hp: 205, attack: 24, defense: 12 },
    { level: 9, hp: 220, attack: 26, defense: 13 },
    { level: 10, hp: 235, attack: 28, defense: 14 },
];

// 레벨업 필요 경험치 (Balance_Designer 지침 반영)
export const EXP_TO_NEXT_LEVEL = [
    0,   // Level 0 (unused)
    100, // Level 1 -> 2
    200, // Level 2 -> 3
    350, // Level 3 -> 4
    550, // Level 4 -> 5
    800, // Level 5 -> 6
    1100, // Level 6 -> 7
    1450, // Level 7 -> 8
    1850, // Level 8 -> 9
    2300, // Level 9 -> 10
    999999 // Max level (or higher)
];

// 몬스터 종류별 스탯 (Balance_Designer 지침 반영)
export const MONSTER_TYPES = {
    SLIME: {
        name: "슬라임", hp: 30, attack: 5, speed: 1.5, expReward: 20, sprite: SPRITE_SLIME
    },
    GOBLIN: {
        name: "고블린", hp: 60, attack: 10, speed: 2.0, expReward: 40, sprite: SPRITE_GOBLIN
    },
    ORC: {
        name: "오크", hp: 120, attack: 20, speed: 1.5, expReward: 80, sprite: SPRITE_ORC
    }
};

export const MONSTER_CHASE_RANGE = 5 * RENDER_TILE_SIZE; // 몬스터 추격 범위 (픽셀)
export const ATTACK_RANGE = RENDER_TILE_SIZE * 1.2; // 플레이어 공격 범위 (픽셀)
export const ATTACK_COOLDOWN = 500; // 플레이어 공격 쿨다운 (ms)
