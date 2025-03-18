FROM alpine:latest AS builder

RUN apk add zig

WORKDIR /app

COPY game .

RUN zig build

FROM oven/bun:alpine AS runner

WORKDIR /app

COPY server/package.json package.json
COPY server/bun.lockb server/bun.lockb

RUN bun install

COPY server .

COPY --from=builder /app/zig-out/bin/game.wasm /app/game.wasm

EXPOSE 3000
CMD ["bun", "run", "start"]
