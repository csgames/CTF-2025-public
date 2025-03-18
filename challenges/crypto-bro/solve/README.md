# Crypto Bro

The XOR inverse is itself, so there is only 1 XOR, not 69. To solve the challenge, you can send only null bytes to the socket which will send back the flag, or send any data and then XOR it with the received message.

---

L'inverse du xor est lui-même. Les 68 premiers xor s'annule donc, ce qui laisse uniquemnt un xor. Pour résoudre le défi, il suffit d'envoyé au socket que des null bytes pour recevoir la clé. Sinon, il est aussi possible d'envoyé un message et xor le message initial avec la réponse.
