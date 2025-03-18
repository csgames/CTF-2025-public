from Crypto.Util.number import getPrime

while True:
    P = getPrime(40)
    Q = getPrime(40)
    E = 3

    if (P - 1) % E == 0 or (Q - 1) % E == 0:
        continue

    print("P:", P)
    print("Q:", Q)
    print("N:", P * Q)
    break
