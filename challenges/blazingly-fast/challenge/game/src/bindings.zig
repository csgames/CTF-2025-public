const std = @import("std");

const lib = @import("lib.zig");

const GAME_MESSAGE_OFFSET = 0;
const GAME_MESSAGE_SIZE = @sizeOf(lib.Message) * lib.MessageQueue.COUNT;

const GAME_WORLD_OFFSET = GAME_MESSAGE_OFFSET + GAME_MESSAGE_SIZE;
const GAME_WORLD_SIZE = @sizeOf(lib.World);

const GAME_PLAYER_OFFSET = GAME_WORLD_OFFSET + GAME_WORLD_SIZE;
const GAME_PLAYER_SIZE = @sizeOf(lib.Player) * lib.PlayerLobby.COUNT;

const GAME_DLC_SIZE = 128;

const GAME_SIZE = GAME_MESSAGE_SIZE + GAME_WORLD_SIZE + GAME_PLAYER_SIZE + GAME_DLC_SIZE;

// Game

fn game_world(game: *void) *lib.World {
    return @ptrFromInt(@intFromPtr(game) + GAME_WORLD_OFFSET);
}

fn game_messages(game: *void) *lib.MessageQueue {
    return @ptrFromInt(@intFromPtr(game) + GAME_MESSAGE_OFFSET);
}

fn game_players(game: *void) *lib.PlayerLobby {
    return @ptrFromInt(@intFromPtr(game) + GAME_PLAYER_OFFSET);
}

export fn game_size() usize {
    return GAME_SIZE;
}

export fn game_init(game: *void, seed: u32) bool {
    const world = game_world(game);
    lib.World.generate(@intCast(seed), &world.tiles);

    const messages = game_messages(game);
    messages.add("Blazingly Fast Chat");

    return true;
}

// Action

export fn action_join(game: *void, name: [*c]const u8) u8 {
    const world = game_world(game);
    const players = game_players(game);

    const name_slice: [:0]const u8 = std.mem.span(name);
    const index = lib.Action.join(name_slice, players, world) catch return std.math.maxInt(u8);

    return @intCast(index);
}

export fn action_leave(game: *void, player: u8) bool {
    if (player >= std.math.maxInt(u3)) return false;

    const players = game_players(game);

    lib.Action.leave(@intCast(player), players) catch return false;

    return true;
}

export fn action_message(game: *void, player: u8, message: [*c]const u8) bool {
    if (player >= std.math.maxInt(u3)) return false;

    const messages = game_messages(game);
    const players = game_players(game);

    const player_p = players.get_mut(@intCast(player)) orelse return false;
    const text: [:0]const u8 = std.mem.span(message);
    lib.Action.message(player_p, text, messages) catch return false;

    return true;
}

export fn action_move(game: *void, player: u8, direction: u8) bool {
    if (player >= std.math.maxInt(u3)) return false;

    const world = game_world(game);
    const players = game_players(game);

    const direction_enum: lib.Direction = @enumFromInt(direction);
    const player_p = players.get_mut(@intCast(player)) orelse return false;
    lib.Action.move(player_p, world, direction_enum) catch return false;

    return true;
}

export fn action_pickup(game: *void, player: u8) bool {
    if (player >= std.math.maxInt(u3)) return false;

    const world = game_world(game);
    const players = game_players(game);

    const player_p = players.get_mut(@intCast(player)) orelse return false;
    lib.Action.pickup(player_p, world) catch return false;

    return true;
}

// Player

export fn player_get(game: *void, index: u8) [*c]const lib.Player {
    if (index >= std.math.maxInt(u3)) return 0;

    const players = game_players(game);

    return players.get(@intCast(index)) orelse 0;
}

export fn player_count(game: *void) u8 {
    const players = game_players(game);

    return players.count();
}

// Message

export fn message_get(game: *void, offset: u8) [*c]const u8 {
    const messages = game_messages(game);

    const message = messages.get(offset) orelse return 0;

    return message;
}

export fn message_count(game: *void) u8 {
    const messages = game_messages(game);

    return messages.size();
}

export fn message_last(game: *void) [*c]const u8 {
    const messages = game_messages(game);

    const message = messages.last() orelse return 0;

    return message;
}

// World

export fn world_map(game: *void) [*c]const u8 {
    const world = game_world(game);

    return @ptrCast(&world.tiles);
}
