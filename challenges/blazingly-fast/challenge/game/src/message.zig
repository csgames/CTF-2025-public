const std = @import("std");

pub const Message = [64]u8;

pub const MessageQueue = extern struct {
    loop: bool = false,
    next: u8 = 0,
    messages: [COUNT]Message = undefined,

    pub const COUNT = 16;

    const Self = @This();

    pub fn init() Self {
        return Self{};
    }

    pub fn size(self: *Self) u8 {
        if (self.loop) return self.messages.len;

        return self.next;
    }

    pub fn get(self: *Self, offset: u8) ?*const Message {
        if (offset >= self.size()) return null;

        if (!self.loop) {
            return &self.messages[offset];
        }

        return &self.messages[(self.next + offset) % self.messages.len];
    }

    pub fn last(self: *Self) ?*const Message {
        if (self.size() == 0) return null;

        if (self.next == 0) return &self.messages[self.messages.len - 1];

        return &self.messages[self.next - 1];
    }

    pub fn add(self: *Self, message: []const u8) void {
        const message_len = @min(message.len, @sizeOf(Message));

        const msg = &self.messages[self.next];
        @memcpy(msg[0..message_len], message[0..message_len]);

        if (message_len < @sizeOf(Message)) msg[message_len] = '\x00';

        if (self.loop) {
            self.next = @intCast((self.next + 1) % self.messages.len);
        } else {
            self.next += 1;

            if (self.next >= self.messages.len) {
                self.loop = true;
                self.next = 0;
            }
        }
    }
};

test "Queue last" {
    // Arrange
    var queue = MessageQueue.init();
    const first_message = "First";
    const second_message = "Second";

    // Act
    queue.add(first_message);
    queue.add(second_message);

    // Assert
    const message = queue.last() orelse return error.NotFound;

    try std.testing.expectEqualSlices(u8, second_message, message[0..second_message.len]);
}

test "Queue size not full" {
    // Arrange
    var queue = MessageQueue.init();
    const message = "Message";

    // Act
    for (0..queue.messages.len / 2) |_| {
        queue.add(message);
    }

    // Assert
    try std.testing.expectEqual(queue.messages.len / 2, queue.size());
}

test "Queue size full" {
    // Arrange
    var queue = MessageQueue.init();
    const message = "Message";

    // Act
    for (0..queue.messages.len + 1) |_| {
        queue.add(message);
    }

    // Assert
    try std.testing.expectEqual(queue.messages.len, queue.size());
}

test "Queue wrapping" {
    // Arrange
    var queue = MessageQueue.init();
    const first_message = "First";
    const second_message = "Second";

    // Act
    for (0..queue.messages.len) |_| {
        queue.add(first_message);
    }

    for (0..queue.messages.len - 1) |_| {
        queue.add(second_message);
    }

    // Assert
    const first = queue.get(0) orelse return error.NotFound;
    try std.testing.expectEqualSlices(u8, first_message, first[0..first_message.len]);

    for (1..queue.messages.len) |i| {
        const message = queue.get(@intCast(i)) orelse return error.NotFound;

        try std.testing.expectEqualSlices(u8, second_message, message[0..second_message.len]);
    }
}
