import { z } from "zod";

const MOVE_MESSAGE = z.object({
    type: z.literal("move"),
    data: z.object({
        direction: z.union([z.literal(0), z.literal(1), z.literal(2), z.literal(3)])
    })
});

const MESSAGE_MESSAGE = z.object({
    type: z.literal("message"),
    data: z.object({
        text: z.string()
    })
});

const PICKUP_MESSAGE = z.object({
    type: z.literal("pickup")
});

export const MESSAGE = z.union([MOVE_MESSAGE, MESSAGE_MESSAGE, PICKUP_MESSAGE]);

export default MESSAGE;
