import fs from "node:fs/promises";

interface WasmExports {
    action_join: (ptr: number, name: number) => number,
    action_leave: (ptr: number, player: number) => boolean,
    action_message: (ptr: number, player: number, text: number) => boolean,
    action_move: (ptr: number, player: number, direction: number) => boolean,
    action_pickup: (ptr: number, player: number) => boolean,

    game_size: () => number,
    game_init: (ptr: number, seed: number) => boolean,

    player_get: (ptr: number, index: number) => number,
    player_count: (ptr: number) => number,

    world_map: (ptr: number) => number,

    message_get: (ptr: number, index: number) => number,
    message_last: (ptr: number) => number,
    message_count: (ptr: number) => number,
}

const wasmBuffer = await fs.readFile(Bun.env.GAME_WASM || "../game/zig-out/bin/game.wasm");
const wasmModule = await WebAssembly.instantiate(wasmBuffer);

const wasmMemory = wasmModule.instance.exports.memory as WebAssembly.Memory;
const wasmExports = wasmModule.instance.exports as any as WasmExports;

const tempMemoryOffset = 100_000
const tempMemory = new Uint8Array(wasmMemory.buffer, tempMemoryOffset, 1024);

type Player = [string, number, number];

const gameBaseOffset = 1024;
const gameMaxOffset = tempMemoryOffset;

const playerCount = 8;
const mapSize = 16 * 16;

export default class Game {
    private static offset: number = gameBaseOffset;
    private static size: number | null = null;

    private ptr: number;
    private buffer: Uint8Array;

    public constructor(gameId: string) {
        this.ptr = Game.offset;

        const size = Game.bufferSize();
        Game.offset += size;
        if (Game.offset > gameMaxOffset) Game.offset = gameBaseOffset;

        this.buffer = new Uint8Array(wasmMemory.buffer, this.ptr, size);

        Game.init(this.ptr, parseInt(Bun.hash(gameId)));
    }

    private static bufferSize(): number {
        if (Game.size != null) return Game.size;

        Game.size = wasmExports.game_size();

        return Game.size;
    }

    private static init(ptr: number, seed: number): void {
        wasmExports.game_init(ptr, seed);
    } 

    public getMap(): string {
        const offset = wasmExports.world_map(this.ptr) - this.ptr;

        const map = this.buffer.subarray(offset, offset + mapSize);

        return String.fromCharCode(...map);
    }

    public getPlayer(index: number): Player | null {
        const offset = wasmExports.player_get(this.ptr, index) - this.ptr;
        if (offset < 0) return null;

        let nameSize = 8;
        const name = this.buffer.subarray(offset, offset + nameSize);
        try {
            nameSize = name.indexOf(0);
        } catch(e) {} 

        const position = this.buffer.subarray(offset + 8, offset + 10);

        return [String.fromCharCode(...name.subarray(0, nameSize)), position[0], position[1]];
    }

    public getPlayerCount(): number {
        return wasmExports.player_count(this.ptr);
    }

    public getPlayers(): Player[] {
        const players: Player[] = [];
        for (let i = 0; i < playerCount; i++) {
            const player = this.getPlayer(i);

            if (player !== null) players.push(player);
        }

        return players;
    }

    public getMessageCount(): number {
        return wasmExports.message_count(this.ptr);
    }

    public getMessage(index: number): string | null {
        const offset = wasmExports.message_get(this.ptr, index) - this.ptr;
        if (offset < 0) return null;

        let textSize = 64;
        const text = this.buffer.subarray(offset, offset + 64);
        try {
            textSize = text.indexOf(0);
        } catch(e) {} 

        return String.fromCharCode(...text.subarray(0, textSize));
    }

    public getMessages(): string[] {
        const count = this.getMessageCount();

        const messages: string[] = [];
        for (let i = 0; i < count; i++) {
            messages.push(this.getMessage(i) as string);
        }

        return messages;
    }

    public getLastMessage(): string | null {
        const offset = wasmExports.message_last(this.ptr) - this.ptr;
        if (offset < 0) return null;

        let textSize = 64;
        const text = this.buffer.subarray(offset, offset + 64);
        try {
            textSize = text.indexOf(0);
        } catch(e) {} 

        return String.fromCharCode(...text.subarray(0, textSize));
    }

    public join(name: string): number | null {
        for (let i = 0; i < 8; i++) {
            const code = name.charCodeAt(i);

            if (code) tempMemory[i] = code;
            else {
                tempMemory[i] = 0;
                break;
            }
        }

        const index = wasmExports.action_join(this.ptr, tempMemoryOffset);

        if (index >= playerCount) return null;

        return index;
    }

    public leave(player: number): boolean {
        return wasmExports.action_leave(this.ptr, player);
    }

    public message(player: number, text: string): boolean {
        for (let i = 0; i < 64; i++) {
            const code = text.charCodeAt(i);

            if (code) tempMemory[i] = code;
            else {
                tempMemory[i] = 0;
                break;
            }
        }

        return wasmExports.action_message(this.ptr, player, tempMemoryOffset);
    }

    public move(player: number, direction: number): boolean {
        return wasmExports.action_move(this.ptr, player, direction);
    }

    public pickup(player: number): boolean {
        return wasmExports.action_pickup(this.ptr, player);
    }
}
