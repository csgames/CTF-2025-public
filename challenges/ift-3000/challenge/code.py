print([k:=__import__("hashlib").sha256(open(__file__,"rb").read()[:SIZE]).digest(),d:=DATA,bytes(k[i]^d[i] for i in range(len(d)))][-1])